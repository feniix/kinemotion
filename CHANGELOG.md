# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!-- version list -->

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
