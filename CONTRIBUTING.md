# Contributing to Bearcats Racing Discord Bot

Thank you for your interest in contributing to the Bearcats Racing Discord Bot! This guide will help you get started with contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/bearcats-racing-bot.git`
3. Create a new branch: `git checkout -b feature/your-feature-name`
4. Install dependencies: `pip install -r requirements.txt`
5. Set up your environment variables (see `.env.example`)

## Development Guidelines

### Code Style
- Follow PEP 8 guidelines for Python code
- Use type hints for function parameters and return values
- Document functions and classes with docstrings
- Keep functions focused and single-purpose

### Testing
- Write tests for new features
- Ensure existing tests pass
- Test edge cases and error conditions
- Document test cases in the test files

### Pull Requests
1. Keep PRs focused on a single feature or bug fix
2. Write clear, descriptive commit messages
3. Update documentation as needed
4. Include tests for new features
5. Ensure all tests pass before submitting

## Feature Development

### Adding New Commands
1. Create a new command function in `backend/app.py`
2. Add command documentation to `readme.md`
3. Update the command table in the documentation
4. Add tests for the new command

### Modifying Existing Features
1. Document the changes in your PR
2. Update relevant documentation
3. Ensure backward compatibility
4. Add tests for modified functionality

## Documentation

### Updating Documentation
- Keep `readme.md` up to date with new features
- Document API changes
- Update environment variable requirements
- Add examples for new features

## Issue Reporting

When reporting issues:
1. Use the issue template
2. Provide steps to reproduce
3. Include error messages
4. Specify your environment details

## Code Review Process

1. PRs will be reviewed by maintainers
2. Address review comments promptly
3. Keep the PR up to date with the main branch
4. Squash commits before merging

## Questions?

Feel free to open an issue or contact the maintainers with any questions about contributing to the project.
