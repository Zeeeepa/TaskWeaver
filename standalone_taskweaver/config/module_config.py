import os
from typing import Any, List, Optional

from injector import inject

from standalone_taskweaver.config.config_mgt import AppConfigSource


class ModuleConfig:
    """
    ModuleConfig is the base class for all module configurations.
    """

    @inject
    def __init__(
        self,
        src: AppConfigSource,
    ) -> None:
        self.src = src
        self.name = ""
        self._configure()

    def _configure(self) -> None:
        """
        Configure the module.
        """
        pass

    def _set_name(self, name: str) -> None:
        """
        Set the name of the module.
        :param name: The name.
        """
        self.name = name

    def _get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        :param key: The key.
        :param default: The default value.
        :return: The value.
        """
        return self.src.get(f"{self.name}.{key}", default)

    def _get_bool(self, key: str, default: bool = False) -> bool:
        """
        Get a boolean configuration value.
        :param key: The key.
        :param default: The default value.
        :return: The value.
        """
        return self.src.get_bool(f"{self.name}.{key}", default)

    def _get_int(self, key: str, default: int = 0) -> int:
        """
        Get an integer configuration value.
        :param key: The key.
        :param default: The default value.
        :return: The value.
        """
        return self.src.get_int(f"{self.name}.{key}", default)

    def _get_float(self, key: str, default: float = 0.0) -> float:
        """
        Get a float configuration value.
        :param key: The key.
        :param default: The default value.
        :return: The value.
        """
        return self.src.get_float(f"{self.name}.{key}", default)

    def _get_str(
        self,
        key: str,
        default: str = "",
        required: bool = False,
    ) -> str:
        """
        Get a string configuration value.
        :param key: The key.
        :param default: The default value.
        :param required: Whether the value is required.
        :return: The value.
        """
        value = self.src.get_str(f"{self.name}.{key}", default)
        if required and value == "":
            raise ValueError(f"Required configuration value {self.name}.{key} is not set")
        return value

    def _get_list(
        self,
        key: str,
        default: Optional[List[Any]] = None,
    ) -> List[Any]:
        """
        Get a list configuration value.
        :param key: The key.
        :param default: The default value.
        :return: The value.
        """
        return self.src.get_list(f"{self.name}.{key}", default)

    def _get_dict(self, key: str, default: Optional[dict] = None) -> dict:
        """
        Get a dictionary configuration value.
        :param key: The key.
        :param default: The default value.
        :return: The value.
        """
        return self.src.get_dict(f"{self.name}.{key}", default)

    def _get_path(
        self,
        key: str,
        default: str = "",
        required: bool = False,
    ) -> str:
        """
        Get a path configuration value.
        :param key: The key.
        :param default: The default value.
        :param required: Whether the value is required.
        :return: The value.
        """
        value = self._get_str(key, default, required)
        if value == "":
            return value
        if os.path.isabs(value):
            return value
        return os.path.join(self.src.app_base_path, value)

