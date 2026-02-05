"""
RAG Service module providing singleton pattern for RAG instance management.
Handles caching and resource optimization for multiple themes.
"""

import logging
from typing import Optional, Dict
from pathlib import Path


logger = logging.getLogger(__name__)


class RagService:
    """
    Singleton RAG service with instance caching per theme.
    Manages RAG instances efficiently by caching them.
    """

    _instances: Dict[str, 'RagService'] = {}

    def __init__(self, theme: str, resources_path: Path):
        """
        Initialize RAG service for a specific theme.

        Args:
            theme: Theme name for RAG instance
            resources_path: Path to resources directory
        """
        self.theme = theme
        self.resources_path = resources_path
        self.rag = None
        logger.info(f"Initialized RagService for theme: {theme}")

    @classmethod
    def get_instance(
            cls,
            theme: str,
            resources_path: Optional[Path] = None) -> 'RagService':
        """
        Get or create RAG instance for a theme (singleton pattern).

        Args:
            theme: Theme name
            resources_path: Path to resources directory

        Returns:
            RagService instance
        """
        if theme not in cls._instances:
            if resources_path is None:
                resources_path = Path.cwd() / "resources"
            cls._instances[theme] = RagService(theme, resources_path)
            logger.info(f"Created new RagService instance for theme: {theme}")

        return cls._instances[theme]

    def populate(self, data: Dict) -> None:
        """
        Populate RAG with example data.

        Args:
            data: Data to populate RAG with
        """
        try:
            logger.info(f"Populating RAG for theme {self.theme}")
            # RAG population logic would go here
        except Exception as e:
            logger.error(f"Error populating RAG: {str(e)}")
            raise

    def delete_example(self, example_id: str) -> None:
        """
        Delete example from RAG.

        Args:
            example_id: ID of example to delete
        """
        try:
            logger.info(
                f"Deleting example {example_id} from RAG for theme {
                    self.theme}")
            # RAG deletion logic would go here
        except Exception as e:
            logger.error(f"Error deleting example: {str(e)}")
            raise

    @classmethod
    def cleanup(cls) -> None:
        """Clean up all RAG instances."""
        cls._instances.clear()
        logger.info("Cleaned up all RagService instances")
