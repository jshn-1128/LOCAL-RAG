"""Verify the development environment is correctly configured."""

import re
import subprocess
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

REQUIRED_PYTHON = (3, 11)

REQUIRED_TOOLS: dict[str, str] = {
    "black": "24.0",
    "ruff": "0.5.0",
    "mypy": "1.10.0",
    "pytest": "8.0",
    "pre-commit": "3.7.0",
}

REQUIRED_DIRS = [
    "app",
    "configs",
    "data",
    "docs",
    "logs",
    "models",
    "scripts",
    "tests",
]


def fmt(status: bool, label: str = "") -> str:
    mark = "✅" if status else "❌"
    return f"{mark} {label}" if label else mark


def check_pyenv() -> bool:
    try:
        result = subprocess.run(
            ["pyenv", "version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            print(f"  pyenv: {fmt(False)} not installed or not in PATH")
            return False
        line = result.stdout.strip()
        match = re.match(r"^(\S+)", line)
        active = match.group(1) if match else "unknown"
        print(f"  pyenv active version: {active} {fmt(True)}")
        return True
    except FileNotFoundError:
        print(
            f"  pyenv: {fmt(False)} not found — install from https://github.com/pyenv/pyenv"
        )
        return False


def check_python_version() -> bool:
    ver = sys.version_info
    ok = (ver.major, ver.minor) == REQUIRED_PYTHON
    label = f"{ver.major}.{ver.minor}.{ver.micro}"
    print(f"  Python version: {label} {fmt(ok)}")
    if not ok:
        print(f"    Expected {REQUIRED_PYTHON[0]}.{REQUIRED_PYTHON[1]}.x")
    return ok


def check_venv() -> bool:
    in_venv = sys.prefix != sys.base_prefix
    label = Path(sys.prefix).name
    print(f"  Virtual environment: {label} {fmt(in_venv)}")
    if not in_venv:
        print("    Activate: source .venv/bin/activate")
    return in_venv


def check_python_version_file() -> bool:
    path = Path(".python-version")
    if not path.exists():
        print(f"  .python-version: {fmt(False)} missing")
        return False
    expected = path.read_text().strip()
    ok = expected.startswith(f"{REQUIRED_PYTHON[0]}.{REQUIRED_PYTHON[1]}")
    print(f"  .python-version: {expected} {fmt(ok)}")
    return ok


def parse_version(ver: str) -> tuple[int, ...]:
    return tuple(int(p) for p in ver.split("."))


def check_tool(name: str, min_version: str) -> bool:
    try:
        ver = version(name)
        ok = parse_version(ver) >= parse_version(min_version)
        label = f"{name} {ver}"
        if not ok:
            label += f" (minimum {min_version})"
        print(f"  {label} {fmt(ok)}")
        return ok
    except PackageNotFoundError:
        print(f"  {name}: {fmt(False)} not installed")
        return False


def check_dirs() -> bool:
    ok = True
    root = Path.cwd()
    for d in REQUIRED_DIRS:
        path = root / d
        exists = path.is_dir()
        if not exists:
            print(f"  {d}/ {fmt(False)} missing")
        ok = ok and exists
    if ok:
        print(f"  All {len(REQUIRED_DIRS)} directories present {fmt(True)}")
    return ok


def check_git() -> bool:
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        dirty = bool(result.stdout.strip())
        print(f"  Git working tree: {fmt(not dirty)}")
        if dirty:
            print("    Uncommitted changes detected")
        return not dirty
    except Exception as e:
        print(f"  Git: {fmt(False)} {e}")
        return False


def check_precommit_installed() -> bool:
    hook_path = Path(".git/hooks/pre-commit")
    if not hook_path.exists():
        print(
            f"  pre-commit hooks: {fmt(False)} not installed (run 'pre-commit install')"
        )
        return False
    content = hook_path.read_text()
    ok = "pre-commit" in content
    print(f"  pre-commit hooks: {fmt(ok)}")
    return ok


def main() -> int:
    print("=" * 52)
    print("  Local RAG — Environment Verification")
    print("=" * 52)

    print("\n  Python Environment")
    py_ok = check_python_version()
    venv_ok = check_venv()
    pyfile_ok = check_python_version_file()

    print("\n  Tooling")
    pyenv_ok = check_pyenv()
    tools_ok = all(check_tool(name, ver) for name, ver in REQUIRED_TOOLS.items())

    print("\n  Project Structure")
    dirs_ok = check_dirs()

    print("\n  Repository")
    git_ok = check_git()
    precommit_ok = check_precommit_installed()

    results = [
        py_ok,
        venv_ok,
        pyfile_ok,
        pyenv_ok,
        tools_ok,
        dirs_ok,
        git_ok,
        precommit_ok,
    ]
    all_ok = all(results)

    print("\n" + "=" * 52)
    summary = f"  Result: {'✅ PASS' if all_ok else '❌ FAIL'}"
    for _i, (name, ok) in enumerate(
        [
            ("Python version", py_ok),
            ("Virtual environment", venv_ok),
            (".python-version file", pyfile_ok),
            ("pyenv", pyenv_ok),
            ("Developer tools", tools_ok),
            ("Directories", dirs_ok),
            ("Git working tree", git_ok),
            ("Pre-commit hooks", precommit_ok),
        ]
    ):
        summary += f"\n    {fmt(ok)} {name}"
    print(summary)
    print("=" * 52)

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
