from src.parser.errors import ParserError


class A:
    tools = []


def main():
    x = A()
    y = A()
    x.tools.append("Hi")
    print(y.tools)


if __name__ == "__main__":
    main()
