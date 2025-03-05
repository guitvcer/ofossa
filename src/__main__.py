import typer


def main(name: str) -> None:
    print(f"Hello {name}")  # noqa: WPS421


if __name__ == "__main__":
    typer.run(main)
