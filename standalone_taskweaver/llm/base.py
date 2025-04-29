from typing import Any, Dict, List, Optional, Union

from standalone_taskweaver.llm.util import ChatMessageType


class LLMApi:
    """
    LLMApi is the base class for all LLM APIs.
    """

    def chat_completion(
        self,
        messages: List[ChatMessageType],
        use_smoother: bool = False,
        llm_alias: str = "",
        json_schema: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Get the chat completion.
        :param messages: The messages.
        :param use_smoother: Whether to use smoother.
        :param llm_alias: The LLM alias.
        :param json_schema: The JSON schema.
        :return: The completion.
        """
        raise NotImplementedError

    def chat_completion_stream(
        self,
        messages: List[ChatMessageType],
        use_smoother: bool = False,
        llm_alias: str = "",
        json_schema: Optional[Dict[str, Any]] = None,
        stream: bool = True,
    ) -> Union[str, List[ChatMessageType]]:
        """
        Get the chat completion stream.
        :param messages: The messages.
        :param use_smoother: Whether to use smoother.
        :param llm_alias: The LLM alias.
        :param json_schema: The JSON schema.
        :param stream: Whether to stream the completion.
        :return: The completion.
        """
        raise NotImplementedError

    def get_embedding(
        self,
        text: str,
    ) -> List[float]:
        """
        Get the embedding.
        :param text: The text.
        :return: The embedding.
        """
        raise NotImplementedError

    def compute_similarity(
        self,
        embedding1: List[float],
        embedding2: List[float],
    ) -> float:
        """
        Compute the similarity between two embeddings.
        :param embedding1: The first embedding.
        :param embedding2: The second embedding.
        :return: The similarity.
        """
        raise NotImplementedError

