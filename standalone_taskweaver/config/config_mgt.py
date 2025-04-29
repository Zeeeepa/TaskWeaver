import json
import os
from typing import Any, Dict, Optional

from injector import Injector


class AppConfigSource:
    """
    AppConfigSource is used to store the configuration of the application.
    """

    def __init__(
        self,
        config_file_path: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        app_base_path: Optional[str] = None,
    ) -> None:
        self.config_file_path = config_file_path
        self.config = config if config is not None else {}
        self.app_base_path = app_base_path if app_base_path is not None else os.getcwd()
        self.app_injector = Injector()

        if self.config_file_path is not None and os.path.exists(self.config_file_path):
            with open(self.config_file_path, "r") as f:
                self.config.update(json.load(f))

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        :param key: The key.
        :param default: The default value.
        :return: The value.
        """
        return self.config.get(key, default)

    def get_bool(self, key: str, default: bool = False) -> bool:
        """
        Get a boolean configuration value.
        :param key: The key.
        :param default: The default value.
        :return: The value.
        """
        value = self.get(key, default)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ["true", "yes", "1"]
        return bool(value)

    def get_int(self, key: str, default: int = 0) -> int:
        """
        Get an integer configuration value.
        :param key: The key.
        :param default: The default value.
        :return: The value.
        """
        value = self.get(key, default)
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            return int(value)
        return int(value)

    def get_float(self, key: str, default: float = 0.0) -> float:
        """
        Get a float configuration value.
        :param key: The key.
        :param default: The default value.
        :return: The value.
        """
        value = self.get(key, default)
        if isinstance(value, float):
            return value
        if isinstance(value, str):
            return float(value)
        return float(value)

    def get_str(self, key: str, default: str = "") -> str:
        """
        Get a string configuration value.
        :param key: The key.
        :param default: The default value.
        :return: The value.
        """
        value = self.get(key, default)
        if isinstance(value, str):
            return value
        return str(value)

    def get_list(self, key: str, default: Optional[list] = None) -> list:
        """
        Get a list configuration value.
        :param key: The key.
        :param default: The default value.
        :return: The value.
        """
        value = self.get(key, default)
        if value is None:
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return value.split(",")
        return list(value)

    def get_dict(self, key: str, default: Optional[dict] = None) -> dict:
        """
        Get a dictionary configuration value.
        :param key: The key.
        :param default: The default value.
        :return: The value.
        """
        value = self.get(key, default)
        if value is None:
            return {}
        if isinstance(value, dict):
            return value
        return dict(value)

