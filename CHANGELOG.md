# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [1.1.0](https://github.com/apinator-io/sdk-python/compare/v1.0.0...v1.1.0) (2026-10-25)


### Features

* verify webhooks with the endpoint's webhook secret ([#3](https://github.com/apinator-io/sdk-python/issues/3)) ([b742d7c](https://github.com/apinator-io/sdk-python/commit/b742d7ce763d267dbe10abbdca2f38767516292c))


### Bug Fixes

* send an Apinator User-Agent so Cloudflare doesn't block requests ([#5](https://github.com/apinator-io/sdk-python/issues/5)) ([e1fe956](https://github.com/apinator-io/sdk-python/commit/e1fe956cb5c217c67931dd59b715fcd85e25ccb1))
* tests ([d6b3759](https://github.com/apinator-io/sdk-python/commit/d6b3759290799ce8c072bf48a8673cf621ba78c9))


### Documentation

* document cache channels ([a33322e](https://github.com/apinator-io/sdk-python/commit/a33322e924d65e843c3eaeb763431fe95cc7753b))
* document cache channels ([1f28fc4](https://github.com/apinator-io/sdk-python/commit/1f28fc46c12bcb3fdc0c4a4dd2a184dbf884d803))
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
