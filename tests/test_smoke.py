from budget_buckets import main


def test_main_prints_greeting(capsys):
    main()
    assert "budget-buckets" in capsys.readouterr().out
