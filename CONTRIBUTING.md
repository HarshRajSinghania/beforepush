# Contributing to BeforePush

Thanks for your interest in contributing to BeforePush!

BeforePush is an open-source CLI that checks Git branch readiness before pushing or opening a pull request. Contributions of all kinds are welcome, including bug fixes, improvements, tests, documentation, and new ideas.

## Getting Started

### Prerequisites

* Python 3.13 or later
* [uv](https://docs.astral.sh/uv/)
* Git

### Set Up the Project

Clone the repository:

```bash
git clone https://github.com/alibro005/beforepush.git
cd beforepush
```

Install the project dependencies:

```bash
uv sync
```

Run the test suite:

```bash
uv run pytest -v
```

Run BeforePush locally:

```bash
uv run beforepush
```

You can also test against a different target branch:

```bash
uv run beforepush --target develop
```

## Making Changes

Before starting work on a larger change, check the existing issues to see whether there is already an issue covering it.

For larger changes, open or comment on an issue first so the proposed approach can be discussed before implementation.

For smaller fixes, you can submit a pull request directly.

### Create a Branch

Create a branch from `main`:

```bash
git checkout main
git pull origin main
git checkout -b fix/short-description
```

Use a descriptive branch name. For example:

```text
feat/custom-target-validation
fix/detached-head-check
test/upstream-checks
docs/improve-installation
```

## Code Changes

Please keep changes focused and consistent with the existing project structure.

When adding or changing behavior:

* Add or update tests where appropriate.
* Keep functions small and focused.
* Avoid unnecessary dependencies.
* Preserve the existing CLI behavior unless the change intentionally modifies it.
* Keep terminal output clear and user-friendly.

## Testing

Run the complete test suite before opening a pull request:

```bash
uv run pytest -v
```

If you add new functionality or fix a bug, include tests that cover the relevant behavior when practical.

## Pull Requests

When opening a pull request:

* Use a clear and descriptive title.
* Explain what the change does.
* Explain why the change is needed.
* Reference the related issue when applicable.
* Keep the pull request focused on one change.
* Make sure the test suite passes.

A good pull request description should make it easy for a reviewer to understand the change without having to inspect every line of code.

## Commit Messages

Use clear, concise commit messages.

The project generally follows conventional commit-style prefixes:

```text
feat: add target branch validation
fix: handle detached HEAD state
test: add upstream branch checks
docs: improve installation instructions
refactor: simplify branch status checks
```

Keep commits focused and avoid mixing unrelated changes.

## Reporting Bugs

If you find a bug, please open a GitHub issue and include:

* What you expected to happen.
* What actually happened.
* Steps to reproduce the problem.
* Your Python version.
* Your operating system.
* Relevant terminal output or error messages.

Before opening a new issue, check whether the problem has already been reported.

## Suggesting Features

Feature suggestions are welcome.

When opening a feature request, explain:

* What problem the feature would solve.
* How you would expect it to work.
* Why it would be useful to BeforePush users.

For larger features, please discuss the proposed approach in an issue before starting implementation.

## Code of Conduct

Please be respectful and constructive when interacting with other contributors.

Harassment, personal attacks, and disrespectful behavior are not welcome. Keep discussions focused on the project and its technical goals.

## License

By contributing to BeforePush, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).

Thank you for contributing to BeforePush!
