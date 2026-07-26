"""
Directory scanner for batch document loading.

Recursively scans directories for supported document files,
skipping hidden files, temporary files, and broken symlinks.
"""

from __future__ import annotations

import logging
from pathlib import Path

from app.config.constants import SUPPORTED_DOCUMENT_EXTENSIONS

logger = logging.getLogger(__name__)

_HIDDEN_PREFIX: str = "."
_TEMP_SUFFIXES: frozenset[str] = frozenset({".tmp", ".temp", ".bak", ".swp"})


def _is_hidden(path: Path) -> bool:
    """Check if a file or directory should be considered hidden."""
    return path.name.startswith(_HIDDEN_PREFIX)


def _has_hidden_parent(path: Path) -> bool:
    """Check if any parent directory is hidden."""
    return any(part.startswith(_HIDDEN_PREFIX) for part in path.parts)


def _is_temp_file(path: Path) -> bool:
    """Check if a file has a temporary suffix."""
    return path.suffix.lower() in _TEMP_SUFFIXES


def _is_broken_symlink(path: Path) -> bool:
    """Check if a path is a broken symbolic link."""
    return path.is_symlink() and not path.exists()


def scan_directory(
    directory: Path,
    recursive: bool = True,
    supported_extensions: set[str] | None = None,
) -> list[Path]:
    """Scan a directory for supported document files.

    Args:
        directory: Path to the directory to scan.
        recursive: Whether to scan subdirectories recursively.
        supported_extensions: Set of allowed extensions. Defaults to global set.

    Returns:
        Sorted list of valid file paths.

    Skips:
        - Hidden files and directories (starting with '.')
        - Temporary files (.tmp, .temp, .bak, .swp)
        - Broken symbolic links
        - Unsupported extensions
    """
    if supported_extensions is None:
        supported_extensions = SUPPORTED_DOCUMENT_EXTENSIONS

    files: list[Path] = []

    if recursive:
        iterator: Path = directory
        for entry in sorted(iterator.rglob("*")):
            if _should_skip(entry, supported_extensions):
                continue
            files.append(entry)
    else:
        for entry in sorted(directory.iterdir()):
            if _should_skip(entry, supported_extensions):
                continue
            files.append(entry)

    return files


def _should_skip(entry: Path, supported_extensions: set[str]) -> bool:
    """Determine whether a directory entry should be skipped."""
    if _is_hidden(entry) or _has_hidden_parent(entry):
        return True
    if entry.is_dir():
        return True
    if _is_broken_symlink(entry):
        logger.debug("Skipping broken symlink: %s", entry)
        return True
    if _is_temp_file(entry):
        logger.debug("Skipping temporary file: %s", entry)
        return True
    entry_ext = entry.suffix.lower()
    if entry_ext not in supported_extensions:
        logger.debug("Skipping unsupported extension: %s", entry)
        return True
    return False
