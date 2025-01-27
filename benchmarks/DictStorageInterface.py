from abc import ABC, abstractmethod

import gzip
import json
import duckdb
import csv
from pathlib import Path

class DictStorageInterface(ABC):
    """
    Abstract base class for storage methods taking a dictionary
    Subclasses must implement the following methods:
    - store
    - finalize
    """

    def __init__(self, filename : Path):
        self.filename : Path = filename

    def __init__(self, filename : Path, total : int):
        self.filename : Path = filename
        self.total : int = total

    def store(self, data : dict):
        """
        Store a batch of data. It can be called many times
        :param data: Dictionary of {value : frequency}
        """

    def finalize(self):
        """
        Finalize the storage, e.g. write the data to disk
        """


class GzipJSONStorage(DictStorageInterface):
    """
    Storage implementation that writes the dictionary data using gzip-compressed JSON
    """

    def __init__(self, filename : Path):
        self.filename : Path = filename
        self.file = gzip.open(self.filename, 'wt')

    def store(self, data : dict):
        for value,freq in data.items():
            self.file.write(json.dumps({value : freq}) + "\n")

    def finalize(self):
        self.file.close()


class DuckDBStorage(DictStorageInterface):
    """
    Storage implementation that writes the dictionary data using DuckDB
    Creates an in-memory table and persists it on finalize
    """

    def __init__(self, filename: Path, total: int):
        self.filename = filename
        self.total = total
        self.con = duckdb.connect(":memory:")
        # Create a table without a generated column; recalculate rel_freq at the end
        self.con.execute("""
            CREATE TABLE sampling (
                entry INTEGER PRIMARY KEY,
                cnt INTEGER DEFAULT 0,
                rel_freq DOUBLE
            )
        """)

    def store(self, data: dict):
        # Merge each entry to update or insert the count
        for value, freq in data.items():
            self.con.execute(f"INSERT INTO sampling (entry, cnt) SELECT {value}, {freq} WHERE NOT EXISTS (SELECT 1 FROM sampling WHERE entry = {value})")
            self.con.execute(f"UPDATE sampling SET cnt = cnt + {freq} WHERE entry = {value}")

    def finalize(self):
        # Recalculate rel_freq only once
        self.con.execute(f"UPDATE sampling SET rel_freq = cnt / {self.total}")
        self.con.execute(f"EXPORT DATABASE '{self.filename}'")
        self.con.close()

class CSVStorage(DictStorageInterface):
    """
    Storage implementation that writes the dictionary data using CSV
    """

    def __init__(self, filename):
        self.filename : Path = filename
        self.file = open(self.filename, 'x')
        self.writer = csv.writer(self.file)

    def store(self, data : dict):
        self.writer.writerow(["entry", "cnt", "rel_freq"])
        for value,freq in data.items():
            self.writer.writerow([value, freq, freq/self.total])

    def finalize(self):
        self.file.close()