class ParserError(Exception):
    """Raised when a map file cannot be parsed or validated."""
    def __init__(self, msg: str, line_ind: int | None = None) -> None:
        """
        Initialize a parser error.

        Args:
            msg: Description of the parsing error.
            line_ind: Line number where the error occurred, if available.
        """
        super().__init__(msg)
        self.msg = msg
        self.line_ind = line_ind

    def __str__(self) -> str:
        """Return a human-readable representation of the error."""
        if self.line_ind is None:
            return self.msg
        return f"Line {self.line_ind}: {self.msg}"
