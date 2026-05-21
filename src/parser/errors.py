class ParserError(Exception):
    def __init__(self, msg: str, line_ind: int | None = None) -> None:
        super().__init__(msg)
        self.msg = msg
        self.line_ind = line_ind

    def __str__(self) -> str:
        if self.line_ind is None:
            return self.msg
        return f"Line {self.line_ind}: {self.msg}"
