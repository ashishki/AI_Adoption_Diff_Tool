"""Unit tests for git log ingestion edge cases."""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_adoption_diff.ingestion import IngestionError
from ai_adoption_diff.ingestion.git_reader import read_commits


def test_read_commits_raises_on_invalid_path(tmp_path: Path) -> None:
    invalid_path = tmp_path / "not-a-repo"
    invalid_path.mkdir()

    with pytest.raises(IngestionError, match=str(invalid_path)):
        read_commits(invalid_path)
