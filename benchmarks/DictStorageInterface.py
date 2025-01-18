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
    def store(self, data : dict):
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

    def store(self, data):
        for value,freq in data.items():
            self.file.write(json.dumps({value : freq}) + "\n")


class DucksDBStorage(DictStorageInterface):
    """
    Storage implementation that writes the dictionary data using DucksDB
    """

    def __init__(self, filename):
        self.filename = filename
        self.con = duckdb.connect(self.filename) 


    def store(self, data):
        for value,freq in data.items():
            self.con.execute(f"INSERT INTO table VALUES ({value}, {freq})")

    def finalize(self):
        self.db.close()


class CSVStorage(DictStorageInterface):
    """
    Storage implementation that writes the dictionary data using CSV
    """

    def __init__(self, filename):
        self.filename : Path = filename
        self.file = open(self.filename, 'x')
        self.writer = csv.writer(self.file)

    def store(self, data : dict):
        self.writer.writerow(["value", "freq"])
        for value,freq in data.items():
            self.writer.writerow([value, freq])

    def finalize(self):
        self.file.close()