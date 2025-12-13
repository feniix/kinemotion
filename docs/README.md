# Kinemotion Documentation

Welcome to the kinemotion documentation. This directory contains guides, technical documentation, and research for video-based kinematic analysis of athletic jumps.

## Quick Navigation

### 🚀 Getting Started

- **[Camera Setup Guide](guides/camera-setup.md)** - How to position your camera for optimal analysis
  - Single iPhone at 45° (standard setup)
  - Dual iPhone stereo (advanced setup)
  - [Versión en Español](translations/es/camera-setup.md)

### 📖 User Guides

- **[CMJ Guide](guides/cmj-guide.md)** - Counter-movement jump analysis guide
- **[Bulk Processing](guides/bulk-processing.md)** - Processing multiple videos efficiently
- **[Parameters Reference](reference/parameters.md)** - CLI parameters and options

### 📊 Reference

- **[Pose Systems Quick Reference](reference/pose-systems.md)** - Comparison of pose estimation systems
- **[Parameters](reference/parameters.md)** - Complete CLI parameter documentation

### 🔬 Research & Validation

- **[⚠️ Validation Status](validation-status.md)** - **READ FIRST** - Current validation status, limitations, and appropriate use cases
- **[Sports Biomechanics Pose Estimation](research/sports-biomechanics-pose-estimation.md)** - Comprehensive research analysis on pose detection systems for sports biomechanics
  - Pose2Sim validation (3-4° accuracy)
  - Stereo MediaPipe validation (30.1mm RMSE)
  - AthletePose3D dataset
  - System comparisons and recommendations

### ⚙️ Technical Documentation

- **[Triple Extension](technical/triple-extension.md)** - Biomechanics of triple extension in jumps
- **[Framerate](technical/framerate.md)** - Frame rate considerations for analysis
- **[IMU Metadata](technical/imu-metadata.md)** - Video metadata preservation
- **[Real-Time Analysis](technical/real-time-analysis.md)** - Future real-time processing capabilities

### 👨‍💻 Development

- **[Coach Feedback System Setup](development/feedback-system-setup.md)** - Supabase database integration for coach feedback and analysis sessions
- **[Feature Request System](development/feature-request-system.md)** - Frontend feedback and feature request system configuration
- **[Validation Roadmap](development/validation-roadmap.md)** - 3-month validation plan (no lab equipment required)
- **[Validation Plan](development/validation-plan.md)** - Testing and validation strategy
- **[Errors & Findings](development/errors-findings.md)** - Known issues and debugging information
- **[Wall Ball No-Rep Detection](development/wallball-norep-detection.md)** - Future feature implementation plan for HYROX wall ball analysis

### 🌍 Translations

- **[Español (Spanish)](translations/es/)**
  - [Guía de Configuración de Cámara](translations/es/camera-setup.md)

______________________________________________________________________

## Documentation Organization

This documentation follows a structured organization:

- **guides/** - User-facing how-to guides for setup and usage
- **reference/** - Quick lookup reference materials
- **technical/** - Implementation details and technical explanations
- **research/** - Academic research and validation studies
- **development/** - Developer and contributor resources
- **translations/** - Non-English documentation

## Quick Links by Audience

### For Athletes & Coaches

Start here:

1. [Camera Setup Guide](guides/camera-setup.md) - Critical first step
1. [CMJ Guide](guides/cmj-guide.md) - Understanding CMJ analysis
1. [Parameters Reference](reference/parameters.md) - Adjusting analysis settings

### For Researchers

#### ⚠️ IMPORTANT: Read validation status first before using in research

1. [**Validation Status**](validation-status.md) - **READ FIRST** - Limitations and appropriate use

1. [Sports Biomechanics Pose Estimation](research/sports-biomechanics-pose-estimation.md) - Research analysis

1. [Pose Systems Quick Reference](reference/pose-systems.md) - System comparisons

1. [Validation Roadmap](development/validation-roadmap.md) - Planned validation activities

### For Developers

1. [Triple Extension](technical/triple-extension.md) - Biomechanics implementation
1. [IMU Metadata](technical/imu-metadata.md) - Video processing details
1. [Validation Plan](development/validation-plan.md) - Testing strategy
1. Main [CLAUDE.md](../CLAUDE.md) - Complete project documentation

______________________________________________________________________

## Contributing to Documentation

When adding new documentation:

- **User guides** → `guides/` (how-to content)
- **Reference materials** → `reference/` (quick lookups, parameters, specs)
- **Technical details** → `technical/` (implementation, algorithms, biomechanics)
- **Research** → `research/` (validation studies, academic content)
- **Development** → `development/` (testing, debugging, contributor info)
- **Translations** → `translations/{language-code}/`

Ensure cross-references use relative paths and follow conventional commits format when committing changes.

______________________________________________________________________

**Last Updated:** November 7, 2025
