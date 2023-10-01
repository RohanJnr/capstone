from abc import ABC, abstractmethod
from multiprocessing import Process


class MPClass(ABC):
    """Class that is initialized and runs as a process."""

    @abstractmethod
    def get_process(self) -> Process:
        """Start the process."""
        ...
