"""Run the same project checks locally and in CI."""

from pathlib import Path
import subprocess
import sys
from tempfile import gettempdir
from uuid import uuid4


PYTEST_BASETEMP = (
    Path(gettempdir())
    / f"biotrace-pytest-{uuid4()}"
)


COMMANDS = [
    [
        sys.executable,
        "-m",
        "pip",
        "check",
    ],
    [
        sys.executable,
        "-m",
        "pytest",
        "--basetemp",
        str(PYTEST_BASETEMP),
        "-p",
        "no:cacheprovider",
    ],
    [
        sys.executable,
        "-m",
        "compileall",
        "-q",
        "app",
        "src",
        "scripts",
    ],
]


def main() -> None:
    for command in COMMANDS:
        printable = " ".join(
            command
        )

        print(
            "\n"
            + "=" * 72
        )

        print(
            f"Running: {printable}"
        )

        print(
            "=" * 72
        )

        subprocess.run(
            command,
            check=True,
        )

    print(
        "\nAll BioTrace "
        "verification checks passed."
    )


if __name__ == "__main__":
    main()
