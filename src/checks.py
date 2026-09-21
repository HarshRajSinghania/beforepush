from dataclasses import dataclass, field
from enum import Enum

import git


class CheckStatus(Enum):
    PASS = "pass"
    WARNING = "warning"
    FAIL = "fail"


@dataclass
class CheckResult:
    name: str
    status: CheckStatus
    message: str
    details: list[str] = field(default_factory=list)


def _safe_detail(label: str, getter) -> str | None:
    """Return a labeled diagnostic line, or None if the Git call fails."""
    try:
        value = getter()
    except RuntimeError as error:
        message = str(error).strip()
        if message:
            return f"{label}: unavailable ({message})"
        return f"{label}: unavailable"
    if not value:
        return f"{label}: (none)"
    return f"{label}: {value}"


def _repository_details() -> list[str]:
    details: list[str] = []
    for label, getter in (
        ("Repository", git.get_repo_root),
        ("HEAD", git.get_head_sha),
        ("Remotes", git.get_remote_summary),
    ):
        line = _safe_detail(label, getter)
        if line is not None:
            details.append(line)
    return details


def check_git_repository(*, verbose: bool = False) -> CheckResult:
    """Check whether the current directory is a Git repository."""
    if git.is_git_repository():
        details = _repository_details() if verbose else []
        return CheckResult(
            name="Git repository",
            status=CheckStatus.PASS,
            message="Current directory is a Git repository.",
            details=details,
        )

    details = []
    if verbose:
        details.append("git rev-parse --is-inside-work-tree did not report a work tree.")
    return CheckResult(
        name="Git repository",
        status=CheckStatus.FAIL,
        message="Current directory is not a Git repository.",
        details=details,
    )


def check_current_branch(*, verbose: bool = False) -> CheckResult:
    """Check whether a branch is currently checked out."""
    try:
        branch = git.get_current_branch()
    except RuntimeError as error:
        details = [f"git branch --show-current failed: {error}"] if verbose else []
        return CheckResult(
            name="Current branch",
            status=CheckStatus.FAIL,
            message="Could not determine the current branch.",
            details=details,
        )

    if branch:
        details = []
        if verbose:
            details.append(f"Branch: {branch}")
            head = _safe_detail("HEAD", git.get_head_sha)
            if head:
                details.append(head)
        return CheckResult(
            name="Current branch",
            status=CheckStatus.PASS,
            message=f"Currently on '{branch}'.",
            details=details,
        )

    details = []
    if verbose:
        details.append("git branch --show-current returned an empty branch name (detached HEAD?).")
        head = _safe_detail("HEAD", git.get_head_sha)
        if head:
            details.append(head)
    return CheckResult(
        name="Current branch",
        status=CheckStatus.FAIL,
        message="No branch is currently checked out.",
        details=details,
    )


def check_working_tree(*, verbose: bool = False) -> CheckResult:
    """Check whether the working tree is clean."""
    try:
        has_changes = git.has_changes()
        status = git.get_status() if verbose else ""
    except RuntimeError as error:
        details = [f"git status --porcelain failed: {error}"] if verbose else []
        return CheckResult(
            name="Working tree",
            status=CheckStatus.FAIL,
            message="Could not read the Git working tree.",
            details=details,
        )

    if not has_changes:
        details = ["Working tree status: clean"] if verbose else []
        return CheckResult(
            name="Working tree",
            status=CheckStatus.PASS,
            message="Working tree is clean.",
            details=details,
        )

    details = []
    if verbose:
        details.append("Changed files (git status --porcelain):")
        details.extend(status.splitlines() or ["(status unavailable)"])
    return CheckResult(
        name="Working tree",
        status=CheckStatus.FAIL,
        message="Uncommitted or untracked changes detected.",
        details=details,
    )


def check_upstream_branch(*, verbose: bool = False) -> CheckResult:
    """Check whether the current branch has an upstream branch."""
    try:
        upstream = git.get_upstream_branch()
    except RuntimeError as error:
        details = []
        if verbose:
            details.append("No upstream is configured for the current branch.")
            if str(error).strip():
                details.append(f"git rev-parse @{{u}}: {error}")
            remotes = _safe_detail("Remotes", git.get_remote_summary)
            if remotes:
                details.append(remotes)
        return CheckResult(
            name="Upstream branch",
            status=CheckStatus.WARNING,
            message="No upstream branch configured.",
            details=details,
        )

    details = [f"Upstream: {upstream}"] if verbose else []
    return CheckResult(
        name="Upstream branch",
        status=CheckStatus.PASS,
        message=f"Tracking '{upstream}'.",
        details=details,
    )


def check_target_branch(target: str, *, verbose: bool = False) -> CheckResult:
    """Check whether the current branch is behind the target branch."""
    try:
        current_branch = git.get_current_branch()

        if current_branch == target:
            details = [f"Current branch matches target '{target}'."] if verbose else []
            return CheckResult(
                name="Target branch",
                status=CheckStatus.PASS,
                message=f"Currently on target branch '{target}'.",
                details=details,
            )

        if not git.branch_exists(target):
            details = []
            if verbose:
                details.append(f"git rev-parse could not resolve '{target}' to a commit.")
            return CheckResult(
                name="Target branch",
                status=CheckStatus.FAIL,
                message=f"Target branch '{target}' does not exist.",
                details=details,
            )

        behind = git.get_behind_count(target)

    except RuntimeError as error:
        details = [f"Comparison with '{target}' failed: {error}"] if verbose else []
        return CheckResult(
            name="Target branch",
            status=CheckStatus.FAIL,
            message=f"Could not compare with '{target}'.",
            details=details,
        )

    if behind == 0:
        details = [f"HEAD..{target} commit count: 0"] if verbose else []
        return CheckResult(
            name="Target branch",
            status=CheckStatus.PASS,
            message=f"Branch is up to date with {target}.",
            details=details,
        )
    commit_word = "commit" if behind == 1 else "commits"
    details = [f"HEAD..{target} commit count: {behind}"] if verbose else []
    return CheckResult(
        name="Target branch",
        status=CheckStatus.FAIL,
        message=f"Branch is {behind} {commit_word} behind {target}. "
        f"Update your branch before opening a PR.",
        details=details,
    )


def run_checks(target: str, *, verbose: bool = False) -> list[CheckResult]:
    """Run all repository readiness checks."""
    repository = check_git_repository(verbose=verbose)
    if repository.status == CheckStatus.PASS and not git.branch_exists("HEAD"):
        details = []
        if verbose:
            details.append("HEAD does not resolve to a commit yet.")
        return [
            repository,
            CheckResult(
                name="Commit history",
                status=CheckStatus.FAIL,
                message="Current branch has no commits to check. "
                "Create a commit before checking readiness.",
                details=details,
            ),
        ]

    return [
        repository,
        check_current_branch(verbose=verbose),
        check_working_tree(verbose=verbose),
        check_upstream_branch(verbose=verbose),
        check_target_branch(target, verbose=verbose),
    ]
