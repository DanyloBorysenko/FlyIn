def main():
    try:
        i: int = int("dfsd")
    except ValueError as e:
        raise RuntimeError(f"{e}")
    print(i)


if __name__ == "__main__":
    main()
