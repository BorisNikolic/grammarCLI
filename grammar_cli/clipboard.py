import pyperclip


def read_clipboard() -> str:
    return pyperclip.paste()


def write_clipboard(text: str) -> None:
    pyperclip.copy(text)
