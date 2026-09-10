import cli


def test_cli_uses_main_by_default(monkeypatch):
    captured = {}

    def fake_run_checks(target):
        captured["target"] = target
        return []

    def fake_display_results(results, target):
        captured["results"] = results
        captured["display_target"] = target

    monkeypatch.setattr(cli, "run_checks", fake_run_checks)
    monkeypatch.setattr(cli, "display_results", fake_display_results)

    monkeypatch.setattr(
        "sys.argv",
        ["beforepush"],
    )

    cli.main()

    assert captured["target"] == "main"
    assert captured["display_target"] == "main"
    assert captured["results"] == []


def test_cli_accepts_custom_target(monkeypatch):
    captured = {}

    def fake_run_checks(target):
        captured["target"] = target
        return []

    def fake_display_results(results, target):
        captured["display_target"] = target

    monkeypatch.setattr(cli, "run_checks", fake_run_checks)
    monkeypatch.setattr(cli, "display_results", fake_display_results)

    monkeypatch.setattr(
        "sys.argv",
        ["beforepush", "--target", "develop"],
    )

    cli.main()

    assert captured["target"] == "develop"
    assert captured["display_target"] == "develop"