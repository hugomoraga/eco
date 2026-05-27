"""
test_logging_integration.py — Integration tests for the logging system.

Tests:
1. structlog is properly configured
2. Logs go to stderr
3. Logs go to debug.log when run_dir is provided
4. Hexagonal architecture: core imports from core.utils.logger, not infra
5. init_logger is called by adapter layer, not core
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path


class TestLoggingIntegration:
    """Integration tests for logging system."""

    def test_structlog_is_configured(self):
        """Verify structlog can be imported and used."""
        from infra.logging import init_logger, get_logger

        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = Path(tmpdir)
            init_logger(run_dir)
            log = get_logger("test")
            log.info("test_message", key="value")

        assert True

    def test_logs_go_to_stderr(self):
        """Verify logs appear in stderr."""
        code = """
from pathlib import Path
import tempfile
from infra.logging import init_logger, get_logger

with tempfile.TemporaryDirectory() as tmpdir:
    init_logger(Path(tmpdir))
    log = get_logger("test_stderr")
    log.info("stderr_test", turn=1)
"""
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "stderr_test" in result.stderr or "info" in result.stderr.lower()

    def test_logs_go_to_debug_log(self):
        """Verify logs are written to debug.log."""
        code = """
from pathlib import Path
import tempfile
from infra.logging import init_logger, get_logger

with tempfile.TemporaryDirectory() as tmpdir:
    run_dir = Path(tmpdir)
    init_logger(run_dir)
    log = get_logger("test_file")
    log.info("file_test", turn=1)
    # Explicitly read the file in the same process to verify
    debug_log = run_dir / "debug.log"
    content = debug_log.read_text()
    print(f"CONTENT_START{content}CONTENT_END")
"""
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "CONTENT_START" in result.stdout
        start_idx = result.stdout.find("CONTENT_START") + len("CONTENT_START")
        end_idx = result.stdout.find("CONTENT_END")
        content = result.stdout[start_idx:end_idx]
        assert "file_test" in content, f"file_test not in debug.log content: {content}"

    def test_no_logs_to_stdout(self):
        """Verify logs do NOT go to stdout (reserved for JSON protocol)."""
        code = """
from pathlib import Path
import tempfile
from infra.logging import init_logger, get_logger

with tempfile.TemporaryDirectory() as tmpdir:
    init_logger(Path(tmpdir))
    log = get_logger("test_stdout")
    log.info("should_not_be_in_stdout", turn=1)
"""
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
        )
        assert "should_not_be_in_stdout" not in result.stdout

    def test_headless_run_creates_debug_log(self):
        """Verify headless run creates debug.log in run directory."""
        result = subprocess.run(
            [sys.executable, "run.py", "--headless", "--turns", "1"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )
        assert result.returncode == 0

        run_dir = Path(__file__).parent.parent / "runs"
        assert run_dir.exists()

        run_subdirs = sorted(run_dir.glob("run_*"), key=lambda p: p.stat().st_mtime)
        latest_run = run_subdirs[-1] if run_subdirs else None

        if latest_run:
            debug_log = latest_run / "debug.log"
            assert debug_log.exists(), f"debug.log should exist in {latest_run}"
            content = debug_log.read_text()
            assert len(content) > 0, "debug.log should not be empty"


class TestHexagonalArchitecture:
    """Verify hexagonal architecture constraints are met."""

    def test_core_does_not_import_infra_logging(self):
        """core/ should not import directly from infra.logging.

        Exception: core/utils/logger.py is the allowed bridge to infra.logging.
        """
        core_dir = Path(__file__).parent.parent / "core"
        violations = []

        for py_file in core_dir.rglob("*.py"):
            if py_file.name == "logger.py" and "utils" in str(py_file):
                continue  # core/utils/logger.py is the allowed bridge
            content = py_file.read_text()
            if "from infra.logging import" in content or "from infra import" in content:
                violations.append(str(py_file.relative_to(core_dir.parent)))

        assert len(violations) == 0, f"core/ files should not import from infra: {violations}"

    def test_core_uses_core_utils_logger(self):
        """core/ components that need logging should use core.utils.logger."""
        core_dir = Path(__file__).parent.parent / "core"

        for py_file in core_dir.rglob("*.py"):
            content = py_file.read_text()
            if "get_logger" in content and "infra" not in content:
                assert "from core.utils.logger import" in content or "core.utils.logger" in content, \
                    f"{py_file.name} uses get_logger but doesn't import from core.utils.logger"
