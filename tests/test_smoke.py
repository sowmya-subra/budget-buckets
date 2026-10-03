import pytest

from budget_buckets.cli import main


def test_cli_help_lists_commands(capsys):
    with pytest.raises(SystemExit):
        main(["--help"])
    out = capsys.readouterr().out
    assert "pull" in out
    assert "show" in out
