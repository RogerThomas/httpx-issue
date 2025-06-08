#!/usr/bin/env python
import logging

import typer
from rich.logging import RichHandler

logger = logging.getLogger("Main")
app = typer.Typer(name="Project")


@app.callback(invoke_without_command=True)
def main(n: int) -> None:
    logger.info("n: %s", n)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s]: %(message)s",
        handlers=[RichHandler(show_time=False, show_level=False)],
    )
    app()
