# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!-- version list -->

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
