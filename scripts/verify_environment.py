"""Verify the development environment is correctly configured."""

import subprocess
import sys
from importlib.metadata import version
from pathlib import Path

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


def check_python_version() -> bool:
    ver = sys.version_info
    ok = ver.major == 3 and ver.minor == 11
    print(f"  Python: {ver.major}.{ver.minor}.{ver.micro}" + (" ✅" if ok else " ❌"))
    return ok


def check_tool(name: str) -> bool:
    try:
        ver = version(name)
        print(f"  {name}: {ver} ✅")
        return True
    except Exception:
        print(f"  {name}: not found ❌")
        return False


def check_dirs() -> bool:
    ok = True
    root = Path.cwd()
    for d in REQUIRED_DIRS:
        path = root / d
        if path.is_dir():
            print(f"  {d}/ ✅")
        else:
            print(f"  {d}/ ❌ (missing)")
            ok = False
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
        print(f"  Git working tree: {'dirty ❌' if dirty else 'clean ✅'}")
        return not dirty
    except Exception as e:
        print(f"  Git: {e} ❌")
        return False


def main() -> int:
    print("=" * 50)
    print("  Local RAG - Environment Verification")
    print("=" * 50)

    print("\nPython:")
    py_ok = check_python_version()

    print("\nTools:")
    tools_ok = all(check_tool(name) for name in REQUIRED_TOOLS)

    print("\nDirectories:")
    dirs_ok = check_dirs()

    print("\nRepository:")
    git_ok = check_git()

    print("\n" + "=" * 50)
    all_ok = all([py_ok, tools_ok, dirs_ok, git_ok])
    print(f"  Result: {'✅ PASS' if all_ok else '❌ FAIL'}")
    print("=" * 50)

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
