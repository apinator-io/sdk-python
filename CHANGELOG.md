# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [1.0.0](https://github.com/apinator-io/sdk-python/releases/tag/v1.0.0) (2026-02-17)

### Added

- `Apinator` client with HMAC-authenticated API requests
- Event triggering on single or multiple channels
- Channel authentication for private and presence channels
- Webhook signature verification with timestamp freshness check
- Channel introspection (list channels, get channel info)
- Standalone `authenticate_channel` and `verify_webhook` functions
- Exception hierarchy: `RealtimeError`, `ApiError`, `AuthenticationError`, `ValidationError`
- Zero external dependencies — Python 3.10+ stdlib only
- Full test suite with pytest
