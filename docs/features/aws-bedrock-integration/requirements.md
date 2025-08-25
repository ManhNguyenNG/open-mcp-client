# Requirements Document

## Introduction
This feature adds first-class support for AWS Bedrock as a Large Language Model (LLM) provider in Open MCP Client. It enables selecting Bedrock-backed models for chat and tool-use workflows while preserving current observability (LangSmith), security, and UX patterns. The integration must be configurable via environment variables and runtime configuration without exposing secrets to the browser.

References:
- Multi-provider discussion context: `https://github.com/CopilotKit/open-mcp-client/issues/18`

## Requirements

### Requirement 1: Provider selection (Bedrock) at runtime
**User Story:** As a developer, I want to select AWS Bedrock as the LLM provider, so that I can use Bedrock-hosted models transparently within the app.

#### Acceptance Criteria
1. WHEN the runtime is initialized THEN the system SHALL support choosing "bedrock" as the provider in configuration.
2. WHEN "bedrock" is selected THEN the system SHALL route LLM calls to the Bedrock client instead of OpenAI.
3. IF the provider is not specified THEN the system SHALL default to the existing provider (OpenAI) without regressions.
4. WHEN switching providers at dev time THEN the system SHALL not require a server restart beyond standard env reload.

### Requirement 2: Secure credentials and configuration
**User Story:** As a platform engineer, I want credentials to be server-side only, so that secrets are never exposed to the client.

#### Acceptance Criteria
1. WHEN Bedrock is used THEN the system SHALL read credentials exclusively from server-side environment variables.
2. IF the client requests provider info THEN the system SHALL never return raw credentials or signed headers.
3. WHEN credentials are missing or invalid THEN the system SHALL return a clear server-side error without leaking secrets.
4. WHEN deploying to different environments THEN the system SHALL allow configuring AWS profile/role via env variables.

### Requirement 3: Bedrock model configuration
**User Story:** As a developer, I want to configure the Bedrock model and region, so that my workloads run in the correct account and region.

#### Acceptance Criteria
1. WHEN provider is "bedrock" THEN the system SHALL accept `AWS_REGION` and `BEDROCK_MODEL_ID` via environment variables.
2. IF `BEDROCK_MODEL_ID` is unsupported or empty THEN the system SHALL fail fast with a descriptive error.
3. WHEN optional settings (max tokens, temperature, top_p, stop sequences) are provided THEN the system SHALL forward them to the Bedrock invocation.
4. WHEN guardrail/safety options are provided (if supported by the chosen model) THEN the system SHALL apply them consistently.

### Requirement 4: Observability and tracing (LangSmith)
**User Story:** As a developer, I want complete tracing across providers, so that I can debug and analyze performance.

#### Acceptance Criteria
1. WHEN using Bedrock THEN the system SHALL emit traces compatible with LangSmith at parity with OpenAI traces.
2. IF tracing is disabled by env THEN the system SHALL not emit provider calls while still functioning.
3. WHEN errors occur in Bedrock calls THEN the system SHALL capture error metadata in traces without leaking secrets.

### Requirement 5: Error handling and resilience
**User Story:** As a user, I want resilient behavior on throttling and timeouts, so that transient issues don’t break the session.

#### Acceptance Criteria
1. WHEN Bedrock returns throttling (rate exceeded) THEN the system SHALL implement a bounded retry with exponential backoff.
2. WHEN a request exceeds timeout THEN the system SHALL cancel the call and surface a user-friendly error.
3. IF the IAM role lacks permissions THEN the system SHALL return a clear, actionable error describing the missing permission.
4. WHEN the region is misconfigured THEN the system SHALL fail fast with guidance to set `AWS_REGION`.

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
3. WHEN configuration is incomplete THEN the system SHALL present a clear checklist of required variables and values.

### Requirement 8: Documentation
**User Story:** As a developer, I want clear setup and troubleshooting documentation, so that I can confidently enable Bedrock.

#### Acceptance Criteria
1. WHEN the feature ships THEN the system SHALL provide a setup guide for AWS credentials, region, and model IDs.
2. WHEN troubleshooting is needed THEN the system SHALL include a dedicated section for common Bedrock errors (throttling, permissions, region).
3. WHEN comparing providers THEN the documentation SHALL include a capability matrix or notes for feature parity.

## Testing Requirements

### Unit Tests
1. WHEN provider is set to "bedrock" THEN the provider selection utility SHALL return the Bedrock client.
2. IF required env vars are missing THEN initialization SHALL throw a descriptive error.
3. WHEN optional parameters are provided THEN the request payload builder SHALL include them correctly.

### Integration Tests
1. WHEN invoking a simple completion with Bedrock (mocked or sandbox) THEN the system SHALL return a well-formed response.
2. WHEN throttling is simulated THEN the retry policy SHALL cap retries and ultimately surface a clear error.
3. WHEN invalid IAM permissions are simulated THEN the system SHALL surface the correct error classification.

### End-to-End Tests
1. WHEN Bedrock is enabled in env THEN the chat flow in UI SHALL complete a basic prompt successfully.
2. WHEN switching from OpenAI to Bedrock in dev THEN the application SHALL remain functional without client-side code changes.

## Validation Requirements
1. Configuration validation SHALL confirm presence and format of `AWS_REGION` and `BEDROCK_MODEL_ID`.
2. Security validation SHALL verify no secrets are exposed to the client bundle.
3. Observability validation SHALL verify traces appear in LangSmith with provider metadata.

## Documentation Requirements
1. Update `docs/operations/setup.md` with Bedrock-specific setup and env variables.
2. Add a new `docs/features/aws-bedrock-integration/` section for this feature.
3. Update `.ai-rules/tech.md` to reflect Bedrock as a supported provider.

## Code Review Requirements
- Reviewer: Senior engineer with experience in AWS and LLM integrations.
- Review aspects: correctness, security (secrets handling, SigV4), resilience (retries/backoff), observability, and maintainability.
- Approval: Required before merging; all review comments must be addressed.
