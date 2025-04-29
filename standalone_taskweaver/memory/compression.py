from typing import Callable, List, Optional, Tuple

from standalone_taskweaver.llm import LLMApi
from standalone_taskweaver.memory.round import Round


class RoundCompressor:
    """
    RoundCompressor is used to compress the rounds in the memory.
    """

    def __init__(
        self,
        llm_api: LLMApi,
    ) -> None:
        self.llm_api = llm_api

    def compress_rounds(
        self,
        rounds: List[Round],
        rounds_formatter: Callable[[List[Round]], str],
        prompt_template: str,
    ) -> Tuple[str, List[Round]]:
        """
        Compress the rounds in the memory.
        :param rounds: The rounds to compress.
        :param rounds_formatter: The function to format the rounds.
        :param prompt_template: The prompt template.
        :return: The summary and the rounds after compression.
        """
        if len(rounds) <= 1:
            return "", rounds

        # keep the last round
        last_round = rounds[-1]
        rounds_to_compress = rounds[:-1]

        # format the rounds to compress
        rounds_str = rounds_formatter(rounds_to_compress)

        # compress the rounds
        prompt = prompt_template.format(
            rounds=rounds_str,
        )

        # get the summary
        summary = self.llm_api.chat_completion(
            [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        # return the summary and the last round
        return summary, [last_round]

