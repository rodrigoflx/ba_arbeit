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
    def store(self, data : dict, total : int):
        """
        Store a batch of data.
        :param data: Dictionary of {value : frequency}
        """


class GzipJSONStorage(DictStorageInterface):
    """
    Storage implementation that writes the dictionary data using gzip-compressed JSON
    """

    def __init__(self, filename : Path):
        self.filename : Path = filename
        self.file = gzip.open(self.filename, 'wt')

    def store(self, data, total):
        for value,freq in data.items():
            self.file.write(json.dumps({value : freq}) + "\n")


class DuckDBStorage(DictStorageInterface):
    """
    Storage implementation that writes the dictionary data using DuckDB
    Creates an in-memory table and persists it on finalize
    """

    def __init__(self, filename):
        self.filename = filename
        self.con = duckdb.connect(":memory:") 
        self.con.execute("""
            CREATE TABLE sampling (
                entry INTEGER,
                cnt INTEGER,
                rel_freq DOUBLE
            )
        """)

    def store(self, data, total):
        # Use executemany for batch processing without creating a full list
        self.con.executemany("""
            INSERT INTO sampling (entry, cnt, rel_freq)
            VALUES (?, ?, ?)
        """, ((value, freq, freq/total) for value, freq in data.items()))

    def finalize(self):
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

    def store(self, data : dict, total : int):
        self.writer.writerow(["entry", "cnt", "rel_freq"])
        for value,freq in data.items():
            self.writer.writerow([value, freq, freq/total])

    def finalize(self):
        self.file.close()