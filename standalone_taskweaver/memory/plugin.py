import importlib
import inspect
import os
from typing import Any, Dict, List, Optional, Type

from injector import Binder, Module, inject, singleton

from standalone_taskweaver.config.config_mgt import AppConfigSource
from standalone_taskweaver.config.module_config import ModuleConfig


class PluginSpec:
    """
    PluginSpec is used to store the specification of a plugin.
    """

    def __init__(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        returns: Dict[str, Any],
    ) -> None:
        self.name = name
        self.description = description
        self.parameters = parameters
        self.returns = returns

    def plugin_description(self) -> str:
        """Get the description of the plugin."""
        param_desc = ""
        for param_name, param_spec in self.parameters.items():
            param_desc += f"- {param_name}: {param_spec['type']}"
            if "description" in param_spec:
                param_desc += f" - {param_spec['description']}"
            param_desc += "\\n"

        return_desc = ""
        for return_name, return_spec in self.returns.items():
            return_desc += f"- {return_name}: {return_spec['type']}"
            if "description" in return_spec:
                return_desc += f" - {return_spec['description']}"
            return_desc += "\\n"

        return (
            f"Plugin: {self.name}\\n"
            f"Description: {self.description}\\n"
            f"Parameters:\\n{param_desc}"
            f"Returns:\\n{return_desc}"
        )


class PluginEntry:
    """
    PluginEntry is used to store the entry of a plugin.
    """

    def __init__(
        self,
        name: str,
        module: Type,
        spec: PluginSpec,
    ) -> None:
        self.name = name
        self.module = module
        self.spec = spec

    def format_prompt(self) -> str:
        """Format the plugin for prompt."""
        return self.spec.plugin_description()


class PluginRegistry:
    """
    PluginRegistry is used to store all the plugins.
    """

    def __init__(self) -> None:
        self.plugins: Dict[str, PluginEntry] = {}

    def register(
        self,
        name: str,
        module: Type,
        spec: PluginSpec,
    ) -> None:
        """Register a plugin."""
        self.plugins[name] = PluginEntry(
            name=name,
            module=module,
            spec=spec,
        )

    def get(self, name: str) -> Optional[PluginEntry]:
        """Get a plugin by name."""
        return self.plugins.get(name, None)

    def get_list(self) -> List[PluginEntry]:
        """Get all plugins."""
        return list(self.plugins.values())


class PluginConfig(ModuleConfig):
    def _configure(self) -> None:
        self._set_name("plugin")
        self.plugin_dir = self._get_path(
            "plugin_dir",
            os.path.join(self.src.app_base_path, "plugins"),
        )


class PluginModule(Module):
    def configure(self, binder: Binder) -> None:
        binder.bind(PluginRegistry, to=PluginRegistry, scope=singleton)
        binder.bind(PluginConfig, to=PluginConfig, scope=singleton)
        binder.bind(PluginLoader, to=PluginLoader, scope=singleton)


class PluginLoader:
    @inject
    def __init__(
        self,
        config: PluginConfig,
        registry: PluginRegistry,
        app_config: AppConfigSource,
    ) -> None:
        self.config = config
        self.registry = registry
        self.app_config = app_config

        self.load_plugins()

    def load_plugins(self) -> None:
        """Load all plugins."""
        if not os.path.exists(self.config.plugin_dir):
            return

        # get all plugin files
        plugin_files = [
            f
            for f in os.listdir(self.config.plugin_dir)
            if f.endswith(".py") and not f.startswith("__")
        ]

        # load all plugins
        for plugin_file in plugin_files:
            try:
                plugin_name = plugin_file[:-3]
                plugin_path = os.path.join(self.config.plugin_dir, plugin_file)
                spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
                if spec is None or spec.loader is None:
                    continue
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # find the plugin class
                plugin_class = None
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and hasattr(obj, "plugin_spec"):
                        plugin_class = obj
                        break

                if plugin_class is None:
                    continue

                # register the plugin
                self.registry.register(
                    name=plugin_name,
                    module=plugin_class,
                    spec=plugin_class.plugin_spec,
                )
            except Exception as e:
                print(f"Failed to load plugin {plugin_file}: {e}")

