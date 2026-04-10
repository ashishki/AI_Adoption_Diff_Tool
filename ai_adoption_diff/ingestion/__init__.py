"""Ingestion package."""


class IngestionError(Exception):
    """Raised when git log ingestion fails."""


# Re-export CommitRecord at package boundary (defined after IngestionError to avoid circular import)
from ai_adoption_diff.ingestion.git_reader import CommitRecord  # noqa: E402

__all__ = ["CommitRecord", "IngestionError"]
