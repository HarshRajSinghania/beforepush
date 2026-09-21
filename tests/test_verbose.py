import subprocess

import cli
from checks import CheckResult, CheckStatus, check_working_tree
import git


def test_cli_verbose_long_flag(monkeypatch):
    captured = {}

    def fake_run_checks(target, **kwargs):
        captured["verbose"] = kwargs.get("verbose")
        return [
            CheckResult(
                "Git repository",
                CheckStatus.PASS,
                "ok",
                details=["Repository: /tmp"],
            ),
        ]

    def fake_display_results(results, target, **kwargs):
        captured["display_verbose"] = kwargs.get("verbose")
        captured["details"] = results[0].details

    monkeypatch.setattr(cli, "run_checks", fake_run_checks)
    monkeypatch.setattr(cli, "display_results", fake_display_results)
    monkeypatch.setattr("sys.argv", ["beforepush", "--verbose"])

    assert cli.main() == 0
    assert captured["verbose"] is True
    assert captured["display_verbose"] is True
    assert captured["details"] == ["Repository: /tmp"]


def test_cli_verbose_short_flag(monkeypatch):
    captured = {}

    def fake_run_checks(target, **kwargs):
        captured["verbose"] = kwargs.get("verbose")
        return []

    monkeypatch.setattr(cli, "run_checks", fake_run_checks)
    monkeypatch.setattr(cli, "display_results", lambda *a, **k: None)
    monkeypatch.setattr("sys.argv", ["beforepush", "-v"])

    assert cli.main() == 0
    assert captured["verbose"] is True


def test_cli_verbose_does_not_change_exit_code(monkeypatch):
    monkeypatch.setattr(
        cli,
        "run_checks",
        lambda target, **kwargs: [
            CheckResult("Example", CheckStatus.FAIL, "Failed.", details=["why"]),
        ],
    )
    monkeypatch.setattr(cli, "display_results", lambda *a, **k: None)
    monkeypatch.setattr("sys.argv", ["beforepush", "--verbose"])

    assert cli.main() == 1


def test_working_tree_verbose_lists_changed_files(monkeypatch):
    monkeypatch.setattr(git, "has_changes", lambda: True)
    monkeypatch.setattr(git, "get_status", lambda: " M src/cli.py\n?? scratch.txt")

    result = check_working_tree(verbose=True)

    assert result.status == CheckStatus.FAIL
    joined = "\n".join(result.details)
    assert "src/cli.py" in joined
    assert "scratch.txt" in joined


def test_working_tree_default_has_no_details(monkeypatch):
    monkeypatch.setattr(git, "has_changes", lambda: True)
    monkeypatch.setattr(git, "get_status", lambda: " M src/cli.py")

    result = check_working_tree()

    assert result.status == CheckStatus.FAIL
    assert result.details == []


def test_cli_verbose_output_includes_diagnostics(tmp_path, monkeypatch, capsys):
    subprocess.run(
        ["git", "init", "--initial-branch", "main", str(tmp_path)],
        check=True,
        capture_output=True,
    )
    monkeypatch.chdir(tmp_path)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Test User",
            "-c",
            "user.email=test@example.com",
            "-c",
            "commit.gpgsign=false",
            "commit",
            "--allow-empty",
            "-m",
            "Initial commit",
        ],
        check=True,
        capture_output=True,
    )
    monkeypatch.setattr("sys.argv", ["beforepush", "--verbose"])

    assert cli.main() == 0
    output = capsys.readouterr().out
    assert "Verbose diagnostics enabled" in output
    assert "Repository:" in output
    assert "HEAD:" in output
    assert "Working tree is clean." in output


def test_cli_default_output_omits_verbose_header(tmp_path, monkeypatch, capsys):
    subprocess.run(
        ["git", "init", "--initial-branch", "main", str(tmp_path)],
        check=True,
        capture_output=True,
    )
    monkeypatch.chdir(tmp_path)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Test User",
            "-c",
            "user.email=test@example.com",
            "-c",
            "commit.gpgsign=false",
            "commit",
            "--allow-empty",
            "-m",
            "Initial commit",
        ],
        check=True,
        capture_output=True,
    )
    monkeypatch.setattr("sys.argv", ["beforepush"])

    assert cli.main() == 0
    output = capsys.readouterr().out
    assert "Verbose diagnostics enabled" not in output
    assert "Repository:" not in output
