"""Run the same project checks locally and in CI."""

import subprocess
import sys


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