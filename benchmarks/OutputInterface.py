from abc import ABC, abstractmethod
from pathlib import Path

class OutputInterface(ABC):
    """
    Abstract base class for storage methods taking a dictionary
    Subclasses must implement the following methods:
    - store
    - finalize
    """
    @abstractmethod
    def do_nothing(self):
        pass

    def __init__(self, filename : Path):
        self.filename : Path = filename


class ParquetOutput(OutputInterface):
    def __init__(self, filename):
        super().__init__(filename)

    def do_nothing(self):
        pass

class CSVOutput(OutputInterface):
    """
    Storage implementation that writes the dictionary data using CSV
    """

    def __init__(self, filename):
        self.filename : Path = filename

    def do_nothing(self):
        pass