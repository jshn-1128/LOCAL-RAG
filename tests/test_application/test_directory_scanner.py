"""
Tests for directory scanner.

Verifies:
  - Scans .txt, .md, .pdf, .docx files
  - Skips hidden files
  - Skips unsupported extensions
  - Skips directories
  - Skips temporary files
  - Recursive scanning
  - Deterministic ordering
  - Empty directory
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app.application.ingestion.directory_scanner import scan_directory


class TestScanDirectory:
    def test_scans_supported_files(self, tmp_path: Path):
        (tmp_path / "a.txt").write_text("a")
        (tmp_path / "b.md").write_text("b")
        files = scan_directory(tmp_path, recursive=False)
        assert len(files) == 2
        assert all(f.suffix in {".txt", ".md"} for f in files)

    def test_skips_hidden_files(self, tmp_path: Path):
        (tmp_path / "visible.txt").write_text("x")
        (tmp_path / ".hidden.txt").write_text("secret")
        files = scan_directory(tmp_path, recursive=False)
        assert len(files) == 1
        assert files[0].name == "visible.txt"

    def test_skips_unsupported_extensions(self, tmp_path: Path):
        (tmp_path / "good.txt").write_text("x")
        (tmp_path / "bad.xyz").write_text("y")
        files = scan_directory(tmp_path, recursive=False)
        assert len(files) == 1
        assert files[0].suffix == ".txt"

    def test_skips_directories(self, tmp_path: Path):
        (tmp_path / "file.txt").write_text("x")
        (tmp_path / "subdir").mkdir()
        files = scan_directory(tmp_path, recursive=False)
        assert len(files) == 1

    def test_skips_temp_files(self, tmp_path: Path):
        (tmp_path / "doc.txt").write_text("x")
        (tmp_path / "backup.tmp").write_text("y")
        (tmp_path / "swap.swp").write_text("z")
        files = scan_directory(tmp_path, recursive=False)
        assert len(files) == 1
        assert files[0].name == "doc.txt"

    def test_recursive_scan(self, tmp_path: Path):
        (tmp_path / "root.txt").write_text("a")
        sub = tmp_path / "subdir"
        sub.mkdir()
        (sub / "nested.txt").write_text("b")
        files = scan_directory(tmp_path, recursive=True)
        assert len(files) == 2

    def test_non_recursive_scan(self, tmp_path: Path):
        (tmp_path / "root.txt").write_text("a")
        sub = tmp_path / "subdir"
        sub.mkdir()
        (sub / "nested.txt").write_text("b")
        files = scan_directory(tmp_path, recursive=False)
        assert len(files) == 1
        assert files[0].name == "root.txt"

    def test_deterministic_ordering(self, tmp_path: Path):
        (tmp_path / "c.txt").write_text("c")
        (tmp_path / "a.txt").write_text("a")
        (tmp_path / "b.txt").write_text("b")
        files = scan_directory(tmp_path, recursive=False)
        names = [f.name for f in files]
        assert names == sorted(names)

    def test_empty_directory(self, tmp_path: Path):
        files = scan_directory(tmp_path, recursive=False)
        assert files == []

    def test_custom_supported_extensions(self, tmp_path: Path):
        (tmp_path / "doc.custom").write_text("x")
        (tmp_path / "doc.txt").write_text("y")
        files = scan_directory(
            tmp_path, recursive=False, supported_extensions={".custom"}
        )
        assert len(files) == 1
        assert files[0].suffix == ".custom"

    def test_skips_broken_symlink(self, tmp_path: Path):
        (tmp_path / "real.txt").write_text("x")
        link = tmp_path / "broken.txt"
        try:
            link.symlink_to(tmp_path / "nonexistent.txt")
        except (OSError, NotImplementedError):
            pytest.skip("Symlink not supported on this platform")
        files = scan_directory(tmp_path, recursive=False)
        assert len(files) == 1
        assert files[0].name == "real.txt"

    def test_skips_hidden_directories(self, tmp_path: Path):
        (tmp_path / "visible.txt").write_text("x")
        hidden = tmp_path / ".hidden"
        hidden.mkdir()
        (hidden / "secret.txt").write_text("y")
        files = scan_directory(tmp_path, recursive=True)
        names = [f.name for f in files]
        assert "secret.txt" not in names
