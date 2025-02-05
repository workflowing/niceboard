from .services.search import NiceBoardSearchService
from .client import Client

# For backwards compatibility
from .services.search import NiceBoardSearchService as search_jobs

__version__ = "0.1.0"
__all__ = ["search_jobs", "NiceBoardSearchService", "Client"]
