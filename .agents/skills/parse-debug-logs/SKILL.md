---
name: parse-debug-logs
description: "Skill to parse and analyze Terraform debug logs (TF_LOG=DEBUG) to identify API errors, requests, and responses."
---

# `parse-debug-logs`

> **Note to AI Agents:** Use this skill when you have access to a Terraform debug log (usually generated with `TF_LOG=DEBUG`) and need to identify the root cause of a test failure or apply error.

## Prerequisites
* You must have access to the log file or its content.

## Execution Steps

### 1. Identify API Requests and Responses
Search the log for HTTP requests and responses to Google Cloud APIs.
*   **Pattern**: Look for lines containing `URL: ` or `HTTP/`.
*   **JSON Payloads**: Look for `Request Body:` and `Response Body:` to see the actual data sent and received.

### 2. Search for Errors
Look for common error indicators:
*   **HTTP Status Codes**: Search for `400 Bad Request`, `403 Forbidden`, `404 Not Found`, `409 Conflict`, `429 Too Many Requests`, `500 Internal Server Error`.
*   **Error Messages**: Search for `"error"`, `"message"`, `"code"` in JSON responses.
*   **Terraform Errors**: Search for `[ERROR]` or lines starting with `Error:`.

### 3. Extract Resource IDs
To understand which resource failed, find the resource ID or name in the URL or request body.
*   **Example**: `projects/{project}/locations/{location}/...`

### 4. Analyze the Flow
*   Trace the sequence of operations (Create, Read, Update, Delete) for the failing resource to see where it deviated from expectations.
*   Check for long polling or timeout issues by looking at timestamps.

## Common Patterns to Look For
*   **Conflict (409)**: Indicates the resource or a singleton already exists or is in a state that prevents the operation.
*   **Forbidden (403)**: Missing permissions or service not enabled.
*   **Bad Request (400)**: Invalid field values or structure in the request.
