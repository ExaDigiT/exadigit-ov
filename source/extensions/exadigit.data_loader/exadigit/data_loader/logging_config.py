import logging

import omni.client

# Set up root logger to ensure all levels are shown
logging.basicConfig(level=logging.DEBUG)

# Create a logger instance for the extension
logger = logging.getLogger("exadigit.data_loader")

# Ensure logs propagate across all modules
logger.propagate = True

# Set log level explicitly for this logger
logger.setLevel(logging.DEBUG)

# Create a console handler if not already present
if not logger.hasHandlers():
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)  # Ensure all logs show
    formatter = logging.Formatter("[%(levelname)s] [%(name)s] %(message)s")
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

# Explicitly tell Omniverse to accept lower log levels
omni.client.set_log_level(omni.client.LogLevel.DEBUG)
