import logging
import os
import datetime
def setup_logging(log_dir="logs", base_log_file="application"):
    """
    Set up logging configuration.

    For each run, a new log file is created in the specified log_dir.
    The log file is named as {base_log_file}_{timestamp}.log.

    Log format:
    [timestamp] - [log level] - [file name] - [message]
    """
    # Create the logs directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    logging.getLogger("multipart").setLevel(logging.WARNING)
    # Generate a timestamp string for the current run
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"{base_log_file}_{timestamp}.log"

    # Define the log format
    log_format = "%(asctime)s - %(levelname)s - %(filename)s - %(message)s"

    # Create a formatter using the log format
    formatter = logging.Formatter(log_format)

    # Set up a file handler that writes DEBUG and above messages to the file
    file_handler = logging.FileHandler(os.path.join(log_dir, log_file))
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    # Set up a stream handler (console) that outputs INFO and above messages
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.INFO)

    # Get the root logger and set its overall level to DEBUG
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Add both handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

