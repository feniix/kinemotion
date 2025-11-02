# Security Policy

## Project Status

**Kinemotion is pre-1.0 software under active development.**

As stated in the [README](README.md), this tool's accuracy has **not been validated** against gold standard measurements. It is experimental software intended for:

- Personal experiments and research
- Tracking relative changes over time
- Exploratory analysis

This is **not production-ready software** and should not be used in security-critical, safety-critical, or clinical contexts.

## Reporting Security Issues

If you discover a security vulnerability, please report it by:

1. **Opening a GitHub issue** with details about the vulnerability
1. Using the label "security" if available

For now, we handle security reports the same as other bug reports. When the project reaches version 1.0, we will implement a more formal security disclosure process.

## Security Considerations

As with any tool that processes video files:

- **Only process videos from trusted sources** - video codec vulnerabilities could be exploited by malicious files
- **Run in isolated environments** if processing untrusted content
- **Keep dependencies updated** - especially OpenCV and MediaPipe which handle video processing

## Roadmap

When Kinemotion reaches version 1.0, this security policy will be expanded to include:

- Supported versions and patch policy
- Private vulnerability disclosure process
- Response timelines and severity classifications
- Coordinated disclosure procedures

## Questions?

For questions about security, open a GitHub issue or contact the maintainers through the repository.

Thank you for helping improve Kinemotion!
