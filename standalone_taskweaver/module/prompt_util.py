import re
from typing import List, Optional


class PromptUtil:
    """
    PromptUtil is used to manipulate prompts.
    """

    DELIMITER_TEMPORAL = "TEMPORAL"
    DELIMITER_PERMANENT = "PERMANENT"

    @staticmethod
    def add_part(
        text: str,
        part: str,
        delimiter: str = DELIMITER_TEMPORAL,
    ) -> str:
        """
        Add a part to the text.
        :param text: The text.
        :param part: The part.
        :param delimiter: The delimiter.
        :return: The text with the part.
        """
        return f"{text}\\n<{delimiter}>\\n{part}\\n</{delimiter}>\\n"

    @staticmethod
    def remove_parts(
        text: str,
        delimiter: str = DELIMITER_TEMPORAL,
    ) -> str:
        """
        Remove parts from the text.
        :param text: The text.
        :param delimiter: The delimiter.
        :return: The text without the parts.
        """
        pattern = f"<{delimiter}>.*?</{delimiter}>"
        return re.sub(pattern, "", text, flags=re.DOTALL)

    @staticmethod
    def remove_all_delimiters(text: str) -> str:
        """
        Remove all delimiters from the text.
        :param text: The text.
        :return: The text without the delimiters.
        """
        pattern = f"<{PromptUtil.DELIMITER_TEMPORAL}>.*?</{PromptUtil.DELIMITER_TEMPORAL}>"
        text = re.sub(pattern, "", text, flags=re.DOTALL)
        pattern = f"<{PromptUtil.DELIMITER_PERMANENT}>.*?</{PromptUtil.DELIMITER_PERMANENT}>"
        text = re.sub(pattern, "", text, flags=re.DOTALL)
        return text

    @staticmethod
    def extract_parts(
        text: str,
        delimiter: str = DELIMITER_TEMPORAL,
    ) -> List[str]:
        """
        Extract parts from the text.
        :param text: The text.
        :param delimiter: The delimiter.
        :return: The parts.
        """
        pattern = f"<{delimiter}>(.*?)</{delimiter}>"
        matches = re.findall(pattern, text, flags=re.DOTALL)
        return matches

    @staticmethod
    def extract_first_part(
        text: str,
        delimiter: str = DELIMITER_TEMPORAL,
    ) -> Optional[str]:
        """
        Extract the first part from the text.
        :param text: The text.
        :param delimiter: The delimiter.
        :return: The first part.
        """
        parts = PromptUtil.extract_parts(text, delimiter)
        if len(parts) > 0:
            return parts[0]
        return None

