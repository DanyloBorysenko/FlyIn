from src.parser.errors import ParserError


def main():
    try:
        raise ParserError("msg", 1)
    except ParserError as e:
        print(e)


if __name__ == "__main__":
    main()
