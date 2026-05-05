---
name: handle-model-not-available
description: "Skill to handle errors where a specific model is not available in a region for a service."
---

# `handle-model-not-available`

> **Note to AI Agents:** Use this skill when a test fails with an error message indicating that a model (like `gemini-1.5-flash`) is not available in a specific region (like `us`).

## Prerequisites
* You must have a specific error message indicating model unavailability.
* You must be in the `magic-modules` workspace.

## Execution Steps

### 1. Locate the Usage
Search for the failing model name in the `magic-modules` directory to find which templates or configurations are using it.

```bash
grep -r "model_name" mmv1/templates/terraform/examples/
```

### 2. Analyze Product Context
Identify the product (e.g., `ces`, `vertexai`) and check if other tests for the same product use different models or regions.

### 3. Propose Fallbacks
* If another model is used in an update step or a similar test (e.g., `gemini-2.0-flash`), propose switching to that model.
* If no fallback is obvious, recommend contacting the service team to verify model availability for that specific API in that region.

### 4. Verification
Do NOT assume a fix works without verification. Since tests cannot be run directly by the agent in some environments, provide the proposed diff to the user and ask them to run the specific test command.
