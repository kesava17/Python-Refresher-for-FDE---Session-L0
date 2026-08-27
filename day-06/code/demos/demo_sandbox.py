"""Sandboxing untrusted code (security): exec shares all; a subprocess contains it.

The concept, in plain words:
    Sometimes you run code you did not write: a user formula, a plugin, an AI-generated
    snippet. The wrong way is exec() (or eval), because that runs inside YOUR process.
    It shares your variables, your imported modules, and your environment, so the
    snippet can read a secret sitting in os.environ, or reach into anything else the
    process holds. There is no real boundary. The safer way is to run it in a separate
    process you control: a subprocess with a cleaned environment (the secret is simply
    not passed to the child) and a timeout (so a snippet that loops forever is killed
    instead of hanging you). The operating system enforces the boundary that exec never
    had.

    A real sandbox goes further (locked-down containers, seccomp, no network), but the
    core idea is here: do not run untrusted code in your own process, and control what
    the child can see and how long it may run.

Why a fresher should care:
    "Just exec the user's expression" is a direct path to handing over every secret in
    the process. Moving untrusted code into a contained child, with nothing sensitive in
    its environment and a time limit, is the difference between a feature and a breach.

What this demo shows:
    The same untrusted snippet (which tries to read a secret from the environment) run
    two ways. In-process exec reads the secret, because it shares this process. In a
    subprocess with the secret removed from the child environment and a timeout set, the
    snippet sees nothing, so it is contained.

Run:  poetry run python demo_sandbox.py
"""

from __future__ import annotations

import os
import subprocess
import sys

# The untrusted snippet. All it does here is try to read a secret from the
# environment and report what it found. A real attacker's snippet would do more.
UNTRUSTED_SNIPPET = (
    "import os\n"
    "print('snippet sees secret:', os.environ.get('APP_SECRET'))\n"
)


def run_inprocess_exec(secret_name: str) -> None:
    """UNSAFE: exec runs in THIS process, so it can read our secret directly."""
    os.environ[secret_name] = "s3cr3t-demo-value"
    # exec shares this process: globals, imports, and os.environ are all reachable.
    exec(UNTRUSTED_SNIPPET, {})


def run_subprocess_contained(secret_name: str) -> None:
    """SAFE: a separate process with the secret stripped and a timeout."""
    # Copy the environment, then remove the secret so the child never receives it.
    child_env = dict(os.environ)
    child_env.pop(secret_name, None)
    try:
        result = subprocess.run(
            [sys.executable, "-c", UNTRUSTED_SNIPPET],
            env=child_env,  # cleaned: no secret in here
            capture_output=True,
            text=True,
            timeout=5,  # a runaway snippet is killed, not left to hang us
            check=True,
        )
        print(result.stdout.strip())
    except subprocess.TimeoutExpired:
        print("snippet exceeded its time limit and was killed")


def main() -> None:
    secret_name = "APP_SECRET"

    print("in-process exec (shares this process):")
    run_inprocess_exec(secret_name)
    print("  the secret leaked, because exec has no boundary\n")

    print("contained subprocess (cleaned env + timeout):")
    run_subprocess_contained(secret_name)
    print("  the child never received the secret, so it reads None")


if __name__ == "__main__":
    main()
