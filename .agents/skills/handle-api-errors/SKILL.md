---
name: handle-api-errors
description: "Skill to handle errors returned by the Google Cloud API during test execution."
---

# `handle-api-errors`

> **Note to AI Agents:** Use this skill when a test fails with a direct error from the Google Cloud API (e.g., status codes 400, 403, 409, etc.).

## Prerequisites
* You must have the exact error message from the test output.
* You must be in the `magic-modules` workspace.

## Execution Steps

### 1. Identify the Error Type
Look at the error message to determine the category:

#### A. Model Availability Issues (e.g., "model X is not available in region Y")
1. **Locate the Usage**: Search for the model name in `magic-modules` to find which templates are using it.
2. **Analyze Product Context**: Check if other tests for the same product use different models or regions.
3. **Propose Fallbacks**: Suggest switching to a model known to work (like `gemini-2.0-flash` or `gemini-3.0-flash-001` for CES) or recommend contacting the service team.

#### B. Permission Denied / IAM Issues (e.g., "Error 403: ... does not have permission")
1. **Check Service Account**: Identify which service account is being used (e.g., `gcp-sa-ces`).
2. **Verify Roles**: Check if the test configuration includes `google_project_iam_member` or similar resources to grant roles.
3. **Propose Fix**: Suggest adding the missing IAM role or ensuring the service account has access to the resource.

#### C. Resource Already Exists / Conflict (e.g., "Error 409: ... already exists")
1. **Check Naming**: Ensure the test resource uses a random suffix or unique ID.
2. **Dangling Resources**: This often indicates a previous test failed to clean up. Suggest checking the project for the existing resource.

### 2. Verification
Provide the proposed diff to the user and ask them to run the specific test command to verify the fix.
