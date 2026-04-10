"""Environment-backed runtime configuration."""

from __future__ import annotations

import os
from pathlib import Path

from pydantic import BaseModel, Field


class Config(BaseModel):
    """Project runtime configuration loaded from environment variables."""

    log_level: str = Field(default_factory=lambda: os.getenv("AI_DIFF_LOG_LEVEL", "INFO"))
    output_dir: Path = Field(
        default_factory=lambda: Path(os.getenv("AI_DIFF_OUTPUT_DIR", "./output"))
    )
    # GITHUB_TOKEN is read here and never passed to any logger.
    github_token: str | None = Field(default_factory=lambda: os.getenv("GITHUB_TOKEN"))
