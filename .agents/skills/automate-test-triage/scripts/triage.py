import datetime
import json
import os
import re
import subprocess
from collections import defaultdict

def get_date_str(days_ago):
    today = datetime.date.today()
    target_date = today - datetime.timedelta(days=days_ago)
    return target_date.strftime("%Y-%m-%d")

def fetch_results(date_str, provider_type):
    uri = f"gs://nightly-test-data/test-metadata/{provider_type}/{date_str}-{provider_type}.json"
    print(f"Fetching {uri}...")
    result = subprocess.run(["gsutil", "cat", uri], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Failed to fetch {uri}")
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON for {uri}: {e}")
        return None

def is_generic_error(error_msg):
    if not error_msg:
        return True
    error_msg_lower = error_msg.lower()
    if "error 13" in error_msg_lower:
        return True
    if "internal error" in error_msg_lower:
        return True
    if "failed to perform tenant project creation" in error_msg_lower:
        return True
    return False

def get_failures(provider_type):
    failure_counts = defaultdict(int)
    latest_failures = {} # Store name -> {error: msg, log: link}
    latest_available_date = None

    # Check past 7 days (including today)
    for i in range(7):
        date_str = get_date_str(i)
        data = fetch_results(date_str, provider_type)
        if data:
            if latest_available_date is None:
                latest_available_date = date_str
                # Record failures in the latest available run
                for item in data:
                    if item.get("status") == "FAILURE":
                        error_msg = item.get("error_message", "")
                        log_link = item.get("log_link") or item.get("LogLink", "")
                        if not is_generic_error(error_msg):
                            latest_failures[item.get("name")] = {
                                "error": error_msg,
                                "log": log_link
                            }

            # Count failures across all days
            for item in data:
                if item.get("status") == "FAILURE":
                    failure_counts[item.get("name")] += 1
                    
    return latest_failures, failure_counts, latest_available_date

def get_actual_error(error_str):
    full_clean_error = "\n".join([line for line in error_str.split('\n') if not (line.startswith("=== RUN") or line.startswith("=== PAUSE") or line.startswith("=== CONT") or line.startswith("--- FAIL:") or line.strip() == "FAIL")]).strip()
    
    error_keywords = ["Error:", "googleapi: Error", "Check failed:"]
    actual_error = full_clean_error
    for kw in error_keywords:
        idx = full_clean_error.find(kw)
        if idx != -1:
            actual_error = full_clean_error[idx:]
            break
    return actual_error

def sanitize_for_comparison(error_str):
    # Replace project IDs and resource names like tf-test... or tf_test...
    s = re.sub(r'tf[-_]test[a-z0-9-_]+', 'tf-test-ID', error_str)
    # Replace ci-test-project-nightly-beta/ga
    s = re.sub(r'ci-test-project-nightly-[a-z]+', 'ci-test-project', s)
    # Replace project numbers like projects/12345678
    s = re.sub(r'projects/\d+', 'projects/NUMBER', s)
    # Replace project numbers in messages like project number: 123456
    s = re.sub(r'project number: \d+', 'project number: NUMBER', s)
    # Replace folder and organization numbers like folders/123456
    s = re.sub(r'(folders|organizations)/\d+', r'\g<1>/NUMBER', s)
    # Replace random numbers in subject or violations
    s = re.sub(r'project:\d+', 'project:NUMBER', s)
    # Replace service account project numbers like service-123456@
    s = re.sub(r'service-\d+@', 'service-NUMBER@', s)
    # Replace custom service account names before @ci-test-project...
    s = re.sub(r'[a-z0-9-]+@ci-test-project', 'sa@ci-test-project', s)
    # Replace service account key IDs
    s = re.sub(r'/keys/[a-f0-9]+', '/keys/KEY_ID', s)
    # Replace random hex strings ending in -tp (common in Apigee tests)
    s = re.sub(r'[a-z0-9]{10,20}-tp', 'RANDOM-tp', s)
    # Replace UUIDs
    s = re.sub(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', 'UUID', s)
    # Normalize v1beta vs v1 in Google API URLs
    s = re.sub(r'googleapis\.com/v1beta/', 'googleapis.com/v1/', s)
    # Replace resource array indices like [0]
    s = re.sub(r'\[\d+\]', '[X]', s)
    # Replace Help Tokens
    s = re.sub(r'Help Token: [a-zA-Z0-9_-]+', 'Help Token: TOKEN', s)
    # Replace Request IDs
    s = re.sub(r'"requestId":\s*"[a-f0-9]+"', '"requestId": "ID"', s)
    # Replace tag values
    s = re.sub(r'tagValues/\d+', 'tagValues/NUMBER', s)
    # Replace timestamps in JSON metadata like "time":"2026-05-13T04:20:17.485043Z"
    s = re.sub(r'"time":\s*"\d{4}-\d{2}-\d{2}T[0-9:.]+Z"', '"time": "TIMESTAMP"', s)
    # Replace Go test file line numbers
    s = re.sub(r'[a-zA-Z0-9_]+_test\.go:\d+:', 'test.go:LINE:', s)
    # Replace terraform plan unchanged hidden counts
    s = re.sub(r'\(\d+ unchanged (attributes|blocks|elements) hidden\)', r'(X unchanged \g<1> hidden)', s)
    return s

def find_issue_link(test_name, issues):
    exact_target = f"Failing test(s): {test_name}"
    for issue in issues:
        title = issue.get("title", "").strip()
        if title == exact_target:
            return f"[#{issue['number']}]({issue['url']})"
            
    # Try wildcard/substring matching e.g. "Failing test(s): TestAccAccessContextManager*"
    for issue in issues:
        title = issue.get("title", "").strip()
        if title.startswith("Failing test(s): "):
            pattern = title.replace("Failing test(s): ", "").strip()
            if pattern.endswith("*"):
                prefix = pattern[:-1]
                if test_name.startswith(prefix):
                    return f"[#{issue['number']}]({issue['url']})"
            elif test_name in title or pattern in test_name:
                return f"[#{issue['number']}]({issue['url']})"
                
    return "N/A"

def main():
    beta_failures, beta_counts, beta_date = get_failures("beta")
    ga_failures, ga_counts, ga_date = get_failures("ga")

    # Combine failures
    all_failures = defaultdict(dict)
    
    count_threshold = 4
    
    for name, details in beta_failures.items():
        count = beta_counts[name]
        if count >= count_threshold:
            if name not in all_failures:
                all_failures[name] = {}
            all_failures[name]["Beta"] = {
                "count": count,
                "error": details["error"],
                "log": details["log"]
            }
            
    for name, details in ga_failures.items():
        count = ga_counts[name]
        if count >= count_threshold:
            if name not in all_failures:
                all_failures[name] = {}
            all_failures[name]["GA"] = {
                "count": count,
                "error": details["error"],
                "log": details["log"]
            }

    # Fetch GitHub issues
    issues = []
    print("Fetching open test-failure issues from GitHub...")
    gh_res = subprocess.run(["gh", "issue", "list", "--repo", "hashicorp/terraform-provider-google", "--label", "test-failure", "--state", "open", "--limit", "1000", "--json", "number,title,url"], capture_output=True, text=True)
    if gh_res.returncode == 0:
        try:
            issues = json.loads(gh_res.stdout)
        except Exception as e:
            print(f"Failed to parse gh issue list JSON: {e}")
    else:
        print(f"Failed to fetch GitHub issues: {gh_res.stderr}")

    output_file = "tmp/test-status/persistent_failures.md"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, "w") as f:
        f.write("# Persistent Test Failures (Past 7 Days)\n\n")
        f.write(f"Criteria: Failed in latest run and at least 4 days in past 7 days, excluding generic errors.\n\n")
        
        if beta_date:
            f.write(f"**Latest Beta run**: {beta_date}\n")
        if ga_date:
            f.write(f"**Latest GA run**: {ga_date}\n")
        f.write("\n")
        
        f.write("| # | Test Name | Provider | Failures (Days) | GitHub Issue | Log Link | Error Message |\n")
        f.write("| --- | --- | --- | --- | --- | --- | --- |\n")
        
        row_idx = 1
        for name in sorted(all_failures.keys()):
            providers = all_failures[name]
            issue_link = find_issue_link(name, issues)
            
            if "Beta" in providers and "GA" in providers:
                beta_details = providers["Beta"]
                ga_details = providers["GA"]
                
                beta_error = get_actual_error(beta_details["error"])
                ga_error = get_actual_error(ga_details["error"])
                
                beta_sanitized = sanitize_for_comparison(beta_error)
                ga_sanitized = sanitize_for_comparison(ga_error)
                
                if beta_sanitized == ga_sanitized:
                    # Similar error in both! Show GA and be explicit!
                    table_error = ga_error.replace("|", "\\|").replace("\n", "<br>")
                    table_error = f"<pre>{table_error}</pre>"
                    log_display = f"[Log]({ga_details['log']})" if ga_details['log'] else "N/A"
                    
                    f.write(f"| {row_idx} | {name} | Both (GA shown) | {ga_details['count']} | {issue_link} | {log_display} | {table_error} |\n")
                    row_idx += 1
                    continue # Skip to next test!
            
            # If not similar or only one provider failed, show them normally
            for prov in ["Beta", "GA"]:
                if prov in providers:
                    details = providers[prov]
                    actual_error = get_actual_error(details["error"])
                    
                    table_error = actual_error.replace("|", "\\|").replace("\n", "<br>")
                    table_error = f"<pre>{table_error}</pre>"
                    
                    log_display = f"[Log]({details['log']})" if details["log"] else "N/A"
                    
                    f.write(f"| {row_idx} | {name} | {prov} | {details['count']} | {issue_link} | {log_display} | {table_error} |\n")
                    row_idx += 1

    print(f"\nResults written to {output_file}")

if __name__ == "__main__":
    main()
