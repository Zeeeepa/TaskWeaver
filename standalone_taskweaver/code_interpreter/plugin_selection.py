import re
from typing import List

from standalone_taskweaver.llm import LLMApi
from standalone_taskweaver.memory.plugin import PluginEntry, PluginRegistry


class SelectedPluginPool:
    """
    SelectedPluginPool is used to store the selected plugins.
    """

    def __init__(self) -> None:
        self.plugins: List[PluginEntry] = []

    def add_selected_plugins(self, plugins: List[PluginEntry]) -> None:
        """Add selected plugins."""
        for plugin in plugins:
            if plugin not in self.plugins:
                self.plugins.append(plugin)

    def get_plugins(self) -> List[PluginEntry]:
        """Get all plugins."""
        return self.plugins

    def filter_unused_plugins(self, code: str) -> None:
        """Filter out unused plugins."""
        used_plugins = []
        for plugin in self.plugins:
            if re.search(r"\b" + plugin.name + r"\b", code):
                used_plugins.append(plugin)
        self.plugins = used_plugins


class PluginSelector:
    """
    PluginSelector is used to select plugins based on the query.
    """

    def __init__(
        self,
        plugin_registry: PluginRegistry,
        llm_api: LLMApi,
    ) -> None:
        self.plugin_registry = plugin_registry
        self.llm_api = llm_api
        self.plugin_embeddings = {}

    def load_plugin_embeddings(self) -> None:
        """Load plugin embeddings."""
        for plugin in self.plugin_registry.get_list():
            self.plugin_embeddings[plugin.name] = self.llm_api.get_embedding(
                plugin.format_prompt(),
            )

    def plugin_select(
        self,
        query: str,
        top_k: int = 3,
    ) -> List[PluginEntry]:
        """
        Select plugins based on the query.
        :param query: The query.
        :param top_k: The number of plugins to select.
        :return: The selected plugins.
        """
        query_embedding = self.llm_api.get_embedding(query)
        plugin_scores = {}
        for plugin_name, plugin_embedding in self.plugin_embeddings.items():
            plugin_scores[plugin_name] = self.llm_api.compute_similarity(
                query_embedding,
                plugin_embedding,
            )

        # sort plugins by score
        sorted_plugins = sorted(
            plugin_scores.items(),
            key=lambda x: x[1],
            reverse=True,
        )

        # select top-k plugins
        selected_plugins = []
        for plugin_name, _ in sorted_plugins[:top_k]:
            plugin = self.plugin_registry.get(plugin_name)
            if plugin is not None:
                selected_plugins.append(plugin)

        return selected_plugins

