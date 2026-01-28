import logging
import sys
from uvicorn.logging import DefaultFormatter

def setup_logging():
    """
    Configure logging for the application to match Uvicorn/FastAPI style.
    """
    # Create a handler that writes to stdout
    handler = logging.StreamHandler(sys.stdout)
    
    # Use Uvicorn's DefaultFormatter to get the "INFO:     Message" style
    # with colors if the terminal supports it.
    formatter = DefaultFormatter(fmt="%(levelprefix)s %(message)s")
    handler.setFormatter(formatter)

    # Configure the root logger
    root_logger = logging.getLogger()
    
    # Remove existing handlers to avoid duplication/formatting conflicts
    root_logger.handlers.clear()
    
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)
    
    # Set lower level for third-party libraries if needed
    # logging.getLogger("uvicorn").setLevel(logging.INFO)
    # logging.getLogger("fastapi").setLevel(logging.INFO)

logger = logging.getLogger("genui-backend")
