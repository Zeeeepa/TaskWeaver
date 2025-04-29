import json
import logging
import os
from typing import Any, Dict, List, Optional


class TelemetryLogger:
    """
    TelemetryLogger is used to log telemetry data.
    """

    def __init__(
        self,
        log_dir: Optional[str] = None,
        log_level: int = logging.INFO,
    ) -> None:
        self.log_dir = log_dir
        self.logger = logging.getLogger("taskweaver")
        self.logger.setLevel(log_level)

        # create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # create file handler
        if log_dir is not None:
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            file_handler = logging.FileHandler(
                os.path.join(log_dir, "taskweaver.log"),
            )
            file_handler.setLevel(log_level)
            file_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

    def debug(self, message: str) -> None:
        """
        Log a debug message.
        :param message: The message.
        """
        self.logger.debug(message)

    def info(self, message: str) -> None:
        """
        Log an info message.
        :param message: The message.
        """
        self.logger.info(message)

    def warning(self, message: str) -> None:
        """
        Log a warning message.
        :param message: The message.
        """
        self.logger.warning(message)

    def error(self, message: str) -> None:
        """
        Log an error message.
        :param message: The message.
        """
        self.logger.error(message)

    def critical(self, message: str) -> None:
        """
        Log a critical message.
        :param message: The message.
        """
        self.logger.critical(message)

    def dump_prompt_file(
        self,
        prompt: List[Dict[str, Any]],
        file_path: str,
    ) -> None:
        """
        Dump a prompt to a file.
        :param prompt: The prompt.
        :param file_path: The file path.
        """
        with open(file_path, "w") as f:
            json.dump(prompt, f, indent=2)

