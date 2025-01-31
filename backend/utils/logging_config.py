import logging
import os
import logging.config

# Define log directory and log file path
log_directory = "log"
log_file_path = os.path.join(log_directory, "app.log")

# Ensure the log directory exists
os.makedirs(log_directory, exist_ok=True)

# Clear (truncate) the log file on application restart
with open(log_file_path, 'w'):
    pass

# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": log_file_path,  # Dynamically set log file path
            "formatter": "default",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "file"],
    },
}

# Set up logging configuration
logging.config.dictConfig(LOGGING_CONFIG)

# Example usage
logger = logging.getLogger(__name__)
logger.info("Application started. Logging is set up.")
