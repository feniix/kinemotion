# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!-- version list -->

## kinemotion-v0.66.5 (2025-12-19)

### Refactor

- remove redundant CalledProcessError from exception tuple

## kinemotion-v0.66.4 (2025-12-19)

### Refactor

- reduce cognitive complexity in debug_overlay_utils and cmj api

## kinemotion-v0.66.3 (2025-12-19)

### Fix

- remove duplicate 'message' parameter in _log call

## kinemotion-v0.66.2 (2025-12-19)

### Fix

- **codecs**: remove Fly.io references, document actual Cloud Run architecture

## kinemotion-v0.66.1 (2025-12-19)

### Fix

- **warnings**: remove redundant 'h264' codec, use standard 'avc1' only

## kinemotion-v0.66.0 (2025-12-19)

### Feat

- **ap3d**: add validation infrastructure, methodology documentation, and data tracking setup

### Fix

- **logging**: make structured logging compatible with standard logging
- suppress Pyright reportCallIssue warnings in debug_overlay_utils
- remove VP9 codec for iOS compatibility and add structured logging

## kinemotion-v0.65.0 (2025-12-18)

### Feat

- **ap3d**: add AthletePose3D validation scripts and setup guide

## kinemotion-v0.64.0 (2025-12-15)

### Feat

- **backend**: add structlog type annotations and remove unnecessary casts
- **types**: add MediaPipe Pose type stubs for improved IDE support
- enable genuine pyright strict mode with comprehensive type infrastructure

### Fix

- update user_id field types from UUID to str for email-based identifiers
- update database schema to use email as user identifier
- update analysis API endpoints to use email as user identifier

## kinemotion-v0.63.0 (2025-12-15)

### Feat

- use email as unique identifier for users and storage organization

### Fix

- enhance database debugging with detailed connection logging
- revert httpx client configuration that broke Supabase compatibility

## kinemotion-v0.62.0 (2025-12-15)

### Feat

- implement complete backend authentication with modern Supabase key support

### Fix

- use useAuth hook to get session token for feedback submission
- use backend API URL for feedback submission
- use environment variable for backend API URL in database status check

## kinemotion-v0.61.0 (2025-12-15)

### Feat

- update Supabase integration to use modern API keys
- update frontend to use modern Supabase publishable key

## kinemotion-v0.60.1 (2025-12-15)

### Fix

- prevent auth_duration_ms from polluting non-auth logs

## kinemotion-v0.60.0 (2025-12-15)

### Feat

- add authentication performance logging to backend
- add comprehensive i18n support to 5 frontend components

## kinemotion-v0.59.1 (2025-12-15)

### Fix

- add missing i18n translation JSON files to git

## kinemotion-v0.59.0 (2025-12-15)

### Feat

- add comprehensive frontend i18n support with 3 languages

## kinemotion-v0.58.0 (2025-12-14)

### Feat

- update fallback version to match current release

### Fix

- add build step before publishing to PyPI

## kinemotion-v0.57.0 (2025-12-14)

### Feat

- export __version__ in public API

## kinemotion-v0.56.0 (2025-12-14)

### Feat

- try releases again

## kinemotion-v0.55.0 (2025-12-14)

### Feat

- test new release workflow

## v0.54.0 (2025-12-14)

### Continuous Integration

- Upgrade GitHub Actions to latest major versions
  ([`e38da26`](https://github.com/feniix/kinemotion/commit/e38da26da82668d2147576fea581537e4463cd10))

### Features

- Test new release name
  ([`4c1cebc`](https://github.com/feniix/kinemotion/commit/4c1cebc7bbc2a7e70e4513044f3a61645e92b36a))


## v0.53.0 (2025-12-14)

### Features

- Test new release name
  ([`408a825`](https://github.com/feniix/kinemotion/commit/408a82534056822252dd6425920e6a05a80a595a))


## v0.52.0 (2025-12-14)

### Features

- Bump version
  ([`6f0f055`](https://github.com/feniix/kinemotion/commit/6f0f055bd806f947371467dfa3b60720fddbff39))


## v0.51.0 (2025-12-14)

### Chores

- Sync version with PyPI 0.51.0
  ([`13a3806`](https://github.com/feniix/kinemotion/commit/13a380695f9499935c05f3088d7d409df6b7ccf3))

### Features

- Bump version
  ([`751e190`](https://github.com/feniix/kinemotion/commit/751e1908768fee2cf193d79c672174546955c445))

- Sync versions
  ([`03e6413`](https://github.com/feniix/kinemotion/commit/03e6413388142e3b04d535f9c07d653d5f73144e))


## v0.50.1 (2025-12-14)

### Bug Fixes

- Fix version
  ([`e030ed2`](https://github.com/feniix/kinemotion/commit/e030ed2b76315bfcfa21ae61e0d65d99b7e8ba49))

- **backend**: Use configured logger from logging_config
  ([`e38e3bf`](https://github.com/feniix/kinemotion/commit/e38e3bff973ac47efa9c5735a7e45fead2b219f8))


## v0.50.0 (2025-12-13)

### Bug Fixes

- Resolve model import conflicts after refactoring
  ([`75fd4f2`](https://github.com/feniix/kinemotion/commit/75fd4f2e266787512f1691e249ba5a7295ead8cb))

### Features

- Start FastAPI modular architecture refactoring
  ([`eac69f6`](https://github.com/feniix/kinemotion/commit/eac69f6edafaf484c10edfdca0bdad1ce8a9cf34))

### Refactoring

- Complete FastAPI modular architecture refactoring
  ([`6086adf`](https://github.com/feniix/kinemotion/commit/6086adf007c6667e6132cab457cb8a361e4223a6))

- Create modular directory structure
  ([`1f50da6`](https://github.com/feniix/kinemotion/commit/1f50da637c0afed9a492eed9aef46655c51f8aa6))

- Create modular main application structure
  ([`3ba2bb5`](https://github.com/feniix/kinemotion/commit/3ba2bb55fc83e4a78b6e85ed6a5c58e641de5879))

- Create service layer with business logic
  ([`53319e0`](https://github.com/feniix/kinemotion/commit/53319e05e6f996b83c577d264f40261ebc675c4a))

- Extract models from app.py
  ([`23d601d`](https://github.com/feniix/kinemotion/commit/23d601d46c41dccf9834314f89454e47d9a89340))

- Fix frontend-backend API compatibility in modular architecture
  ([`1f78863`](https://github.com/feniix/kinemotion/commit/1f7886335091927508ca5eca69a634dafea503a7))

- Modularize routes into separate modules
  ([`10d2efe`](https://github.com/feniix/kinemotion/commit/10d2efe7eeba344dea06753cba8263e6776c5f44))


## v0.49.0 (2025-12-13)

### Bug Fixes

- Normalize timing log event names to proper snake_case keys
  ([`ecbb154`](https://github.com/feniix/kinemotion/commit/ecbb154dc19f2de47c10bea9f638b13eb71026b4))

### Chores

- Update sonar app version
  ([`2975f7b`](https://github.com/feniix/kinemotion/commit/2975f7bf0ab4732ca92f7c9728ed3d8911992ca1))

### Features

- Implement comprehensive feedback system with Supabase database integration
  ([`9bcf73f`](https://github.com/feniix/kinemotion/commit/9bcf73f79436e2b4de900b58f95258719fcdce80))


## v0.48.0 (2025-12-12)

### Chores

- Configure cursor mcp
  ([`0f344f5`](https://github.com/feniix/kinemotion/commit/0f344f57f9613459de8d6f306b0566f82ff64997))

### Features

- Serve original videos from R2 storage instead of Vercel
  ([`fe74d1f`](https://github.com/feniix/kinemotion/commit/fe74d1fc51103df2fb505a1cdc1f0e1f53845c3f))

- **backend**: Improve R2 storage configuration and testing
  ([`0a8579d`](https://github.com/feniix/kinemotion/commit/0a8579dafaeb0b823e43aefea36b94c08dbe834d))

### Refactoring

- **cmj**: Apply AnalysisOverrides pattern and fix verbose print bug
  ([`3e3c3b8`](https://github.com/feniix/kinemotion/commit/3e3c3b8acc2021d2fb4655027258e195ce0c17c7))

- **dropjump**: Reduce cognitive complexity in process_dropjump_video
  ([`bf4ebfb`](https://github.com/feniix/kinemotion/commit/bf4ebfb3dede9a4a9761d66dcb376633dc980932))

- **dropjump**: Reduce parameters with AnalysisOverrides dataclass
  ([`35f1dce`](https://github.com/feniix/kinemotion/commit/35f1dce09b50ff78cdd34e7967b0258e3469437b))


## v0.47.4 (2025-12-12)

### Bug Fixes

- **cmj**: Remove empty TYPE_CHECKING block
  ([`fb91da8`](https://github.com/feniix/kinemotion/commit/fb91da8b49aebdb52c15e413a22c50f9d952c54b))

### Refactoring

- **cmj**: Reduce cognitive complexity of process_cmj_video from 32 to ≤15
  ([`e646fe0`](https://github.com/feniix/kinemotion/commit/e646fe0d41e857e4a0ca5f3bab1533a966fa1088))


## v0.47.3 (2025-12-12)

### Bug Fixes

- **api**: Remove unused timer parameter from _assess_dropjump_quality
  ([`31ac8ef`](https://github.com/feniix/kinemotion/commit/31ac8efc8b474383f9de72eccc50ea02d408eb86))

### Refactoring

- **api**: Split large api.py into modular architecture
  ([`6eb3f06`](https://github.com/feniix/kinemotion/commit/6eb3f06ab52534e7f97ad85d6e9a361b657cabb8))


## v0.47.2 (2025-12-12)

### Bug Fixes

- **telemetry**: Use structlog for robust error handling
  ([`0c66c5f`](https://github.com/feniix/kinemotion/commit/0c66c5f486c4f034e5833ee0016d37fc31e9240d))

### Documentation

- Update CLAUDE.md with test count and coverage improvements
  ([`1132324`](https://github.com/feniix/kinemotion/commit/1132324fe9bfe907bc6850397fd5370668b1bfa6))

### Refactoring

- Reduce cognitive complexity across validation, kinematics, and API
  ([`04a88cb`](https://github.com/feniix/kinemotion/commit/04a88cbcec3b52bf1767e9647627b839ca842ecf))


## v0.47.1 (2025-12-12)

### Bug Fixes

- **core**: Ensure correct timing.py linting and type safety
  ([`84ea7cf`](https://github.com/feniix/kinemotion/commit/84ea7cf269c81299cf0939b0c28f83c51910a523))


## v0.47.0 (2025-12-12)

### Documentation

- Add basic memory about instrumentation
  ([`8b1dcab`](https://github.com/feniix/kinemotion/commit/8b1dcab83ba14aefbb28bfd03752208089d4bfe4))

### Features

- **core**: Implement granular timing instrumentation using Null Object pattern
  ([`a6a4fdf`](https://github.com/feniix/kinemotion/commit/a6a4fdf7cf9a16090eed5f172ce084cd4ab5879f))

- **telemetry**: Add OpenTelemetry integration and dependencies
  ([`10a56b9`](https://github.com/feniix/kinemotion/commit/10a56b96e4a488c34c62ae6d3a698bf716af3a77))


## v0.46.0 (2025-12-12)

### Features

- **core**: Enhance timing with high-precision measurement and zero-overhead option
  ([`756821e`](https://github.com/feniix/kinemotion/commit/756821e0a050266f09a2d16a20fe014b875e2a0e))


## v0.45.1 (2025-12-11)

### Bug Fixes

- **refactor**: Improve type safety and reduce cognitive complexity
  ([`040f2dc`](https://github.com/feniix/kinemotion/commit/040f2dc02594e40cf30fa9d3ecb5f7d03145707e))

### Chores

- Upgrade frontend packages
  ([`a138481`](https://github.com/feniix/kinemotion/commit/a1384815f19ce10f56700536afc5e908fe62dbf3))


## v0.45.0 (2025-12-11)

### Bug Fixes

- **frontend**: Align Quality Check with Key Performance Indicators
  ([`b071025`](https://github.com/feniix/kinemotion/commit/b0710259c25f501473b9bda3d5f22258a4bb2bb8))

- **frontend**: Exclude test files from tsconfig.json
  ([`493a2ef`](https://github.com/feniix/kinemotion/commit/493a2efb36113717ef1c1e94e7f10e53a5be1366))

### Features

- **frontend**: Implement comprehensive testing suite and UI refactoring
  ([`6dce4c6`](https://github.com/feniix/kinemotion/commit/6dce4c619a73c6594944d713e493e94a1abcb965))

- **frontend**: Improve validation banner display and fix type error
  ([`d9be44d`](https://github.com/feniix/kinemotion/commit/d9be44d0c7100c9de055311556f1bf58f0733fa5))

### Testing

- Update sonar project version
  ([`7f132ea`](https://github.com/feniix/kinemotion/commit/7f132ea20935e9d74303a7e8ad348577cd6c40a0))


## v0.44.0 (2025-12-11)

### Features

- Optimize debug video generation and fix logging warning
  ([`619ccd5`](https://github.com/feniix/kinemotion/commit/619ccd53a4013457033749481cf6792f44529d93))


## v0.43.0 (2025-12-11)

### Continuous Integration

- Remove b ad workflow
  ([`7584229`](https://github.com/feniix/kinemotion/commit/7584229682eb94ddf13a6becac7ad31b96d62f0f))

### Features

- Optimize debug video generation and improve code quality
  ([`81ce698`](https://github.com/feniix/kinemotion/commit/81ce698d5a0fa8dff6c20c6870a7bee52080cef0))

### Testing

- Optimize test suite execution speed
  ([`26ea210`](https://github.com/feniix/kinemotion/commit/26ea21072745ef606405b5f6f5277dd422636baf))


## v0.42.0 (2025-12-10)

### Documentation

- Add some more docs about cpu settings
  ([`ebd0f5b`](https://github.com/feniix/kinemotion/commit/ebd0f5b2c9e1b25a9c95d04b32c35f27560f3584))

- Performance-optimization-pose-tracker-pool
  ([`c1b2e76`](https://github.com/feniix/kinemotion/commit/c1b2e7665371e8384261044a4f3e10202df78dc2))

### Features

- Add debug toggle for optional video overlay generation
  ([`afd0b49`](https://github.com/feniix/kinemotion/commit/afd0b496d3c33d9428c71d417b9cb4b18a5dd9cc))


## v0.41.3 (2025-12-10)

### Bug Fixes

- Capture complete timing breakdown including debug video generation
  ([`77486f2`](https://github.com/feniix/kinemotion/commit/77486f2056630283e83bf3990a02c3bf129df42d))

- Ensure metadata is attached before JSON serialization
  ([`59f5e98`](https://github.com/feniix/kinemotion/commit/59f5e98508ff089a5d00dceb42524908a720bcca))

- Revert "Fix: Performance bottleneck due to PoseTracker re-initialization"
  ([`548e24e`](https://github.com/feniix/kinemotion/commit/548e24eaf60f81e09db0fe978d7526e7fd840ad3))

### Documentation

- Add data about performace pose tracker
  ([`00f71ab`](https://github.com/feniix/kinemotion/commit/00f71ab0ac2d57d8c3e69e6885f0916027502a39))


## v0.41.2 (2025-12-10)

### Bug Fixes

- Revert "add 120s timeout to API requests to prevent duplicate retries"
  ([`576c84a`](https://github.com/feniix/kinemotion/commit/576c84ad9d5f4906ac4133f44a3ac4f47a15c378))


## v0.41.1 (2025-12-10)

### Bug Fixes

- Add 120s timeout to API requests to prevent duplicate retries
  ([`132c67d`](https://github.com/feniix/kinemotion/commit/132c67dc89ba1b7e9f43b0548e3b5596ecd4ad8b))


## v0.41.0 (2025-12-10)

### Features

- Add comprehensive timing instrumentation across backend and core pipeline
  ([`acb3df6`](https://github.com/feniix/kinemotion/commit/acb3df65d2895fbdae7fcc7f52a73bf7b6fb36d1))

- Implement hybrid timing instrumentation with PerformanceTimer abstraction
  ([`b207193`](https://github.com/feniix/kinemotion/commit/b207193e047c869e52dfe5303616806f491f938f))


## v0.40.0 (2025-12-10)

### Documentation

- Switch formatting tool from black to ruff in GEMINI.md
  ([`7bf2e3e`](https://github.com/feniix/kinemotion/commit/7bf2e3e073fea368470359a0bdff65b8568e48e1))

### Features

- Add detailed timing logs to analysis pipeline
  ([`4c75820`](https://github.com/feniix/kinemotion/commit/4c758201be03dbd06f463e2434ca287bb123bfd5))

### Testing

- Relax flight time assertion in kinematics test
  ([`b360c4d`](https://github.com/feniix/kinemotion/commit/b360c4de88c92e365657775041fe7eea04892a27))


## v0.39.1 (2025-12-10)

### Bug Fixes

- Prioritize browser-compatible video codecs
  ([`76ea08f`](https://github.com/feniix/kinemotion/commit/76ea08fd6edb3d0e0269b2e05db90a98e99777c1))

- Use ffmpeg re-encoding only as a fallback
  ([`d55923f`](https://github.com/feniix/kinemotion/commit/d55923f9c09d0d8507519c140b58485eaabb4f86))


## v0.39.0 (2025-12-10)

### Bug Fixes

- Proxy the health endpoint to the backend
  ([`f1d45d2`](https://github.com/feniix/kinemotion/commit/f1d45d2b194e39f96d43c0462960e80e236a8df9))

- Use presigned URLs for R2 storage access
  ([`ffd642e`](https://github.com/feniix/kinemotion/commit/ffd642e4c597447f8eee9d4275f48695a7862cf6))

- **dropjump**: Use argmin for landing detection in finding acceleration spike
  ([`1dd1e1a`](https://github.com/feniix/kinemotion/commit/1dd1e1abff7a3c4aae6675f8aa5f2ddf46de76f6))

- **kinematics**: Correct scale and phase detection logic for CMJ/DJ
  ([`283b560`](https://github.com/feniix/kinemotion/commit/283b560e69c5785a0d18c5b411e89fedc2a8a7bd))

### Chores

- Remove basic-memory naming hook and cleanup documentation
  ([`b2f41ce`](https://github.com/feniix/kinemotion/commit/b2f41ce5d81a23090d2f60bd1a79451bd363bd77))

### Features

- Improve frontend
  ([`241f2f5`](https://github.com/feniix/kinemotion/commit/241f2f58055c241f9919af70156f5ec586ed249f))

- Improve frontend
  ([`d6e69f3`](https://github.com/feniix/kinemotion/commit/d6e69f335cf6cee4da8affbab876b858aa04af12))

- Integrate Cloudflare R2 storage and debug video overlay
  ([`b7b05bd`](https://github.com/feniix/kinemotion/commit/b7b05bd500a26d742d78d1670079fb201af49140))

### Testing

- Update R2 integration tests
  ([`955aa86`](https://github.com/feniix/kinemotion/commit/955aa8610040548635c0f34a931e402825740995))


## v0.38.1 (2025-12-09)

### Bug Fixes

- **backend**: Add backend README.md copy and sync backend deps for uvicorn
  ([`996e7ed`](https://github.com/feniix/kinemotion/commit/996e7ed9a438b79e24fe6695b03aa0e0092bbc3f))

### Documentation

- **memory**: Add AthletePose3D investigation findings to basic-memory
  ([`597e41c`](https://github.com/feniix/kinemotion/commit/597e41cb2dd965de69fcf46ebdaa3241dbc49ff4))


## v0.38.0 (2025-12-09)

### Bug Fixes

- Use workspace lock with kinemotion local source for cross-platform determinism
  ([`b6b79b9`](https://github.com/feniix/kinemotion/commit/b6b79b9424a57d6dd27bb26b1630a5a752b75608))

- **backend**: Use dict unpacking for TypedDict compatibility in determinism endpoint
  ([`c186a14`](https://github.com/feniix/kinemotion/commit/c186a1474cc34c67df188989de62de38684e3b0b))

- **backend**: Use json serialization for TypedDict in determinism endpoint
  ([`f9b64dc`](https://github.com/feniix/kinemotion/commit/f9b64dc13f718d2184605424898d24a9f45b056e))

- **backend**: Use to_dict() method for DropJumpMetrics serialization
  ([`6f3ba7c`](https://github.com/feniix/kinemotion/commit/6f3ba7c0267e126b3a16e24894909ec320585cb8))

- **backend**: Use type-safe dict return for determinism endpoint
  ([`34afd01`](https://github.com/feniix/kinemotion/commit/34afd01211332bddd096ece619023b4f7bebf1a9))

### Features

- **backend**: Add full drop jump analysis endpoint for determinism testing
  ([`0b57c81`](https://github.com/feniix/kinemotion/commit/0b57c81f667dd20710493adb56d1fd32052cbd20))


## v0.37.0 (2025-12-09)

### Chores

- Organize permissions list and add sequential-thinking tool
  ([`64aaf72`](https://github.com/feniix/kinemotion/commit/64aaf72b44fbb3561f84ec5e12f9ec14c2d0d05b))

### Features

- **backend**: Add determinism testing endpoints for M1 vs Intel comparison
  ([`8447790`](https://github.com/feniix/kinemotion/commit/8447790f6aef2bd11fdfa086ce4e67b5226de9e2))


## v0.36.1 (2025-12-08)

### Bug Fixes

- **dropjump**: Improve analysis reproducibility with temporal averaging
  ([`6f98b1f`](https://github.com/feniix/kinemotion/commit/6f98b1f918539e714b604ac1a0bf6187c6ff28a6))

### Chores

- Up the mem of the backend
  ([`67133ca`](https://github.com/feniix/kinemotion/commit/67133ca2cded45df74ef5bfe3e9d9b7d85bde1a9))


## v0.36.0 (2025-12-07)

### Bug Fixes

- **backend**: Upgrade kinemotion to v0.35.1 to fix negative metrics bug
  ([`492dfaa`](https://github.com/feniix/kinemotion/commit/492dfaa87251e527bef0c85822314b7d57ecd48c))

### Documentation

- Fix broken links in agents-guide
  ([`1daaffb`](https://github.com/feniix/kinemotion/commit/1daaffb43de1db48c0decba66f1f73a28b56c124))

### Features

- Add version display in frontend footer
  ([`cb4ed66`](https://github.com/feniix/kinemotion/commit/cb4ed669f642430f5bad4b900489d6858235eb43))


## v0.35.2 (2025-12-07)

### Bug Fixes

- **validation**: Resolve CMJ athlete profile misclassification
  ([`1565514`](https://github.com/feniix/kinemotion/commit/156551412c50090c589bda9cacc8e62a542db19f))


## v0.35.1 (2025-12-07)

### Bug Fixes

- **detection**: Improve event detection accuracy through empirical validation
  ([`f9f6c91`](https://github.com/feniix/kinemotion/commit/f9f6c917904bfcb95ef9bd988867a2b824cc59c8))

### Chores

- Change settings and update basic memory
  ([`41390d3`](https://github.com/feniix/kinemotion/commit/41390d336d0d8083606903f6c263841000fc2f17))

- Sonar relase update
  ([`e8edc51`](https://github.com/feniix/kinemotion/commit/e8edc510a5b9e793766cc4c5acfb033f63e8f892))

### Documentation

- Update CMJ camera angle recommendation to 45° oblique
  ([`c3f09fa`](https://github.com/feniix/kinemotion/commit/c3f09faf4ebb1c12a2ddb4bacb5ba9aaeab936c7))


## v0.35.0 (2025-12-02)

### Chores

- Add missing Supabase client and fix TypeScript errors
  ([`126839f`](https://github.com/feniix/kinemotion/commit/126839f8723a36ea62019b724ad43ea87b2e353f))

- Exclude non-source directories from ruff linting
  ([`af62d04`](https://github.com/feniix/kinemotion/commit/af62d04b91cba3f40eca624ce9c5c1fcd3b4c802))

- **test**: Use safe dict access in CMJ kinematics test
  ([`48dc977`](https://github.com/feniix/kinemotion/commit/48dc977ab54dae9f0e94e9da5133307348cfe72f))

### Code Style

- Format code with ruff and fix basic-memory permalinks
  ([`4c3c23a`](https://github.com/feniix/kinemotion/commit/4c3c23a44501ee9357fac76884bdf09ff9f72741))

### Continuous Integration

- Fix docker build
  ([`56c8cb8`](https://github.com/feniix/kinemotion/commit/56c8cb84bb4478559c9121ec47f4e22244200dd6))

- Implement least-privilege service account separation for Cloud Run deployment
  ([`2fdfaad`](https://github.com/feniix/kinemotion/commit/2fdfaad5d15c0f2fcca98d5d9263af8f6a044d2c))

- Skip release workflow for deployment-only changes
  ([`ff34ebf`](https://github.com/feniix/kinemotion/commit/ff34ebf9b12107795dd57a2462cb4e47eea211ad))

- **backend**: Correct Docker port configuration for Cloud Run deployment
  ([`35fd087`](https://github.com/feniix/kinemotion/commit/35fd0874e9aa937dde3aadb8222431bf60a39191))

### Documentation

- Add Google OAuth setup guide and script review documentation
  ([`1260aff`](https://github.com/feniix/kinemotion/commit/1260aff7c9b82c19f34fbc8fb506592ac450f97d))

- Add repository split migration guides for backend and frontend
  ([`0c4d85f`](https://github.com/feniix/kinemotion/commit/0c4d85f2685a5f39791c43626d3b1cc8be4aaaf6))

- Fix basic-memory documentation format issues
  ([`a818d6c`](https://github.com/feniix/kinemotion/commit/a818d6cd54086dc43ce4b2be46a6d007cb9442cc))

- Update documentation
  ([`f302044`](https://github.com/feniix/kinemotion/commit/f302044c896cd5edbfcc3dee2bdb0f580be723ce))

- Update project state and deployment documentation
  ([`845628d`](https://github.com/feniix/kinemotion/commit/845628d8e4f6184eeb61ef4fdaa1aa3dab5dcce5))

### Features

- Add decorators for marking unused/experimental features
  ([`b96076e`](https://github.com/feniix/kinemotion/commit/b96076e59bbfddbd75057ba90d36b4a36bf2a2d1))

### Refactoring

- Eliminate code duplication by moving interpolate_threshold_crossing to core
  ([`1ea8da0`](https://github.com/feniix/kinemotion/commit/1ea8da03ae1a649ab51c467882cb0f83b3e16260))

- Extract validation base classes and move jump-specific validators
  ([`7c78c53`](https://github.com/feniix/kinemotion/commit/7c78c532b8a50ba3dfa64e4fc00f720b50c0180f))

- Mark 6 additional unused functions in analysis modules
  ([`631834d`](https://github.com/feniix/kinemotion/commit/631834d3550e644a0101c238c76c0e3976ba77a6))

- Mark adaptive_smooth_window as unused
  ([`b70debe`](https://github.com/feniix/kinemotion/commit/b70debef780ed8405b6a4699f85e24e1669aede1))

- **test**: Reorganize test suite and centralize fixtures
  ([`5a78e9c`](https://github.com/feniix/kinemotion/commit/5a78e9ca5f0461dd467b2bd0bbe61d9e5719ee26))

### Testing

- Complete P0/P1/P2 test suite improvements
  ([`cf40ffc`](https://github.com/feniix/kinemotion/commit/cf40ffc04910ccadef1308ff6385a679c2a808bb))

- Improve coverage for smoothing and CMJ CLI modules
  ([`e728a93`](https://github.com/feniix/kinemotion/commit/e728a930c222dc0027c9a385fa7182a1dc6e0b4c))


## v0.34.0 (2025-12-02)

### Chores

- Add Supabase setup scripts and update deployment script
  ([`474ffd1`](https://github.com/feniix/kinemotion/commit/474ffd1efc16bd32810fda2c3c34edb5bf754e42))

- Sync backend/uv.lock with workspace lock and update Docker build
  ([`9021b54`](https://github.com/feniix/kinemotion/commit/9021b54c1b99f6cbb4b5146aceb53cb21f84247f))

### Continuous Integration

- Add artifact registry permissions to github actions setup script
  ([`0d0ccf3`](https://github.com/feniix/kinemotion/commit/0d0ccf398ceaa5e51fae9f4b86d65b28dc89e97e))

- Build and push docker images to gcr instead of cloud run source build
  ([`9e8f7cf`](https://github.com/feniix/kinemotion/commit/9e8f7cfa9a525b1bc5006665856649c226d756f5))

- Remove Trivy vulnerability scanner from build job
  ([`c436d4f`](https://github.com/feniix/kinemotion/commit/c436d4f63626efff3d9e2a85ea0d7abcb5906956))

- Update github actions to latest major versions
  ([`38cb8b0`](https://github.com/feniix/kinemotion/commit/38cb8b047a84dadc668e9ce91d2575a596c46e59))

- Update GitHub Actions to latest versions
  ([`721c1e0`](https://github.com/feniix/kinemotion/commit/721c1e027d66926ba43ee375fa4a7563b5fb5e09))

### Documentation

- Move Supabase authentication documentation to basic-memory
  ([`33957a6`](https://github.com/feniix/kinemotion/commit/33957a6017a2d913490c688b82042aeb7cdcc54f))

- Update basic-memory with Supabase authentication documentation
  ([`d37e097`](https://github.com/feniix/kinemotion/commit/d37e09768f33f127c0fe32d3e2750b2adaef8f92))

### Features

- Add Supabase authentication to frontend
  ([`2a38391`](https://github.com/feniix/kinemotion/commit/2a38391cfe6141b51122ea3df554474a441e5d16))


## v0.33.2 (2025-12-01)

### Bug Fixes

- **backend**: Resolve R2 integration test failures
  ([`366463e`](https://github.com/feniix/kinemotion/commit/366463e1ad4cee582c7a222d46427c473908d2b1))

### Documentation

- Update analysis with R2 integration test fixes
  ([`d7a2f20`](https://github.com/feniix/kinemotion/commit/d7a2f20790441fa6d25ba6785cd677eba2b45908))


## v0.33.1 (2025-12-01)

### Bug Fixes

- **backend**: Handle KeyboardInterrupt during pytest fixture teardown
  ([`0f83afe`](https://github.com/feniix/kinemotion/commit/0f83afe3728579a8b575ccd7681b40247f426849))

### Chores

- Update MCP and IDE configuration, document KeyboardInterrupt analysis
  ([`6f1d188`](https://github.com/feniix/kinemotion/commit/6f1d188130fba6f25e2993ccb03874d8ca3bfdf6))

### Continuous Integration

- Add manual workflow dispatch trigger for backend deployment
  ([`f520667`](https://github.com/feniix/kinemotion/commit/f520667fe4c063ca6a7a9755d5a632634b77005a))


## v0.33.0 (2025-12-01)

### Chores

- Trigger vercel redeploy
  ([`59c6b24`](https://github.com/feniix/kinemotion/commit/59c6b24277af4d3cfd20bc7a299a34023f17bb73))

- **backend**: Add localhost:8888 to CORS origins for local testing
  ([`bf9db7f`](https://github.com/feniix/kinemotion/commit/bf9db7f273a3afe51a360d55b7548f25fd9bee02))

- **backend**: Reorder middleware so CORS wraps rate limiter
  ([`fb66bc4`](https://github.com/feniix/kinemotion/commit/fb66bc4ac8db6b82740418b78c1cf6eb84cde874))

### Continuous Integration

- Add automated Cloud Run deployment with Workload Identity Federation
  ([`d3381ae`](https://github.com/feniix/kinemotion/commit/d3381ae853a09568c41f05bd4eada217f5c376f7))

### Documentation

- **deployment**: Add automated deployment setup guide with workload identity
  ([`a483592`](https://github.com/feniix/kinemotion/commit/a48359230c2e168e40e41b99c0b992836e6547c4))

- **deployment**: Add production deployment and troubleshooting guides
  ([`006eee8`](https://github.com/feniix/kinemotion/commit/006eee8c9aa18025c1679942e4e0191d97784a55))

### Features

- **backend**: Add referer validation and document code quality metrics
  ([`716efb3`](https://github.com/feniix/kinemotion/commit/716efb33329768413779dacc4c6de988c91f34a2))


## v0.32.3 (2025-11-30)

### Bug Fixes

- **backend**: Explicitly allow CORS headers for multipart form data
  ([`d7ad685`](https://github.com/feniix/kinemotion/commit/d7ad685cf4bab2945b22d04d6f34c77bcccd8eac))

### Chores

- **frontend,backend**: Remove debug logging
  ([`ba6b753`](https://github.com/feniix/kinemotion/commit/ba6b753369c2992a3b28311290b02290c26bc970))


## v0.32.2 (2025-11-30)

### Bug Fixes

- **backend,frontend**: Improve CORS handling and add debug logging
  ([`e8817cf`](https://github.com/feniix/kinemotion/commit/e8817cf8552bf0248f3492cc74c44aa14c619a0e))

### Chores

- **backend**: Fix CORS configuration for production
  ([`c0270f7`](https://github.com/feniix/kinemotion/commit/c0270f7c73dc3f3a94c09334ad26205544f221c4))


## v0.32.1 (2025-11-30)

### Bug Fixes

- **frontend**: Correct API endpoint path for production backend
  ([`dbda4c2`](https://github.com/feniix/kinemotion/commit/dbda4c2c7786c49844e39610fff31d39b7a7b29e))

### Chores

- Configure vercel.json for frontend subdirectory build
  ([`5d755b5`](https://github.com/feniix/kinemotion/commit/5d755b5a20c0b1a99d39f28d9b3524cff4ac3ce0))

- Exclude yarn binary from pre-commit hooks and embed yarn 4.12.0
  ([`0cbfbdb`](https://github.com/feniix/kinemotion/commit/0cbfbdb8bf0b586d50b24443e2d2fcc0e8ef3e6b))

- Fix basic-memory permalink naming convention
  ([`134ceba`](https://github.com/feniix/kinemotion/commit/134cebaee4d992731ecbf008adb887f6a951a951))

- Ignore generated files in ./frontend
  ([`83207fc`](https://github.com/feniix/kinemotion/commit/83207fc94e61e4be7caff9a40f1878670fc093f0))

- Update basic memory notes and configurations
  ([`4753d57`](https://github.com/feniix/kinemotion/commit/4753d57ccb2c9c3fd21fd20e029d90e53a43d21a))

- Update basic memory permalinks
  ([`c35aa0f`](https://github.com/feniix/kinemotion/commit/c35aa0f7b381a4c57c866829aa955bbbd6cff734))

- Update Claude Code hooks, MCP configuration, and gitignore
  ([`8cb82b2`](https://github.com/feniix/kinemotion/commit/8cb82b2ef3e3ac4bc3e6ce94e11a1c55d66910b5))

- **frontend**: Explicitly specify tsconfig path for tsc in build scripts
  ([`4f83f6d`](https://github.com/feniix/kinemotion/commit/4f83f6da46dd4cf7ecb0b3843652b44276a1ffa6))

- **frontend**: Simplify build script - tsc can now find tsconfig
  ([`5560738`](https://github.com/feniix/kinemotion/commit/55607380e37955c0256fdb06f00bbb1adfde0fdf))

- **frontend**: Track tsconfig files required for vercel build
  ([`a70fd47`](https://github.com/feniix/kinemotion/commit/a70fd4759acda649df9eb1fcabfafe7daee18b86))

- **vercel**: Configure yarn 4.12.0 and verify build output directory
  ([`1a4ac40`](https://github.com/feniix/kinemotion/commit/1a4ac40426d8e24ea0d116b71fb37ce4c2a1490d))

- **vercel**: Enable corepack to respect yarn 4.12.0 from packageManager field
  ([`4e333fa`](https://github.com/feniix/kinemotion/commit/4e333fab60a3b02bda2de6d517fd403449a399f7))

- **vercel**: Move vercel.json to frontend directory for correct configuration loading
  ([`8fc5f5a`](https://github.com/feniix/kinemotion/commit/8fc5f5acfc7be62be896cab9ca57945ec604c71f))

- **vercel**: Remove cd commands - Root Directory already in frontend context
  ([`e577c75`](https://github.com/feniix/kinemotion/commit/e577c7531468f09e5f161335342d9c1ef01c277a))


## v0.32.0 (2025-11-29)

### Bug Fixes

- **vercel**: Add explicit directory context for monorepo build
  ([`b7f4799`](https://github.com/feniix/kinemotion/commit/b7f4799a1061a5b82881f81e7fb618327a3b8eb2))

- **vercel**: Remove redundant cd commands - Root Directory already sets context
  ([`5879608`](https://github.com/feniix/kinemotion/commit/5879608ed570f1745eb693db226b51689878c1b9))

### Chores

- Add Yarn generated files to .gitignore
  ([`199d122`](https://github.com/feniix/kinemotion/commit/199d12236064070197221f2edcb6e2d108d2128a))

- Remove root vercel.json to rely on Vercel auto-detection
  ([`12df352`](https://github.com/feniix/kinemotion/commit/12df3524a6506c3624be527c394589b765ccf975))

- Trigger Vercel rebuild with latest commits
  ([`b7c1bf8`](https://github.com/feniix/kinemotion/commit/b7c1bf8c5a10199029d4bdaf24d628dac3f8f996))

- **frontend**: Add .yarnrc.yml for yarn 4 configuration
  ([`5a04b21`](https://github.com/feniix/kinemotion/commit/5a04b219182781aebad00ef9ff9b0961d1d090d1))

### Features

- **frontend**: Upgrade to latest stable versions of all dependencies
  ([`3c21e44`](https://github.com/feniix/kinemotion/commit/3c21e4427c5bf6564001097adefe6e233b2e5aee))


## v0.31.4 (2025-11-29)

### Bug Fixes

- Add root vercel.json with explicit build configuration
  ([`999f2c9`](https://github.com/feniix/kinemotion/commit/999f2c90a147e04fb7290f49d9de2ddbdb64ffe0))

- Simplify vercel.json paths since Root Directory is set to frontend
  ([`3696a1b`](https://github.com/feniix/kinemotion/commit/3696a1bf2149a0520a6c161a63a7e530a8769eac))


## v0.31.3 (2025-11-29)

### Bug Fixes

- Remove frontend/vercel.json to let Vercel auto-detect from Root Directory
  ([`9984b78`](https://github.com/feniix/kinemotion/commit/9984b783e725af06faedaa619b4254e38960fdd6))


## v0.31.2 (2025-11-29)

### Bug Fixes

- Remove hacky vercel.json configuration
  ([`2b57805`](https://github.com/feniix/kinemotion/commit/2b578059576824aa065180e3c1452340a7ffff20))

### Chores

- Add frontend vercel configuration and deployment best practice docs
  ([`7f09a07`](https://github.com/feniix/kinemotion/commit/7f09a0740010a0a1a62086f0a346cba5fadf3cbd))


## v0.31.1 (2025-11-29)

### Bug Fixes

- Correct Vercel configuration schema for monorepo deployment
  ([`57f2636`](https://github.com/feniix/kinemotion/commit/57f263644c0010e5ef31596a623dc52e527bd035))

- Use yarn --cwd flag for monorepo deployment
  ([`914e184`](https://github.com/feniix/kinemotion/commit/914e18421a2f4b7964be2553b8c61d472ba9a8dc))

### Chores

- Add Vercel monorepo configuration and allow vercel.json in git
  ([`9512211`](https://github.com/feniix/kinemotion/commit/951221120730dd716c2a03fbbf91be44155bb065))


## v0.31.0 (2025-11-29)

### Chores

- Fix basic-memory frontmatter and exclude serena from mdformat
  ([`d4ec428`](https://github.com/feniix/kinemotion/commit/d4ec428db06cf868b411ab12305af8a4d4a2c536))

- Fix line length violations and reorganize documentation
  ([`647c704`](https://github.com/feniix/kinemotion/commit/647c704c67df6aa5dc8370a39d1f1183a0594909))

- Update local_dev.sh with correct module import path
  ([`749fe8f`](https://github.com/feniix/kinemotion/commit/749fe8f03a5a1ba1e25a1e4fd61987aacc76bcef))

### Documentation

- **issue-10**: Add camera perspective validation analysis and recording protocols
  ([`755f2ce`](https://github.com/feniix/kinemotion/commit/755f2cedf4249a96aa82b22d9bc22ab86b9ca696))

### Features

- Add React frontend application for video analysis UI
  ([`b2d32ed`](https://github.com/feniix/kinemotion/commit/b2d32eda0ad9a3ad89d7c6de26c89ae63c23a1e2))

- **backend**: Implement FastAPI video analysis backend with deployment infrastructure
  ([`0e70728`](https://github.com/feniix/kinemotion/commit/0e70728abaffe58c6870d9ea2f6b2a221c33e4a0))

- **deployment**: Add Google Cloud Run deployment infrastructure
  ([`90da5a7`](https://github.com/feniix/kinemotion/commit/90da5a7e4e83850f4c4a3e6704a3196ab914b9da))


## v0.30.0 (2025-11-26)

### Chores

- Clean up old memory file renames
  ([`3c47d2d`](https://github.com/feniix/kinemotion/commit/3c47d2d826e6b38dd088490a707347e32fa79496))

- **memory**: Rename memory files to kebab-case convention
  ([`f747f44`](https://github.com/feniix/kinemotion/commit/f747f442da506e390f815396416817ee8a08cec8))

### Documentation

- **claude**: Add MVP-first roadmap section
  ([`a9761d8`](https://github.com/feniix/kinemotion/commit/a9761d8131e0d93504aeae1f262315084a743e5f))

- **memories**: Add project context and MVP strategy to serena
  ([`e44d5eb`](https://github.com/feniix/kinemotion/commit/e44d5ebb4d92871889486dbb0cb59f69170a1db6))

- **memory**: Add MVP strategy memory files to basic-memory
  ([`3bcf7c7`](https://github.com/feniix/kinemotion/commit/3bcf7c767141b2a7eeadbf8765e82236aa86140f))

- **strategy**: Pivot to MVP-first approach with validation gates
  ([`806e77d`](https://github.com/feniix/kinemotion/commit/806e77d2a87c6dc16b92e18ce7e6109f1844a482))

### Features

- **validation**: Implement biomechanics specialist recommendations
  ([`4cb440b`](https://github.com/feniix/kinemotion/commit/4cb440b35fe47b06f754c5454bcfca0479f1ed6c))

### Testing

- **cmj**: Add phase progression and bounds tests (Issue #11)
  ([`9fcb033`](https://github.com/feniix/kinemotion/commit/9fcb033491abaaa3d40552478d4736bb535b8f46))


## v0.29.3 (2025-11-26)

### Bug Fixes

- **docs**: Update type checker and add OpenSSF badge
  ([`3c08a51`](https://github.com/feniix/kinemotion/commit/3c08a5199e407718087562c769577578f4a5b844))


## v0.29.2 (2025-11-18)

### Bug Fixes

- **docs**: Resolve document generation issues
  ([`db5c759`](https://github.com/feniix/kinemotion/commit/db5c759bb244d4a82e185ec8a1db6bed07a33e36))


## v0.29.1 (2025-11-18)

### Bug Fixes

- Fix test_deep_squat_cmj_recreational_athlete
  ([`4ec6d8d`](https://github.com/feniix/kinemotion/commit/4ec6d8d0d0bd90c8e1a28a2892d7172f9849a46e))

- Fix test_deep_squat_cmj_recreational_athlete
  ([`c3a99ef`](https://github.com/feniix/kinemotion/commit/c3a99ef42be85e6963e08856353f487beff4ea07))


## v0.29.0 (2025-11-18)

### Bug Fixes

- Correct ankle angle calculation using foot_index instead of heel
  ([`422020c`](https://github.com/feniix/kinemotion/commit/422020c33cdf95b64bb7371c27ee030a220a6e0c))

- Extend landing detection search window for realistic flight times
  ([`c4a6e7b`](https://github.com/feniix/kinemotion/commit/c4a6e7b82dff14272cad75e9db6e3a54a6da4a9e))

- **ci**: Add cache invalidation to ensure fresh install of updated code
  ([`43b3a7a`](https://github.com/feniix/kinemotion/commit/43b3a7ab0ae4112e233e719186cdefd01a16daa1))

- **ci**: Disable uv cache completely to ensure fresh builds
  ([`b109d30`](https://github.com/feniix/kinemotion/commit/b109d3020191adb31692b22d299b40a9aaaf1596))

- **ci**: Force complete rebuild with --reinstall to clear stale wheel cache
  ([`303efe6`](https://github.com/feniix/kinemotion/commit/303efe64344006ac2d87d272c61e12b0e83c95f2))

- **cmj**: Improve phase detection robustness for ambiguous derivatives
  ([`f810001`](https://github.com/feniix/kinemotion/commit/f8100013ffb321047b13248d1e2881ee641b0858))

### Chores

- Add justfile with clean commands for generated files
  ([`6d82500`](https://github.com/feniix/kinemotion/commit/6d825007d77bfcdd5bd11fd5a8db654b50ee58e6))

- Add subagent configuration
  ([`81adc7a`](https://github.com/feniix/kinemotion/commit/81adc7a7d7b50d89f5134c98e94652ee1e5015e1))

- Fix agent definitions
  ([`8606c38`](https://github.com/feniix/kinemotion/commit/8606c380cd983ce29b5a629e5d5220894dbd2f30))

- Store local information and serena config
  ([`ada78aa`](https://github.com/feniix/kinemotion/commit/ada78aa099cd23e4387aebe9cdafdefaa7896bf1))

### Continuous Integration

- Fix stale bytecode caching in CI environment
  ([`1673010`](https://github.com/feniix/kinemotion/commit/1673010a44773f87fad6b8b1bb62f8e5c9cd05bb))

- Fix verification step to use uv run for proper environment
  ([`5ae325d`](https://github.com/feniix/kinemotion/commit/5ae325d04812b85c3933225170a9c12ef0fa10d4))

- Trigger fresh build after clearing all caches
  ([`d3b69a3`](https://github.com/feniix/kinemotion/commit/d3b69a3c6c133e33b7f6c99fbf6b11a06c281b57))

### Documentation

- Clarify landing frame detection algorithm and window extension rationale
  ([`965d60b`](https://github.com/feniix/kinemotion/commit/965d60bf310608e338ed7112ebdaafcbcf42e9aa))

- Strategy
  ([`3fc9a31`](https://github.com/feniix/kinemotion/commit/3fc9a31890315b1bad68d6c6ec89dc891123254d))

- Update README and CLAUDE.md with accurate metrics and JSON examples
  ([`f31be43`](https://github.com/feniix/kinemotion/commit/f31be4315f754528abb7e444d9c297a8ce12d41a))

- Use correct naming for basic-memory
  ([`ee55a50`](https://github.com/feniix/kinemotion/commit/ee55a504340ffed86586321e085290aed3319541))

### Features

- **cmj**: Expand CMJ testing with physiological bounds validation
  ([`3289367`](https://github.com/feniix/kinemotion/commit/328936787f4d644f4a3cd8a981de99f04f438273))

### Testing

- Add test for cmj joint angles
  ([`6dd97a2`](https://github.com/feniix/kinemotion/commit/6dd97a28354c4794e77dd26b2bfd3d2df6b631f1))

- Adjust flight time tolerance for synthetic CMJ test
  ([`dd196cb`](https://github.com/feniix/kinemotion/commit/dd196cb5692615a658d1a154138c3ba129e955db))


## v0.28.0 (2025-11-15)

### Features

- Standardize numeric precision across jump types
  ([`def84b0`](https://github.com/feniix/kinemotion/commit/def84b00ba4aef35f398ac615e328ba15e50133d))


## v0.27.0 (2025-11-14)

### Features

- Extract video codec from metadata
  ([`52c7ff2`](https://github.com/feniix/kinemotion/commit/52c7ff2ee3f6620a5271f670ab60e6bca8bc38fb))


## v0.26.1 (2025-11-14)

### Bug Fixes

- Reduce cognitive complexity in ground contact detection and API
  ([`57f0424`](https://github.com/feniix/kinemotion/commit/57f0424043e4f15540851157220133e7361213a1))


## v0.26.0 (2025-11-14)

### Features

- Implement known height validation (Task 1.4)
  ([`6f9dbf9`](https://github.com/feniix/kinemotion/commit/6f9dbf9a78f073e02593067280ee0661fd2f2545))

### Refactoring

- Reduce cognitive complexity in DropJumpMetrics.to_dict() from 17 to 3
  ([`1f6c99b`](https://github.com/feniix/kinemotion/commit/1f6c99b11979b6d336d14c329f2409be0ebbc6db))


## v0.25.0 (2025-11-14)

### Documentation

- Add comprehensive validation status and roadmap
  ([`207b3ab`](https://github.com/feniix/kinemotion/commit/207b3abf4790e423ab69340eee98781aa9bcadc6))

- Add presentation
  ([`0f2715a`](https://github.com/feniix/kinemotion/commit/0f2715adf93a01fd12c72cd310339daf5d072b3e))

- Add research papers
  ([`b623c2a`](https://github.com/feniix/kinemotion/commit/b623c2ab265f34bedb38b6174958368bbd5e53bf))

- Google colab
  ([`98f474c`](https://github.com/feniix/kinemotion/commit/98f474cde68d5bc5ec3b7dc7f438eb912ebc617d))

- Google colab
  ([`f6bc11b`](https://github.com/feniix/kinemotion/commit/f6bc11bb08a566e846a0eb3549cf8e752839c54d))

### Features

- Add automatic quality assessment and confidence scores to all outputs
  ([`8eee0e0`](https://github.com/feniix/kinemotion/commit/8eee0e051c3ac4fee8610f05f5735676a4d50331))

- Refactor CLI to call API functions, adding automatic quality assessment
  ([`b6511cb`](https://github.com/feniix/kinemotion/commit/b6511cbbb7bb93458b827d967636d72391651d0e))

- Restructure JSON output to data/metadata format
  ([`bb00d3e`](https://github.com/feniix/kinemotion/commit/bb00d3e871c68369dcbb308429084b11eecad0e0))

### Testing

- Add determinism validation scripts and confirm algorithm reliability
  ([`bd115b0`](https://github.com/feniix/kinemotion/commit/bd115b056b91a55027c5b85362cc3942cf6ea7c5))

### Breaking Changes

- JSON output format restructured from flat to nested {data, metadata}


## v0.24.0 (2025-11-11)

### Features

- Document platform-specific system dependencies for Windows, macOS, and Linux
  ([`928a6ad`](https://github.com/feniix/kinemotion/commit/928a6adbef18df77f5941ae0b2e82ba9d62a38b7))


## v0.23.0 (2025-11-10)

### Features

- Extract visibility calculation helper to improve code maintainability
  ([`2839d6e`](https://github.com/feniix/kinemotion/commit/2839d6eca4b4f6ff8b6247501560939953282943))


## v0.22.1 (2025-11-10)

### Bug Fixes

- Skip batch mode tests in CI to prevent MediaPipe multiprocessing crashes
  ([`05dd796`](https://github.com/feniix/kinemotion/commit/05dd796b36252323c36f8d503c372d96e4108381))


## v0.22.0 (2025-11-10)

### Bug Fixes

- Make CLI batch tests resilient to processing failures in CI
  ([`1f3dfed`](https://github.com/feniix/kinemotion/commit/1f3dfedbe88a2c9be21c907053e549ee2431c500))

### Features

- Comprehensive test coverage expansion and documentation refactoring
  ([`dc3cda4`](https://github.com/feniix/kinemotion/commit/dc3cda4e022b61f635e537784aafc08e0f6e78fe))


## v0.21.0 (2025-11-10)

### Features

- Add TypedDict and type aliases for improved type safety
  ([`053e010`](https://github.com/feniix/kinemotion/commit/053e010cf80e1c91d5900c39d49b1d7ac2ac6ab4))


## v0.20.2 (2025-11-10)

### Bug Fixes

- Achieve 80%+ coverage on video_io for SonarCloud quality gate
  ([`ed77fdb`](https://github.com/feniix/kinemotion/commit/ed77fdb080f143c492c724c9f4a138b2a364ad7e))


## v0.20.1 (2025-11-10)

### Bug Fixes

- Add test coverage for ffprobe warning path
  ([`8ae3e55`](https://github.com/feniix/kinemotion/commit/8ae3e552a3bfb749d4e9bad10c634093db5eddee))


## v0.20.0 (2025-11-10)

### Features

- Add platform-specific installation guide and ffprobe warnings
  ([`b61c8c6`](https://github.com/feniix/kinemotion/commit/b61c8c6dbc2191ca321a2b813aa995c3a68b0b0b))


## v0.19.0 (2025-11-10)

### Features

- Add comprehensive badge layout to README
  ([`e1e2ca3`](https://github.com/feniix/kinemotion/commit/e1e2ca38c67077092bfc1455acfbe8a424e5d4b4))


## v0.18.2 (2025-11-10)

### Bug Fixes

- Ci build
  ([`5bbfc0f`](https://github.com/feniix/kinemotion/commit/5bbfc0fa610ff811e765dea2021602f09d02f9f8))

### Testing

- Add comprehensive test coverage for joint angles and CMJ analysis
  ([`815c9be`](https://github.com/feniix/kinemotion/commit/815c9be1019414acf61563312a5d58f6305a17a4))


## v0.18.1 (2025-11-10)

### Bug Fixes

- Ci build
  ([`f45e2c3`](https://github.com/feniix/kinemotion/commit/f45e2c3c11ae241d24de3e44836206e111defc2a))

### Refactoring

- **ci**: Use reusable workflow for docs deployment
  ([`013dbd1`](https://github.com/feniix/kinemotion/commit/013dbd112cd5bcbe69bc405066b39bb142996d46))


## v0.18.0 (2025-11-10)

### Bug Fixes

- **ci**: Pass SONAR_TOKEN to reusable test workflow
  ([`79919d0`](https://github.com/feniix/kinemotion/commit/79919d065e5db5d039deec899324c76fa9c11960))

### Features

- **ci**: Streamline testing and enforce quality gates before release
  ([`7b95bc5`](https://github.com/feniix/kinemotion/commit/7b95bc5890521bd10910c87024f77c32475a8fad))


## v0.17.6 (2025-11-10)

### Bug Fixes

- **ci**: Use unified SonarQube scan action
  ([`be20164`](https://github.com/feniix/kinemotion/commit/be20164339a545ff2256d38a8297281eb75ddfea))

### Performance Improvements

- **ci**: Enable uv dependency caching for faster builds
  ([`3a2e093`](https://github.com/feniix/kinemotion/commit/3a2e0932a34953bae8ae31b9a324eb2ca2450f57))


## v0.17.5 (2025-11-10)

### Bug Fixes

- **ci**: Correct SonarQube conditional syntax error
  ([`650762e`](https://github.com/feniix/kinemotion/commit/650762e33041d8cd3be692adac5e492453048036))


## v0.17.4 (2025-11-10)

### Bug Fixes

- **ci**: Make SonarQube scan conditional on token availability
  ([`bd62d7f`](https://github.com/feniix/kinemotion/commit/bd62d7f4d8f83a238093a1490be7316c1544ac25))


## v0.17.3 (2025-11-10)

### Bug Fixes

- **ci**: Skip multiprocessing tests in CI environment
  ([`af683eb`](https://github.com/feniix/kinemotion/commit/af683eb75994863e1cb0f7c30722086ae0084909))


## v0.17.2 (2025-11-10)

### Bug Fixes

- **ci**: Update package names for Ubuntu 24.04 compatibility
  ([`82568dc`](https://github.com/feniix/kinemotion/commit/82568dc5ff502a4308eadaf77a576f953516317c))


## v0.17.1 (2025-11-10)

### Bug Fixes

- **ci**: Add system dependencies for OpenCV and MediaPipe
  ([`bb48049`](https://github.com/feniix/kinemotion/commit/bb480498e04689c3deac443fdc162efe1c59e1e2))


## v0.17.0 (2025-11-10)

### Features

- **ci**: Add SonarQube Cloud integration for coverage reporting
  ([`cdc710f`](https://github.com/feniix/kinemotion/commit/cdc710f7a4c215e570eaa2b58a13f994ea7bae7c))


## v0.16.0 (2025-11-10)


## v0.15.3 (2025-11-10)

### Bug Fixes

- **dropjump**: Correct API imports in CLI module
  ([`b456d4c`](https://github.com/feniix/kinemotion/commit/b456d4c0a09234df70da3d67de0ed53c4fe55cfe))

### Documentation

- **development**: Add HYROX wall ball no-rep detection implementation plan
  ([`f38f5ae`](https://github.com/feniix/kinemotion/commit/f38f5ae21b2cb767fdf0156f193ce988d58fee7f))


## v0.15.2 (2025-11-07)

### Bug Fixes

- **docs**: Update documentation to match current auto-tuning API
  ([`a07b40d`](https://github.com/feniix/kinemotion/commit/a07b40d9057438912a44fc4eb5b9b3e6e34a6d56))


## v0.15.1 (2025-11-06)

### Bug Fixes

- **docs**: Update mkdocstrings references to renamed API functions
  ([`d410df3`](https://github.com/feniix/kinemotion/commit/d410df3fb6dd726ac607443371e375190521dae6))


## v0.15.0 (2025-11-06)

### Features

- Standardize drop jump API naming for consistency with CMJ
  ([`fcd92d0`](https://github.com/feniix/kinemotion/commit/fcd92d0802408d02dcb83a97816b491f92c36f28))

### Breaking Changes

- Users must update imports and function calls from process_video to process_dropjump_video,
  VideoConfig to DropJumpVideoConfig, and process_videos_bulk to process_dropjump_videos_bulk.


## v0.14.4 (2025-11-06)

### Bug Fixes

- **docs**: Make docs workflow depend on release workflow completion
  ([`a26fa34`](https://github.com/feniix/kinemotion/commit/a26fa349a55d3a3b264e0a71e214629e33c0f85c))


## v0.14.3 (2025-11-06)

### Bug Fixes

- **docs**: Enable GitHub Pages deployment on every push to main
  ([`2473ccb`](https://github.com/feniix/kinemotion/commit/2473ccb68f447ebc469f7835bd17720778864829))


## v0.14.2 (2025-11-06)

### Bug Fixes

- **docs**: Optimize Read the Docs build to avoid heavy dependencies
  ([`f46dd9d`](https://github.com/feniix/kinemotion/commit/f46dd9d36c9e5c9c173c01a49e9dadb047a385da))


## v0.14.1 (2025-11-06)

### Bug Fixes

- **docs**: Resolve Read the Docs build failure with Material theme
  ([`8c0b998`](https://github.com/feniix/kinemotion/commit/8c0b99876ab948300b0b9a773848c11474b23c03))


## v0.14.0 (2025-11-06)

### Features

- **docs**: Add MkDocs documentation with auto-generated API reference
  ([`cb5cd31`](https://github.com/feniix/kinemotion/commit/cb5cd313e43c6ba0c95c8e77b5651e7c86c73902))


## v0.13.0 (2025-11-06)

### Documentation

- Add sports biomechanics pose estimation research documentation
  ([`745d273`](https://github.com/feniix/kinemotion/commit/745d273da294d49dd83f8fe488f5ede38189361a))

- Update camera setup guides for 45° angle and dual iPhone configuration
  ([`373a858`](https://github.com/feniix/kinemotion/commit/373a858e81c74da6a85be8c00d7fc0c20ac42e85))

### Features

- **docs**: Reorganize documentation and add 45° camera setup guidance
  ([`0e8f992`](https://github.com/feniix/kinemotion/commit/0e8f992a7854a662b65574f589306bc13529cd5e))


## v0.12.3 (2025-11-06)

### Bug Fixes

- Resolve SonarCloud cognitive complexity violations
  ([`5b20c48`](https://github.com/feniix/kinemotion/commit/5b20c488e058ac3628b0e20847d3fe2539a687c4))

### Refactoring

- **core**: Reduce cognitive complexity in video_io and auto_tuning
  ([`14076fe`](https://github.com/feniix/kinemotion/commit/14076fe9d1f9b41ef2ff9bd643b17cf566e18654))

- **dropjump**: Add shared utility for foot position extraction
  ([`5222cc4`](https://github.com/feniix/kinemotion/commit/5222cc471b9f4406116de0b7fc193f07d21cd88a))

- **dropjump**: Reduce cognitive complexity in CLI functions
  ([`6fc887f`](https://github.com/feniix/kinemotion/commit/6fc887f6288e870a306aa1e3ffc7b8a46c21c3fc))

- **examples**: Simplify programmatic usage with shared utility
  ([`5e1bc19`](https://github.com/feniix/kinemotion/commit/5e1bc194f5784a24cfcbc7e6372ebd26a95225aa))


## v0.12.2 (2025-11-06)

### Bug Fixes

- **core**: Suppress false positive for polyorder parameter
  ([`ae5ffea`](https://github.com/feniix/kinemotion/commit/ae5ffea708741592e1cd356cdf35dcc388cbe97f))

- **dropjump**: Remove unused parameters from calculate_drop_jump_metrics
  ([`6130c11`](https://github.com/feniix/kinemotion/commit/6130c113be71dcd8c278b1f31a3b5e300a6b4532))

### Refactoring

- **core**: Reduce cognitive complexity in pose.py
  ([`f0a3805`](https://github.com/feniix/kinemotion/commit/f0a380561844e54b4372f57c93b82f8c8a1440ee))

- **dropjump**: Reduce cognitive complexity in analysis.py
  ([`180bb37`](https://github.com/feniix/kinemotion/commit/180bb373f63675ef6ecacaea8e9ee9f63c3d3746))

- **dropjump**: Reduce cognitive complexity in debug_overlay.py
  ([`076cb56`](https://github.com/feniix/kinemotion/commit/076cb560c55baaff0ba93d0631eb38d69f8a7d7b))


## v0.12.1 (2025-11-06)

### Bug Fixes

- **core**: Remove unreachable duplicate return statement
  ([`294115d`](https://github.com/feniix/kinemotion/commit/294115da761b2851ecc4405a6503138851a56ad1))

- **examples**: Remove drop_height from API examples
  ([`f3da09e`](https://github.com/feniix/kinemotion/commit/f3da09ef4ab050b13b80b9fdd8c7734e4556647a))

### Refactoring

- **dropjump**: Remove unused calibration parameters
  ([`1a7572c`](https://github.com/feniix/kinemotion/commit/1a7572c83ff4e990e39dcb96ff61220adf40818e))


## v0.12.0 (2025-11-06)

### Documentation

- Update claude.md
  ([`b4d93d9`](https://github.com/feniix/kinemotion/commit/b4d93d94259fbfe86101c256910fcfc07c8dfcc2))

### Features

- **dropjump**: Calculate jump height from flight time like CMJ
  ([`f7d96a2`](https://github.com/feniix/kinemotion/commit/f7d96a253b287d58215fd64bd1e598784cb098f4))

- **dropjump**: Improve landing detection with position stabilization
  ([`6d19938`](https://github.com/feniix/kinemotion/commit/6d199382485a80a975911c51444b2c18aa32c428))

### Refactoring

- **core**: Remove unused code and fix vulture warnings
  ([`16328e2`](https://github.com/feniix/kinemotion/commit/16328e299a0e15f7f0f0e87d133e1f662dc59d0b))

- **core**: Rename AutoTunedParams to AnalysisParameters for consistency
  ([`2b6e59b`](https://github.com/feniix/kinemotion/commit/2b6e59b832769224b600e23bf4141af5d6159169))

### Testing

- Update tests for kinematic-based height calculation
  ([`308469e`](https://github.com/feniix/kinemotion/commit/308469e978c53a971a4a20352cfffd72a3c9e6cd))


## v0.11.7 (2025-11-06)

### Bug Fixes

- Reduce code duplication to 2.73% with shared CLI decorators
  ([`4edbb50`](https://github.com/feniix/kinemotion/commit/4edbb50cec1e9e730a958e88aded53129f772649))

### Documentation

- Add code duplication guidelines to CLAUDE.md
  ([`5294842`](https://github.com/feniix/kinemotion/commit/529484241b236ad60d7dba693afd25e8f89b6a09))


## v0.11.6 (2025-11-06)

### Bug Fixes

- Reduce code duplication to 2.96%
  ([`12fab42`](https://github.com/feniix/kinemotion/commit/12fab420b47b874f08cc8012393521bd6e3e2c43))


## v0.11.5 (2025-11-06)

### Bug Fixes

- Deduplicate apply_expert_param_overrides across CLI modules
  ([`a475c6e`](https://github.com/feniix/kinemotion/commit/a475c6e52aaa3733fc60104df3f8760acc8990b2))

- Deduplicate print_auto_tuned_params across CLI modules
  ([`f084406`](https://github.com/feniix/kinemotion/commit/f084406d08318b87a91dcba0756938cb7cc50a4c))


## v0.11.4 (2025-11-06)

### Bug Fixes

- **api**: Remove countermovement_threshold from CMJVideoConfig and bulk processing
  ([`66ac915`](https://github.com/feniix/kinemotion/commit/66ac915810853b6c7aeca79f07f6470ef5da4041))


## v0.11.3 (2025-11-06)

### Bug Fixes

- Deduplicate CLI utilities across CMJ and drop jump modules
  ([`c314083`](https://github.com/feniix/kinemotion/commit/c314083dd6601071f75ded38864f7ba9a9daab3d))

- **cmj**: Remove unused countermovement_threshold parameter from process_cmj_video
  ([`a8d9425`](https://github.com/feniix/kinemotion/commit/a8d9425a509b44ccf5c9e983e2d8552e9b5f8839))


## v0.11.2 (2025-11-06)

### Bug Fixes

- **cmj**: Reduce cognitive complexity in _extract_positions_from_landmarks
  ([`9772df6`](https://github.com/feniix/kinemotion/commit/9772df69ca8fb2a46726614dd0adda3795cf0ad1))

- **cmj**: Reduce cognitive complexity in cmj_analyze CLI function
  ([`e9c7200`](https://github.com/feniix/kinemotion/commit/e9c720081df171d2b18150a5b370c4471fdf9b19))

- **cmj**: Reduce cognitive complexity in debug overlay rendering
  ([`11f35c4`](https://github.com/feniix/kinemotion/commit/11f35c4cf675301bccfef376e12c0ed06470e259))

- **cmj**: Remove unused variable and parameters in api and analysis
  ([`e8ef607`](https://github.com/feniix/kinemotion/commit/e8ef60735711f4c715d53049477362284efca433))


## v0.11.1 (2025-11-06)

### Bug Fixes

- **cmj**: Remove unused parameters and fix code quality issues
  ([`72a1e43`](https://github.com/feniix/kinemotion/commit/72a1e43ec107e5b1c132efb10a08a09ea2864ae4))


## v0.11.0 (2025-11-06)

### Documentation

- Add camera setup docs
  ([`84678d6`](https://github.com/feniix/kinemotion/commit/84678d60261a361c1dce51aec604491ab096f537))

### Features

- Add counter movement jump (CMJ) analysis with triple extension tracking
  ([`b6fc454`](https://github.com/feniix/kinemotion/commit/b6fc454482b20b11d82fadc51974a554562b60d3))


## v0.10.12 (2025-11-03)

### Bug Fixes

- Add sonar quality gate status
  ([`df66261`](https://github.com/feniix/kinemotion/commit/df662612916d511ee7c6ed63bc79d23b30154bc6))


## v0.10.11 (2025-11-03)

### Bug Fixes

- Correct PyPI badge and update type checker references
  ([`5a4aa38`](https://github.com/feniix/kinemotion/commit/5a4aa38972e59f176be1f520eef6cf4cc6b51156))


## v0.10.10 (2025-11-03)

### Bug Fixes

- **ci**: Include uv.lock in semantic release commits
  ([`8d87578`](https://github.com/feniix/kinemotion/commit/8d8757840e619490d1d27d23fe54a4d219c57bd0))


## v0.10.9 (2025-11-03)

### Bug Fixes

- **ci**: Update uv.lock during semantic release
  ([`9b7bc0b`](https://github.com/feniix/kinemotion/commit/9b7bc0b5115cd9493eed2b99778ed78fb26fdd34))

- **ci**: Update uv.lock during semantic release
  ([`30fb092`](https://github.com/feniix/kinemotion/commit/30fb092575295c2c672bf378a8d2794cc1fe35da))


## v0.10.8 (2025-11-03)

### Bug Fixes

- **cli**: Suppress S107 for Click CLI framework requirement
  ([`17c8335`](https://github.com/feniix/kinemotion/commit/17c83357334ca7d400fe41d802c9e5e61a995fff))


## v0.10.7 (2025-11-03)

### Bug Fixes

- **cli**: Reduce function parameter count using dataclasses
  ([`e86dbee`](https://github.com/feniix/kinemotion/commit/e86dbeef6677984b0cb256158c8e5ff3ad24b5fc))


## v0.10.6 (2025-11-03)

### Bug Fixes

- **cli**: Reduce cognitive complexity in _process_single and _process_batch
  ([`42434af`](https://github.com/feniix/kinemotion/commit/42434af3716afd841c80c118b6e1122846a685ed))


## v0.10.5 (2025-11-03)

### Bug Fixes

- **kinematics**: Reduce cognitive complexity in calculate_drop_jump_metrics
  ([`d6a06f3`](https://github.com/feniix/kinemotion/commit/d6a06f3671eb370a971c73c98270668d5aefe9b1))


## v0.10.4 (2025-11-03)

### Bug Fixes

- **api**: Reduce cognitive complexity in process_video function
  ([`d2e05cb`](https://github.com/feniix/kinemotion/commit/d2e05cb415067a1a1b081216a9474ccda1ae2567))


## v0.10.3 (2025-11-03)

### Bug Fixes

- Reduce function parameter count using dataclass
  ([`0b8abfd`](https://github.com/feniix/kinemotion/commit/0b8abfd6ee53835ba3d787924747ab5e46066395))


## v0.10.2 (2025-11-03)

### Bug Fixes

- Replace legacy numpy random functions with Generator API
  ([`5cfa31b`](https://github.com/feniix/kinemotion/commit/5cfa31bce040eadfc53d52654c2e75087ef087a5))


## v0.10.1 (2025-11-03)

### Bug Fixes

- Resolve SonarCloud code quality issues
  ([`73f7784`](https://github.com/feniix/kinemotion/commit/73f778491bc01bfed973421fe5261364f8540147))

### Build System

- Add style checker for commit messages
  ([`d25669b`](https://github.com/feniix/kinemotion/commit/d25669bdf17810a38a86fbd9b03e208ea14f5326))

- Migrate from mypy to pyright for type checking
  ([`521b526`](https://github.com/feniix/kinemotion/commit/521b52619553bb5b3ee61e0db4ff6fd06744ac7a))

### Documentation

- Install precommit hook for improving markdown
  ([`546164b`](https://github.com/feniix/kinemotion/commit/546164b9f68cf3222da9753fdd2f2cd272ead90f))

- Update documentation for batch processing and Python API
  ([`f0fa8b6`](https://github.com/feniix/kinemotion/commit/f0fa8b69b927ff4a2e7f15bac242374592fe0eb9))


## v0.10.0 (2025-11-02)

### Features

- Add batch processing mode to CLI
  ([`b0ab3c6`](https://github.com/feniix/kinemotion/commit/b0ab3c6b37a013402ff7a89305a68e49549eeae3))

## v0.9.0 (2025-11-02)

### Features

- Add programmatic API for bulk video processing
  ([`213de56`](https://github.com/feniix/kinemotion/commit/213de564fda96b461807dbefa2795e037a5edc94))

## v0.8.3 (2025-11-02)

### Bug Fixes

- Create new release
  ([`5f6322b`](https://github.com/feniix/kinemotion/commit/5f6322b6da24631f95f4e3036ed145e0d47b53a1))

### Documentation

- Update repository metadata for GHCR package description
  ([`4779355`](https://github.com/feniix/kinemotion/commit/4779355901a407514d83cf2aa82f55fa083e7e63))

## v0.8.2 (2025-11-02)

### Bug Fixes

- Add OCI annotations to Docker manifest for GHCR metadata
  ([`c6e2295`](https://github.com/feniix/kinemotion/commit/c6e2295dd5eb3eae6b820d3dc7a84d730772de41))

## v0.8.1 (2025-11-02)

### Bug Fixes

- Add OCI-compliant labels to Docker image
  ([`6b18b33`](https://github.com/feniix/kinemotion/commit/6b18b33538615048c8ea572c4ebc402160ee1c5e))

## v0.8.0 (2025-11-02)

### Features

- Add Docker support and GitHub Container Registry publishing
  ([`249ca4c`](https://github.com/feniix/kinemotion/commit/249ca4c0c0ab40cda5acfebac012db8075b9694f))

## v0.7.1 (2025-11-01)

### Bug Fixes

- Update documentation for auto-tuning system
  ([`6c1a135`](https://github.com/feniix/kinemotion/commit/6c1a135acf5cce7a627644dbc6393460277906ad))

## v0.7.0 (2025-11-01)

### Features

- Add intelligent auto-tuning and video rotation handling
  ([`7b35f67`](https://github.com/feniix/kinemotion/commit/7b35f6790dd8b6714f3e42389555107a043d486c))

## v0.6.4 (2025-10-26)

### Bug Fixes

- Project urls
  ([`c7b5914`](https://github.com/feniix/kinemotion/commit/c7b5914d3516e0f59dcf88ac81f99ffe94edb706))

## v0.6.3 (2025-10-26)

### Bug Fixes

- Changelog markdown
  ([`976de66`](https://github.com/feniix/kinemotion/commit/976de66b2a964b83240a559ea097cb74f5e1a537))

## v0.6.2 (2025-10-26)

### Bug Fixes

- Add semantic-release insertion flag to CHANGELOG.md
  ([`93f3a28`](https://github.com/feniix/kinemotion/commit/93f3a28c750bdb70b2a57f9b0c1910b105753980))

## \[Unreleased\]

### Added

- Your new feature here.

### Changed

- Your change here.

### Deprecated

- Your deprecated feature here.

### Removed

- Your removed feature here.

### Fixed

- Your bug fix here.

### Security

- Your security fix here.

## \[0.5.0\] - 2025-10-26

### Added

- Initial release of `kinemotion`.
