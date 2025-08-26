# Requirements Document

## Introduction
This feature adds first-class support for AWS Bedrock as a Large Language Model (LLM) provider in Open MCP Client. It enables selecting Bedrock-backed models for chat and tool-use workflows while preserving current observability (LangSmith), security, and UX patterns. The integration must be configurable via environment variables and runtime configuration without exposing secrets to the browser.

Defaults and constraints for v1:
- Default model: `us.anthropic.claude-sonnet-4-20250514-v1:0`
- Default region: `us-east-1`
- Auth method: environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, optional `AWS_SESSION_TOKEN`)
- Provider selection: environment variables only (no UI toggle)
- Streaming: required in v1
- Retry/backoff: default bounded exponential backoff

References:
- Multi-provider discussion context: `https://github.com/CopilotKit/open-mcp-client/issues/18`

## Requirements

### Requirement 1: Provider selection (Bedrock) via environment variables
**User Story:** As a developer, I want to select AWS Bedrock as the LLM provider, so that I can use Bedrock-hosted models transparently within the app.

#### Acceptance Criteria
1. WHEN the runtime is initialized THEN the system SHALL support choosing "bedrock" as the provider using a server-side environment variable (e.g., `LLM_PROVIDER=bedrock`).
2. WHEN `LLM_PROVIDER=bedrock` is set THEN the system SHALL route LLM calls to the Bedrock client instead of OpenAI.
3. IF the provider environment variable is not specified THEN the system SHALL default to the existing provider (OpenAI) without regressions.
4. WHEN changing the provider value in environment variables THEN the system SHALL apply the change on server restart or standard env reload; no UI toggle SHALL exist in v1.

### Requirement 2: Secure credentials and configuration (env-only)
**User Story:** As a platform engineer, I want credentials to be server-side only, so that secrets are never exposed to the client.

#### Acceptance Criteria
1. WHEN Bedrock is used THEN the system SHALL read credentials exclusively from server-side environment variables: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, optional `AWS_SESSION_TOKEN`.
2. IF the client requests provider info THEN the system SHALL never return raw credentials, signed headers, or SigV4 artifacts.
3. WHEN credentials are missing or invalid THEN the system SHALL return a clear server-side error without leaking secrets (e.g., "Missing AWS_ACCESS_KEY_ID").
4. WHEN deploying to different environments THEN the system SHALL rely on env variables only for v1 (no profile/role switching via UI); infra may supply IAM role or variables out-of-band.

### Requirement 3: Bedrock model and region configuration with sane defaults
**User Story:** As a developer, I want to configure the Bedrock model and region, so that my workloads run in the correct account and region.

#### Acceptance Criteria
1. WHEN provider is "bedrock" THEN the system SHALL accept `AWS_REGION` and `BEDROCK_MODEL_ID` via environment variables.
2. IF `AWS_REGION` is not set THEN the system SHALL default to `us-east-1` and log a server-side warning.
3. IF `BEDROCK_MODEL_ID` is not set THEN the system SHALL default to `us.anthropic.claude-sonnet-4-20250514-v1:0` and log a server-side warning.
4. IF `BEDROCK_MODEL_ID` is unsupported or invalid THEN the system SHALL fail fast with a descriptive error.
5. WHEN optional settings (max tokens, temperature, top_p, stop sequences) are provided via env THEN the system SHALL forward them to the Bedrock invocation.

### Requirement 4: Observability and tracing (LangSmith)
**User Story:** As a developer, I want complete tracing across providers, so that I can debug and analyze performance.

#### Acceptance Criteria
1. WHEN using Bedrock THEN the system SHALL emit traces compatible with LangSmith at parity with OpenAI traces.
2. IF tracing is disabled by env THEN the system SHALL not emit provider calls while still functioning.
3. WHEN errors occur in Bedrock calls THEN the system SHALL capture error metadata in traces without leaking secrets.

### Requirement 5: Error handling and resilience (retry/backoff)
**User Story:** As a user, I want resilient behavior on throttling and timeouts, so that transient issues don’t break the session.

#### Acceptance Criteria
1. WHEN Bedrock returns throttling (rate exceeded) THEN the system SHALL implement a bounded retry with exponential backoff (defaults: max retries = 3; base delay = 250ms; cap = 2s; with jitter).
2. WHEN a request exceeds timeout THEN the system SHALL cancel the call and surface a user-friendly error.
3. IF the IAM role or keys lack permissions THEN the system SHALL return a clear, actionable error describing the missing permission.
4. WHEN the region is invalid (not a recognized AWS region) THEN the system SHALL fail fast with guidance to set `AWS_REGION`.

### Requirement 6: Security and compliance
**User Story:** As a security engineer, I want strict protection of secrets and PII, so that the system complies with security best practices.

#### Acceptance Criteria
1. WHEN logging Bedrock requests THEN the system SHALL redact credentials, authorization headers, and signed URLs.
2. WHEN logging prompts or tool inputs THEN the system SHALL follow existing redaction policy for sensitive fields.
3. IF the client-side attempts to access server env vars THEN the system SHALL block that access.
4. WHEN enabling Bedrock THEN the system SHALL use AWS SigV4 signing on the server only.

### Requirement 7: UX parity and configuration discoverability
**User Story:** As a user, I want a consistent experience regardless of the provider, so that switching providers does not change how I work.

#### Acceptance Criteria
1. WHEN Bedrock is selected THEN the chat and tool-use flows SHALL behave consistently with the OpenAI flow.
2. WHEN model capabilities differ (e.g., function/tool calling availability) THEN the system SHALL communicate capability limitations gracefully.
3. WHEN configuration is incomplete THEN the system SHALL present a clear checklist of required variables and values (server logs or admin docs), not a client UI.

### Requirement 8: Streaming responses (required in v1)
**User Story:** As a developer, I want streaming responses from Bedrock, so that the UI can render tokens progressively as with OpenAI.

#### Acceptance Criteria
1. WHEN provider is "bedrock" THEN the system SHALL support streaming responses to the client with parity to existing streaming behavior.
2. WHEN streaming is disabled by env THEN the system SHALL fall back to non-streaming completion without errors.
3. WHEN network interruptions occur during streaming THEN the system SHALL close the stream gracefully and surface a retriable error.

### Requirement 9: Documentation
**User Story:** As a developer, I want clear setup and troubleshooting documentation, so that I can confidently enable Bedrock.

#### Acceptance Criteria
1. WHEN the feature ships THEN the system SHALL provide a setup guide for AWS credentials, region, default model IDs, and env variables.
2. WHEN troubleshooting is needed THEN the system SHALL include a dedicated section for common Bedrock errors (throttling, permissions, region).
3. WHEN comparing providers THEN the documentation SHALL include a capability note for streaming and tool calling parity.

## Testing Requirements

### Unit Tests
1. WHEN provider is set to "bedrock" (`LLM_PROVIDER=bedrock`) THEN the provider selection utility SHALL return the Bedrock client.
2. IF required env vars are missing THEN initialization SHALL throw a descriptive error (e.g., missing credentials) or apply documented defaults (region/model) with warnings.
3. WHEN optional parameters are provided THEN the request payload builder SHALL include them correctly.
4. WHEN streaming is enabled THEN the streaming path utility SHALL be selected and send incremental chunks.

### Integration Tests
1. WHEN invoking a simple completion with Bedrock (mocked or sandbox) THEN the system SHALL return a well-formed response.
2. WHEN throttling is simulated THEN the retry policy SHALL cap retries (3) and ultimately surface a clear error.
3. WHEN invalid IAM permissions are simulated THEN the system SHALL surface the correct error classification.
4. WHEN streaming is exercised end-to-end THEN the client SHALL receive incremental tokens in order and the stream SHALL close cleanly.

### End-to-End Tests
1. WHEN Bedrock is enabled in env THEN the chat flow in UI SHALL complete a basic prompt successfully with streaming output.
2. WHEN switching from OpenAI to Bedrock in dev via env THEN the application SHALL remain functional without client-side code changes.

## Validation Requirements
1. Configuration validation SHALL confirm presence and format of `AWS_REGION` (or default to `us-east-1` with warning) and `BEDROCK_MODEL_ID` (or default to `us.anthropic.claude-sonnet-4-20250514-v1:0` with warning).
2. Security validation SHALL verify no secrets are exposed to the client bundle.
3. Observability validation SHALL verify traces appear in LangSmith with provider metadata.
4. Streaming validation SHALL verify tokenized output and correct termination conditions.

## Documentation Requirements
1. Update `docs/operations/setup.md` with Bedrock-specific setup and env variables, including defaults and examples.
2. Add a new `docs/features/aws-bedrock-integration/` section for this feature (requirements/design/tasks).
3. Update `.ai-rules/tech.md` to reflect Bedrock as a supported provider and streaming parity.

## Code Review Requirements
- Reviewer: Senior engineer with experience in AWS and LLM integrations.
- Review aspects: correctness, security (secrets handling, SigV4), resilience (retries/backoff), observability, streaming behavior, and maintainability.
- Approval: Required before merging; all review comments must be addressed.
