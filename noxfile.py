#!/usr/bin/env python
"""This file is a Python file that defines a set of sessions."""

# pylint: disable=C0103

import nox
import nox.sessions

# Package name
package_name: str = "server_manager_agent"
# Python version for environments
python_version: list[str] = ["3.14"]

# region NOX
# Minimum nox required
nox.needs_version = "==2026.4.10"
# Sessions default backend
nox.options.default_venv_backend = "venv"
# Set an empty list of default sessions to run
# This way, all sessions will not execute on accidental nox calling
nox.options.sessions = []
# endregion NOX

# region PIP
# Constraint command for pip
constraint: str = "--constraint=.github/workflows/constraints.txt"
# Pip install command
pip_install: list[str] = ["pip", "install"]
# endregion PIP

# region MYPY
# MyPy default options and check locations
mypy_commands: list[str] = [
    "--install-types",
    "--non-interactive",
    "src",
    "tests",
]
# MyPy requirements
mypy_requirements: list[str] = ["mypy", "pytest"]
# endregion MYPY

# region PYTEST
# Pytest requirements
pytest_requirements: list[str] = [
    "pytest",
    "coverage",
    "pytest-asyncio",
    "pytest-codspeed",
]
# Benchmark commands
benchmark_commands: list[str] = ["pytest", "tests/", "--codspeed", "-rA"]
# endregion PYTEST

# region PRE-COMMIT
pre_commit_requirements: list[str] = [
    "pre-commit",
]
pre_commit_commands: list[str] = [
    "pre-commit",
    "run",
    "--all-files",
    "--show-diff-on-failure",
]
# endregion PRE-COMMIT


@nox.session(name="ruff-check", python=python_version, tags=["check"])
def ruff_check(session: nox.sessions.Session) -> None:
    """Check the code with Ruff.

    Args:
        session (nox.session.Session): An environment and a set of commands to run.
    """
    # Install requirements
    session.run(*pip_install, constraint, "ruff", silent=True)
    # If argument is provided, append to command to fix errors
    if session.posargs:
        # Join the characters of input argument into a single string
        argument: str = "".join(session.posargs)
        session.run("ruff", "check", argument)
    else:
        # Else, run checks
        session.run("ruff", "check")


@nox.session(name="mypy-type", python=python_version, tags=["type"])
def mypy_type(session: nox.sessions.Session) -> None:
    """Type check using MyPy.

    Args:
        session (nox.sessions.Session): An environment and a set of commands to run.
    """
    # Install the package
    session.install(".", silent=True)
    # Install requirements
    session.run(*pip_install, constraint, *mypy_requirements, silent=True)
    # Run MyPy type checking
    session.run("mypy", *mypy_commands)


@nox.session(python=python_version, tags=["test"])
def test(session: nox.sessions.Session) -> None:
    """Runs the test suite and generates coverage data.

    Args:
        session (nox.sessions.Session): An environment and a set of commands to run.
    """
    # Install the package
    session.install(".", silent=True)
    # Install requirements
    session.run(*pip_install, constraint, *pytest_requirements, silent=True)
    # Run tests
    session.run("coverage", "run", "--parallel", "-m", "pytest", "-rF")


@nox.session(python=python_version, tags=["coverage"])
def coverage(session: nox.sessions.Session) -> None:
    """Produce coverage report.

    Args:
        session (nox.sessions.Session): An environment and a set of commands to run.
    """
    # Install requirements
    session.run(*pip_install, constraint, "coverage", silent=True)
    # Combine coverage data
    session.run("coverage", "combine")
    # Report the combined data
    session.run("coverage", "report")
    # Write coverage data to a “coverage.xml” file
    session.run("coverage", "xml")


@nox.session(
    name="test-and-coverage",
    python=python_version,
    tags=["test-and-coverage"],
    requires=["test"],
)
def test_and_coverage(session: nox.sessions.Session) -> None:
    """Run the test suit and produce coverage report.

    Args:
        session (nox.sessions.Session): An environment and a set of commands to run.
    """
    # Run the coverage session, after testing session
    session.notify("coverage")


@nox.session(python=python_version, tags=["benchmark"])
def benchmark(session: nox.sessions.Session) -> None:
    """Runs the benchmarks.

    Args:
        session (nox.sessions.Session): An environment and a set of commands to run.
    """
    # Install the package
    session.install(".", silent=True)
    # Install requirements
    session.run(*pip_install, constraint, *pytest_requirements, silent=True)
    # Run pytest for codspeed
    session.run(*benchmark_commands)


@nox.session(name="pre-commit", python=python_version, tags=["pre-commit"])
def pre_commit(session: nox.sessions.Session) -> None:
    """Runs pre-commit hooks.

    Args:
        session (nox.sessions.Session): An environment and a set of commands to run.
    """
    # Install requirements
    session.run(
        *pip_install,
        constraint,
        *pre_commit_requirements,
        silent=True,
    )
    # Run pre-commit
    session.run(*pre_commit_commands)


@nox.session(name="safety-cli", python="3.14", tags=["safety"])
def safety_cli(session: nox.sessions.Session) -> None:
    """Runs the Safety CLI.

    Args:
        session (nox.sessions.Session): An environment and a set of commands to run.
    """
    # Install requirements
    session.run(*pip_install, constraint, "safety", silent=True)
    # Login to Safety
    session.run("safety", "auth", "login")
    # Validate policy file
    session.run(
        "safety",
        "validate",
        "policy_file",
        "--path",
        ".safety-policy.yml",
    )
    # Run Safety scan
    session.run("safety", "scan", "--detailed-output")


@nox.session(name="build", python=python_version, tags=["build"])
def build(session: nox.sessions.Session) -> None:
    """Build the application using PyInstaller.

    Args:
        session (nox.sessions.Session): An environment and a set of commands to run.
    """
    # Install the package
    session.install(".", silent=True)
    # Install requirements
    session.run(*pip_install, constraint, "pyinstaller", silent=True)
    # Clean previous builds
    session.run("rm", "-rf", "build", "dist", external=True)

    # Build using PyInstaller
    session.run(
        "pyinstaller",
        "--clean",
        "--console",
        "--onedir",
        "--noupx",
        "--noconfirm",
        "--log-level",
        "DEBUG",
        "--name",
        "server-manager-agent",
        "--debug",
        "all",
        "--optimize",
        "2",
        "src/server_manager_agent/main.py",
    )
