---
name: automate-test-triage
description: "Skill to automatically triage failing tests by reading the status file, fetching logs, and proposing fixes."
---

# `automate-test-triage`

> **Note to AI Agents:** Use this skill to automate the process of triaging failing tests based on a status JSON file.

## Prerequisites
* Access to the test status JSON file (local or via `fetch-nightly-results`).
* Access to `gsutil` or URL reading tools to fetch logs.

## Execution Steps

### 1. Read Test Status and Generate Report (7-Day Window)
To automate the process of reading test status and generating the consolidated report, you can run the provided Python script:
*   **Script**: `.agents/skills/automate-test-triage/scripts/triage.py`
*   **Usage**: Run `python3 .agents/skills/automate-test-triage/scripts/triage.py` from the workspace root.
*   **Output**: This will generate the report at `tmp/test-status/persistent_failures.md` within the workspace.

If you prefer to do it manually or need to customize the logic, follow these rules:
*   Fetch and read the test status JSON files for **both GA and Beta providers** for the past 7 days (including today) using the pattern in `fetch-nightly-results`.
*   Identify tests that failed in the **latest** available run for each provider.
*   For each of those tests, count how many times it failed in the 7-day window.
*   Filter the list to only include tests that failed in the latest run **and** failed at least **4 days** out of the 7 days. This helps exclude low-flakiness tests.
*   **Exclude** tests where the `error_message` contains "error 13", generic "internal error", or "Failed to perform tenant project creation" (Error code 10) without actionable details.
*   **Generate Report**: Output a markdown file containing the filtered tests. Save this file to a `tmp/test-status/` directory within the workspace (e.g., `magic-modules/tmp/test-status/persistent_failures.md`) to make it easily viewable.
    *   The file should contain a **single Summary Table** containing columns: `#` (Row Index), `Test Name`, `Provider` (Beta, GA, or Both (GA shown)), `Failures (Days)`, `GitHub Issue`, `Log Link`, and `Error Message`.
    *   **GitHub Issue Linking**: Fetch open issues from `hashicorp/terraform-provider-google` with the `test-failure` label and match the test name against issue titles (e.g., `Failing test(s): <TEST_NAME>`).
    *   If a test fails in **both** GA and Beta with the **same or similar error**, merge them into a single row, set the Provider to `Both (GA shown)`, and display the GA error message and log link.
    *   **Error Message Cleanup**: Remove Go test boilerplate like `=== RUN`, `=== PAUSE`, `=== CONT`, and `--- FAIL`.
    *   **Actual Error Extraction**: Try to locate the actual error message (e.g., starting with `Error:`, `googleapi: Error`, or `Check failed:`) to extract the clear message.
    *   **Sanitization for Comparison**: To identify "similar" errors across providers, sanitize the extracted error message before comparison by replacing dynamic parts like project IDs/resource names (`tf[-_]test[a-z0-9-_]+`), project/folder/org numbers (`(projects|folders|organizations)/\d+`, `project number: \d+`), service account numbers/names (`service-\d+@`, `[a-z0-9-]+@ci-test-project`), service account key IDs (`/keys/[a-f0-9]+`), random hex strings (e.g., `[a-z0-9]{10,20}-tp`), UUIDs (`[0-9a-f]{8}-...`), API version paths (e.g., `v1beta` vs `v1`), Help Tokens (`Help Token: ...`), Request IDs (`"requestId": ...`), Tag Values (`tagValues/\d+`), JSON metadata timestamps (`"time": ...`), Go test file line numbers (`*_test.go:\d+:`), project names (`ci-test-project-nightly-*`), and Terraform plan unchanged hidden counts (`(# of unchanged attributes/blocks/elements hidden)`) with generic placeholders.
    *   **Table Cell Formatting**: To preserve newlines and formatting within the table cell without breaking the Markdown table layout:
        *   Wrap the entire error message in `<pre>...</pre>` tags to preserve whitespace and line breaks.
        *   Replace all newlines (`\n`) with HTML break tags (`<br>`) so that the entire table row stays on a single line in the raw file (required for Markdown tables), while rendering as multi-line in the viewer.
        *   Escape any pipe characters (`|`) as `\|` to avoid breaking table columns.


### 2. Fetch Debug Log
For a selected failing test, use the `LogLink` field to get the full log.
*   **If LogLink is a URL**: Try to read it directly or convert it to a `gs://` URI.
    *   *Example URL*: `https://storage.cloud.google.com/bucket-name/path/file.txt`
    *   *GCS URI*: `gs://bucket-name/path/file.txt`
*   Use `gsutil cat` to read the log content if converted to `gs://`.

### 3. Analyze the Log
Use the `parse-debug-logs` skill to analyze the fetched log content.
*   Identify API errors, requests, and responses.
*   Correlate with the `error_message` in the status file.

### 4. Create a New Branch
Before making any code changes to implement a fix, create a new git branch.
*   **Command**: `git checkout -b fix-<test-name>-<date>`
*   Ensure you are not working directly on `main`.

### 5. Propose Fix
Based on the analysis:
*   **Example**: If the log shows "Compute Engine API has not been used in project...", propose adding `google_project_service` for `compute.googleapis.com` to the test configuration.
*   If it's a quota issue, suggest using sweepers or checking for leaked resources.
*   If it's a plan diff, suggest handling dynamic fields.

### 6. Provide Verification Command
Formulate the command for the user to run the test and validate the fix (as per `run-acctests` skill).
