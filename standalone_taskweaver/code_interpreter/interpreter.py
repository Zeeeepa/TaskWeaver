from abc import ABC, abstractmethod
from typing import Dict


class Interpreter(ABC):
    """
    Interpreter is the base class for all interpreters.
    """

    @abstractmethod
    def update_session_variables(self, session_variables: Dict[str, str]) -> None:
        """
        Update the session variables.
        :param session_variables: The session variables.
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """
        Close the interpreter.
        """
        pass

