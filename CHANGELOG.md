# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## 0.1.0 (2026-08-11)


### Bug Fixes

* tests ([d6b3759](https://github.com/apinator-io/sdk-python/commit/d6b3759290799ce8c072bf48a8673cf621ba78c9))


### Documentation

* update texts ([8a922e1](https://github.com/apinator-io/sdk-python/commit/8a922e10b8bccd6a4883595adefcb8e7757e4239))

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
