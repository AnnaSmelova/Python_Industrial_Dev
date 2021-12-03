from task_Smelova_Anna_repeater import verbose, repeater, verbose_context


def test_verbose_decorator_output(capsys):
    @verbose
    def hello(name):
        """Hello function"""
        print(f"*** Hello {name}! ***")
    hello('Vasya')

    expected_outcome = "before function call\n*** Hello Vasya! ***\nafter function call"

    captured = capsys.readouterr()
    assert expected_outcome in captured.out, (
        f'Wrong decorator outcome',
        f'expected outcome is {expected_outcome}',
    )


def test_verbose_decorator_function_name():
    @verbose
    def hello(name):
        """Hello function"""
        print(f"*** Hello {name}! ***")

    name = hello.__name__
    expected_name = 'hello'
    assert expected_name == name, (
        f'Wrong function name',
        f'expected name is: {expected_name}',
        f'got name: {name}'
    )


def test_verbose_decorator_function_docstring():
    @verbose
    def hello(name):
        """Hello function"""
        print(f"*** Hello {name}! ***")

    docstring = hello.__doc__
    expected_docstring = 'Hello function'
    assert expected_docstring == docstring, (
        f'Wrong function name',
        f'expected docstring is: {expected_docstring}',
        f'got docstring: {docstring}'
    )


def test_repeater_decorator_out(capsys):
    @repeater(3)
    def hello(name):
        """Hello function"""
        print(f"*** Hello {name}! ***")
    hello('Vasya')

    expected_outcome = "*** Hello Vasya! ***\n*** Hello Vasya! ***\n*** Hello Vasya! ***"

    captured = capsys.readouterr()
    assert expected_outcome in captured.out, (
        f'Wrong decorator outcome',
        f'expected outcome is {expected_outcome}',
    )


def test_repeater_decorator_function_name():
    @repeater(3)
    def hello(name):
        """Hello function"""
        print(f"*** Hello {name}! ***")

    name = hello.__name__
    expected_name = 'hello'
    assert expected_name == name, (
        f'Wrong function name',
        f'expected name is: {expected_name}',
        f'got name: {name}'
    )


def test_repeater_decorator_function_docstring():
    @repeater(3)
    def hello(name):
        """Hello function"""
        print(f"*** Hello {name}! ***")

    docstring = hello.__doc__
    expected_docstring = 'Hello function'
    assert expected_docstring == docstring, (
        f'Wrong function name',
        f'expected docstring is: {expected_docstring}',
        f'got docstring: {docstring}'
    )


def test_verbose_context_out(capsys):
    @verbose_context()
    def hello(name: str):
        """Hello function"""
        print(f"*** Hello {name}! ***")
    hello('Vasya')

    expected_outcome = "class: before function call\n*** Hello Vasya! ***\nclass: after function call"

    captured = capsys.readouterr()
    assert expected_outcome in captured.out, (
        f'Wrong decorator outcome',
        f'expected outcome is {expected_outcome}',
    )


def test_verbose_context_decorator_function_name():
    @verbose_context()
    def hello(name):
        """Hello function"""
        print(f"*** Hello {name}! ***")

    name = hello.__name__
    expected_name = 'hello'
    assert expected_name == name, (
        f'Wrong function name',
        f'expected name is: {expected_name}',
        f'got name: {name}'
    )


def test_verbose_context_decorator_function_docstring():
    @verbose_context()
    def hello(name):
        """Hello function"""
        print(f"*** Hello {name}! ***")

    docstring = hello.__doc__
    expected_docstring = 'Hello function'
    assert expected_docstring == docstring, (
        f'Wrong function name',
        f'expected docstring is: {expected_docstring}',
        f'got docstring: {docstring}'
    )


def test_all_decorators_output(capsys):
    @verbose
    @repeater(3)
    @verbose_context()
    def hello(name: str):
        """Hello function"""
        print(f"*** Hello {name}! ***")
    hello('Vasya')

    expected_outcome = 'before function call\nclass: before function call\n*** Hello Vasya! ***\nclass: ' \
                       'after function call\nclass: before function call\n*** Hello Vasya! ***\nclass: after ' \
                       'function call\nclass: before function call\n*** Hello Vasya! ***\nclass: after function ' \
                       'call\nafter function call'

    captured = capsys.readouterr()
    assert expected_outcome in captured.out, (
        f'Wrong all decorators outcome',
        f'expected outcome is {expected_outcome}',
    )


def test_all_decorators_function_name():
    @verbose
    @repeater(3)
    @verbose_context()
    def hello(name):
        """Hello function"""
        print(f"*** Hello {name}! ***")

    name = hello.__name__
    expected_name = 'hello'
    assert expected_name == name, (
        f'Wrong function name',
        f'expected name is: {expected_name}',
        f'got name: {name}'
    )


def test_all_decorators_function_docstring():
    @verbose
    @repeater(3)
    @verbose_context()
    def hello(name):
        """Hello function"""
        print(f"*** Hello {name}! ***")

    docstring = hello.__doc__
    expected_docstring = 'Hello function'
    assert expected_docstring == docstring, (
        f'Wrong function name',
        f'expected docstring is: {expected_docstring}',
        f'got docstring: {docstring}'
    )





