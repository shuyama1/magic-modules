---
name: fetch-nightly-results
description: "Skill to fetch the latest nightly test results for Beta or GA providers from GCS."
---

# `fetch-nightly-results`

> **Note to AI Agents:** Use this skill to get the list of failing tests from the nightly runs.

## Prerequisites
* You must have `gsutil` installed and configured with access to the `gs://nightly-test-data` bucket.
* You must be in the `magic-modules` workspace.

## Execution Steps

### 1. Determine the Target File
Construct the GCS URI based on the provider version and date.
*   **Format**: `gs://nightly-test-data/test-metadata/{version}/{date}-{version}.json`
*   **Example**: `gs://nightly-test-data/test-metadata/beta/2026-05-04-beta.json`
*   Note: If no date is specified, assume yesterday's date.

### 2. Fetch Content
Run the following command to read the file content:

```bash
gsutil cat gs://nightly-test-data/test-metadata/{version}/{date}-{version}.json
```

### 3. Parse and Filter
The output is a JSON array of test objects. Filter for objects where:
*   `"status": "FAILURE"`

### 4. Report
List the failing tests, focusing on the `name`, `service`, and the `error_message` snippet.
