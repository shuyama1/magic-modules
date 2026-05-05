---
name: run-acctests
description: "Skill to execute acceptance tests (testacc) for a specific resource or suite in the provider."
---

# `run-acctests`

> **Note to AI Agents:** Use this skill when you need to run a test in the provider repository to verify a fix or reproduce a failure.

> [!IMPORTANT]
> In this specific environment, the agent cannot execute this skill directly because the provider repository is outside the allowed workspace. You must provide the command to the USER and ask them to run it.

## Prerequisites
* You must know the specific service path (e.g., `./google-beta/services/ces`) and test name (e.g., `TestAccCESDeployment_cesDeploymentBasicExample`).
* The test must be run in the provider directory. The agent should identify this path by:
  1. Checking the active workspaces in the conversation metadata for a path ending in `terraform-provider-google`.
  2. If not found, asking the user for the path.

## Execution Steps

### 1. Formulate the Command
Construct the command to run the test with `TF_LOG=DEBUG` and output to a log file.

```bash
TF_LOG=DEBUG make testacc TEST=./google-beta/services/<SERVICE_NAME> TESTARGS='-run=<TEST_NAME>$' > test_output.log
```

### 2. Instruct the User
Present the command to the user and ask them to run it in the provider directory.

### 3. Verification
Ask the user to share the output or the `test_output.log` file content if the test fails, so we can use the `parse-debug-logs` skill (to be created) to analyze it.
