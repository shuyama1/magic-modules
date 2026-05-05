---
name: handle-quota-issues
description: "Skill to handle quota exceeded errors by identifying leaking resources and using sweepers."
---

# `handle-quota-issues`

> **Note to AI Agents:** Use this skill when a test fails due to quota limits being reached. This is often caused by resource leaks.

## Prerequisites
* You must have the error message specifying the quota limit reached.
* You must be in the `magic-modules` workspace.

## Execution Steps

### 1. Identify the Quota and Leaking Resources
*   Read the error message to identify which resource type hit the limit.
*   List the existing resources in the test project to identify which ones are leaking (i.e., dangling from previous runs).

### 2. Check the Sweeper
*   Magic Modules/Terraform provider has "sweepers" for most resources to clean up test projects.
*   Investigate why the sweeper did not clean up the leaking resources. Check if the resource is covered by a sweeper or if the sweeper failed.

### 3. Fix the Leaking Tests
*   Identify which tests created the leaking resources.
*   Analyze the test code to find why it failed to clean up (e.g., missing `Destroy` check, early exit on error, or invalid clean-up logic).
*   Propose a fix for the test in `magic-modules`.

### 4. Run the Sweeper
*   Instruct the user or use available commands to run the sweeper for the specific resource type to clean up the project.

### 5. Confirm Cleanup
*   List the resources again to confirm that the sweeper successfully removed them and quota is freed.
