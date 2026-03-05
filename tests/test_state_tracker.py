"""
/**
 * [IN]: src.state_tracker (StateTracker, FileState)
 * [OUT]: StateTracker 单元测试
 * [POS]: pytest 测试套件，Phase 4 单元测试覆盖
 * [PROTOCOL]: state_tracker.py 修改 -> 同步更新本测试
 */
"""
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest


class TestStateTrackerInit:
    """测试 StateTracker 初始化"""

    def test_creates_default_state_when_no_file(self, tmp_path):
        with patch("src.config.settings") as mock_settings:
            mock_settings.state_file = tmp_path / "state.json"
            mock_settings.state_file.parent.mkdir(parents=True, exist_ok=True)
            from src.state_tracker import StateTracker
            tracker = StateTracker.__new__(StateTracker)
            tracker.state_file = tmp_path / "state.json"
            tracker._state = {}
            tracker._load()
            assert "files" in tracker._state
            assert "version" in tracker._state

    def test_loads_existing_state(self, tmp_path):
        state_file = tmp_path / "state.json"
        existing = {
            "version": "1.0",
            "last_updated": "2026-01-01T00:00:00",
            "files": {"test.pdf": {"hash": "abc", "status": "completed",
                                   "title": "T", "folder_name": "F",
                                   "processed_at": "2026-01-01",
                                   "outputs": []}},
            "unnamed_counter": 0
        }
        state_file.write_text(json.dumps(existing), encoding="utf-8")

        with patch("src.config.settings") as mock_settings:
            mock_settings.state_file = state_file
            from src.state_tracker import StateTracker
            tracker = StateTracker.__new__(StateTracker)
            tracker.state_file = state_file
            tracker._state = {}
            tracker._load()
            assert "test.pdf" in tracker._state["files"]


class TestStateTrackerComputeHash:
    """测试 StateTracker.compute_hash (静态方法)"""

    def test_returns_sha256_prefixed_string(self, tmp_path):
        from src.state_tracker import StateTracker
        f = tmp_path / "test.pdf"
        f.write_bytes(b"content")
        result = StateTracker.compute_hash(f)
        assert result.startswith("sha256:")

    def test_consistent_for_same_content(self, tmp_path):
        from src.state_tracker import StateTracker
        f = tmp_path / "test.pdf"
        f.write_bytes(b"same content")
        assert StateTracker.compute_hash(f) == StateTracker.compute_hash(f)

    def test_different_for_different_content(self, tmp_path):
        from src.state_tracker import StateTracker
        f1 = tmp_path / "a.pdf"
        f2 = tmp_path / "b.pdf"
        f1.write_bytes(b"content A")
        f2.write_bytes(b"content B")
        assert StateTracker.compute_hash(f1) != StateTracker.compute_hash(f2)


class TestStateTrackerIsProcessed:
    """测试 StateTracker.is_processed"""

    def _make_tracker(self, tmp_path):
        state_file = tmp_path / ".deepread" / "state.json"
        state_file.parent.mkdir(parents=True, exist_ok=True)
        with patch("src.config.settings") as mock_settings:
            mock_settings.state_file = state_file
            from src.state_tracker import StateTracker
            tracker = StateTracker.__new__(StateTracker)
            tracker.state_file = state_file
            tracker._state = {
                "version": "1.0",
                "last_updated": "",
                "files": {},
                "unnamed_counter": 0
            }
        return tracker

    def test_returns_false_for_unknown_file(self, tmp_path):
        tracker = self._make_tracker(tmp_path)
        pdf = tmp_path / "new.pdf"
        pdf.write_bytes(b"new content")
        assert tracker.is_processed(pdf) is False

    def test_returns_false_when_hash_mismatch(self, tmp_path):
        from src.state_tracker import StateTracker
        tracker = self._make_tracker(tmp_path)
        pdf = tmp_path / "paper.pdf"
        pdf.write_bytes(b"current content")
        tracker._state["files"]["paper.pdf"] = {
            "hash": "sha256:different_hash",
            "status": "completed",
            "outputs": [],
            "title": "T",
            "folder_name": "F",
            "processed_at": "2026-01-01",
        }
        assert tracker.is_processed(pdf) is False


class TestStateTrackerUpdateFileState:
    """测试 StateTracker.update_file_state"""

    def test_stores_file_record(self, tmp_path):
        state_file = tmp_path / "state.json"
        with patch("src.config.settings") as mock_settings:
            mock_settings.state_file = state_file
            from src.state_tracker import StateTracker
            tracker = StateTracker.__new__(StateTracker)
            tracker.state_file = state_file
            tracker._state = {
                "version": "1.0",
                "last_updated": "",
                "files": {},
                "unnamed_counter": 0
            }

            # Mock _save_atomic so we don't write to disk during test
            tracker._save_atomic = MagicMock()

            pdf = tmp_path / "paper.pdf"
            pdf.write_bytes(b"content")

            tracker.update_file_state(
                pdf_path=pdf,
                title="Test Paper",
                folder_name="2024-Test",
                outputs=["output/file.md"]
            )

            assert "paper.pdf" in tracker._state["files"]
            record = tracker._state["files"]["paper.pdf"]
            assert record["title"] == "Test Paper"
            assert record["folder_name"] == "2024-Test"
            assert record["status"] == "completed"


class TestStateTrackerGetAllProcessedFiles:
    """测试 StateTracker.get_all_processed_files"""

    def test_returns_only_completed(self, tmp_path):
        state_file = tmp_path / "state.json"
        with patch("src.config.settings") as mock_settings:
            mock_settings.state_file = state_file
            from src.state_tracker import StateTracker
            tracker = StateTracker.__new__(StateTracker)
            tracker.state_file = state_file
            tracker._state = {
                "version": "1.0",
                "last_updated": "",
                "unnamed_counter": 0,
                "files": {
                    "done.pdf": {"status": "completed", "hash": "x",
                                 "title": "T", "folder_name": "F",
                                 "processed_at": "", "outputs": []},
                    "failed.pdf": {"status": "failed", "hash": "y",
                                   "title": "T2", "folder_name": "F2",
                                   "processed_at": "", "outputs": []},
                }
            }
            result = tracker.get_all_processed_files()
            assert "done.pdf" in result
            assert "failed.pdf" not in result

    def test_empty_when_no_files(self, tmp_path):
        state_file = tmp_path / "state.json"
        with patch("src.config.settings") as mock_settings:
            mock_settings.state_file = state_file
            from src.state_tracker import StateTracker
            tracker = StateTracker.__new__(StateTracker)
            tracker.state_file = state_file
            tracker._state = {
                "version": "1.0", "last_updated": "",
                "unnamed_counter": 0, "files": {}
            }
            assert tracker.get_all_processed_files() == []
