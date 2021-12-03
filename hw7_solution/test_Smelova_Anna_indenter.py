from task_Smelova_Anna_indenter import Indenter


def test_default_indenter_output(capsys):
    with Indenter() as indent:
        indent.print("hi")
        with indent:
            indent.print("hello")
            with indent:
                indent.print("bonjour")
        indent.print("hey")

    expected_outcome = 'hi\n    hello\n        bonjour\nhey'

    captured = capsys.readouterr()
    assert expected_outcome in captured.out, (
        f'Wrong indenter default outcome',
        f'expected outcome is {expected_outcome}',
    )


def test_one_param_indenter_output(capsys):
    with Indenter(indent_str="--") as indent:
        indent.print("hi")
        with indent:
            indent.print("hello")
            with indent:
                indent.print("bonjour")
        indent.print("hey")

    expected_outcome = 'hi\n--hello\n----bonjour\nhey'

    captured = capsys.readouterr()
    assert expected_outcome in captured.out, (
        f'Wrong indenter one outcome',
        f'expected outcome is {expected_outcome}',
    )


def test_two_param_indenter_output(capsys):
    with Indenter(indent_str="--", indent_level=1) as indent:
        indent.print("hi")
        with indent:
            indent.print("hello")
            with indent:
                indent.print("bonjour")
        indent.print("hey")

    expected_outcome = '--hi\n----hello\n------bonjour\n--hey'

    captured = capsys.readouterr()
    assert expected_outcome in captured.out, (
        f'Wrong indenter two outcome',
        f'expected outcome is {expected_outcome}',
    )
