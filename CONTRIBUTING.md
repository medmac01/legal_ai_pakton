# Contributing to PAKTON 🚀

Thank you for your interest in contributing to PAKTON! We welcome contributions from the community to help make contractual obligations clearer and more accessible to everyone.

## Table of Contents
- [Getting Started](#getting-started)
- [Project Setup](#project-setup)
- [Branch Structure](#branch-structure)
- [Contribution Workflow](#contribution-workflow)
- [Branch Naming Conventions](#branch-naming-conventions)
- [Pull Request Guidelines](#pull-request-guidelines)
- [Code Style and Standards](#code-style-and-standards)
- [Testing](#testing)
- [License](#license)

## Getting Started

Before contributing, please:
1. Read through this contributing guide
2. Review the [README.md](./README.md) to understand the project structure
3. Check existing [issues](https://github.com/your-repo/PAKTON/issues) and [discussions](https://github.com/your-repo/PAKTON/discussions)
4. Consider starting a discussion if you're planning a significant change

## Project Setup

PAKTON is organized into several components, each with its own setup instructions:

### Core Framework
- **[PAKTON Framework](./PAKTON%20Framework/README.md)** - Main multi-agent system implementation

### Experiments and Evaluation
- **[Frontend Development](./Experiments%20and%20Evaluation/Frontend/README.md)** - Web interface setup
- **[Qualitative Evaluation](./Experiments%20and%20Evaluation/Qualitative/README.md)** - Human and automated evaluation tools
- **[Quantitative Evaluation](./Experiments%20and%20Evaluation/Quantitative/README.md)** - Performance benchmarking tools

### Machine Learning Experimentation
- **[ML Experiments](./Machine%20Learning%20Experimentation/README.md)** - Additional ML research tools

**Important**: Please refer to the README.md file in each subdirectory for specific setup instructions, dependencies, and requirements.

## Branch Structure

We maintain two main branches:

- **`main`**: Production branch containing stable release versions
- **`develop`**: Development branch where all new features and fixes are integrated

**All pull requests must target the `develop` branch.**

## Contribution Workflow

1. **Fork the Repository**
   ```bash
   # Fork the repo on GitHub, then clone your fork
   git clone https://github.com/YOUR-USERNAME/PAKTON.git
   cd PAKTON
   
   # Add upstream remote
   git remote add upstream https://github.com/original-repo/PAKTON.git
   ```

2. **Create a Feature Branch**
   ```bash
   # Checkout develop and pull latest changes
   git checkout develop
   git pull upstream develop
   
   # Create your feature branch (see naming conventions below)
   git checkout -b feature/your-feature-name
   ```

3. **Make Your Changes**
   - Follow the setup instructions in the relevant subdirectory
   - Write clean, well-documented code
   - Add tests if applicable
   - Follow existing code style

4. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add your descriptive commit message"
   ```

5. **Push and Create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a pull request on GitHub targeting the `develop` branch.

## Branch Naming Conventions

Please use the following naming patterns for your branches:

- **New Features**: `feature/description-of-feature`
  - Example: `feature/multi-language-support`
  - Example: `feature/advanced-query-parsing`

- **Bug Fixes**: `fix/description-of-fix`
  - Example: `fix/memory-leak-in-agent`
  - Example: `fix/ui-rendering-issue`

- **Documentation**: `docs/description-of-docs`
  - Example: `docs/api-documentation`

- **Performance**: `perf/description-of-improvement`
  - Example: `perf/optimize-vector-search`

## Pull Request Guidelines

### Before Submitting

- [ ] Ensure your branch is up to date with `develop`
- [ ] Test your changes locally
- [ ] Follow the existing code style
- [ ] Update documentation if needed
- [ ] Add or update tests if applicable

### Pull Request Template

When creating a pull request, please include:

1. **Clear Title**: Use a descriptive title that summarizes the change
2. **Detailed Description**: 
   - What does this PR do?
   - Why is this change needed?
   - How does it work?
   - Any breaking changes?
3. **Issue References**: 
   - Link to related issues: `Closes #123` or `Fixes #456`
   - Reference relevant discussions
4. **Testing**: Describe how you tested your changes
5. **Screenshots**: Include screenshots for UI changes

### Example PR Description
```markdown
## Description
Adds support for processing multi-language legal documents in the PAKTON framework.

## Changes
- Added language detection to document preprocessing
- Implemented multi-language embeddings support
- Updated UI to display language-specific results
- Added tests for new language detection functionality

## Related Issues
Closes #45
Related discussion: #67

## Testing
- Tested with English, Spanish, and French documents
- All existing tests pass
- Added new test cases for language detection

## Screenshots
[Include relevant screenshots if UI changes]
```

### Review Process

1. **Automated Checks**: Ensure all CI checks pass
2. **Code Review**: Wait for maintainer review and address feedback
3. **Approval**: Once approved, your PR will be merged using **squash merge**
4. **Cleanup**: Delete your feature branch after merge

## Code Style and Standards

- Follow the existing code style in each component
- Use meaningful variable and function names
- Add comments for complex logic
- Keep functions small and focused
- Follow PEP 8 for Python code
- Use ESLint/Prettier for JavaScript/TypeScript code

## Testing

- Add tests for new functionality
- Ensure all existing tests pass
- Include both unit tests and integration tests where appropriate
- Test with different document types and sizes

## License

By contributing to PAKTON, you agree that your contributions will be licensed under the [Apache License 2.0](./LICENSE).

### Contributor License Agreement

By submitting a contribution to this project, you:

1. Certify that you have the right to submit the contribution under the Apache License 2.0
2. Agree that your contributions may be distributed under the Apache License 2.0
3. Understand that this project and your contributions are public
4. Warrant that your contributions do not violate any third-party rights

## Questions?

- 💬 Start a [Discussion](https://github.com/your-repo/PAKTON/discussions) for general questions
- 🐛 Open an [Issue](https://github.com/your-repo/PAKTON/issues) for bugs or feature requests
- 📧 Contact the maintainers for sensitive matters

---

Thank you for contributing to PAKTON! Together, we're making legal documents more accessible and understandable for everyone. 🎉