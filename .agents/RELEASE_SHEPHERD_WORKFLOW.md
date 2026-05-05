# Release Shepherd Workflow for Test Failures

This document describes how the team can use the agents and skills defined in `.agents/` to address failing tests during their weekly rotation as a Release Shepherd.

## Overview of Available Skills

The skills are located in `.agents/skills/` and serve as both runbooks for humans and instructions for AI agents.

*   **[fetch-nightly-results](skills/fetch-nightly-results/SKILL.md)**: How to get the list of failing tests from GCS.
*   **[automate-test-triage](skills/automate-test-triage/SKILL.md)**: How to automatically triage failures using status files and log links.
*   **[run-acctests](skills/run-acctests/SKILL.md)**: How to execute acceptance tests in the provider repo.
*   **[parse-debug-logs](skills/parse-debug-logs/SKILL.md)**: How to analyze `TF_LOG=DEBUG` output.
*   **[handle-api-errors](skills/handle-api-errors/SKILL.md)**: Solutions for common API errors.
*   **[handle-quota-issues](skills/handle-quota-issues/SKILL.md)**: How to handle quota exceeded errors.
*   **[handle-model-not-available](skills/handle-model-not-available/SKILL.md)**: Handling regional model availability.
*   **[handle-plan-diffs](skills/handle-plan-diffs/SKILL.md)**: Resolving state mismatches.

## Enabling Agent to Run Tests
By default, the AI agent may not be able to run tests in the `terraform-provider-google` directory if it is outside the allowed workspace. To enable the agent to run tests directly:
*   **Add to Workspace**: Ensure that the provider directory is included in the active workspaces when starting the session.
*   **Approval**: The agent will still ask for permission (via a tool call that you must approve) before running any command.

## How to Use This Workflow

### Scenario A: Automated Triage with an AI Agent (Recommended)
You can ask the agent to perform the entire triage process automatically, including fetching the results.

1.  **Prompt the Agent**:
    *   *Prompt*: `"Use the 'automate-test-triage' skill to find failures, generate a summary report, and analyze them."`
2.  **Agent Action**:
    *   The agent will use `fetch-nightly-results` to download the JSON file from GCS.
    *   The agent will parse the JSON, find failing tests.
    *   **It will generate a markdown report of persistent failures (including log links) for your review.**
    *   It will extract the `LogLink`, fetch the full log (converting to `gs://` if needed).
    *   It will use `parse-debug-logs` to find the root cause.
    *   **It will create a new branch for the fix.**
    *   It will propose a fix and **propose running the test** to validate. (You can approve the command to let the agent run it, or run it manually if the workspace is restricted).

### Scenario B: Manual Triage with AI Assistance
You can delegate individual tasks to the agent.

1.  **Identify Failures**:
    *   *Prompt*: `"Use the 'fetch-nightly-results' skill to find failing tests for the beta provider."`
2.  **Reproduce**:
    *   *Prompt*: `"Help me run the test 'TestAccXYZ' using the 'run-acctests' skill."` (The agent will provide the command for you to run).
3.  **Analyze**:
    *   *Prompt*: `"I ran the test and it failed. Here are the logs: [paste logs]. Use the 'parse-debug-logs' skill to find the root cause."`

### Scenario C: You are performing the tasks manually
You can use the files in `.agents/skills/` as step-by-step guides (runbooks).

1.  Open the relevant `SKILL.md` file.
2.  Follow the **Execution Steps** listed in the file.

## Benefits
*   **Consistency**: Everyone on rotation follows the same steps.
*   **Automation**: AI agents can accelerate the process by automating searches and analysis.
*   **Documentation**: Known solutions are captured in the `handle-*` skills.
