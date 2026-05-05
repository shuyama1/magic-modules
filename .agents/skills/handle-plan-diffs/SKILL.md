---
name: handle-plan-diffs
description: "Skill to handle permanent diffs or state mismatches during test execution."
---

# `handle-plan-diffs`

> **Note to AI Agents:** Use this skill when a test fails because the plan is not empty after apply, or there is a discrepancy between expected and actual state.

## Prerequisites
* You must have the test output showing the diff (e.g., "Plan not empty", "Diff found").
* You must be in the `magic-modules` workspace.

## Execution Steps

### 1. Identify the Field
Look at the diff output to find which field is causing the permanent diff or mismatch.

### 2. Analyze the Field in Magic Modules
Find the resource definition in `mmv1/products/` and locate the field.

### 3. Propose Fix
*   **`default_from_api: true`**: If the API returns a default value that is not in the config, and it causes a diff.
*   **`DiffSuppressFunc`**: If the diff is harmless (e.g., casing, ordering) and should be ignored.
*   **Update Template**: If the test config needs to match the API default.

### 4. Verification
Provide the proposed changes to the user.
