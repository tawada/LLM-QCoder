"""Contains functions to verify the code."""


def is_compilable(code: str) -> bool:
    """
    Checks if the code is compilable or not.
    :param code: The code to check.
    :return: True if the code is compilable, False otherwise.
    """
    try:
        compile(code, '<string>', 'exec')
    except SyntaxError:
        return False
    return True
