import duckdb
from abc import ABC, abstractmethod
from pathlib import Path
import polars as pl
from sortedcontainers import SortedDict
import sqlite3
from collections import Counter

from definitions import OutputType

class StorageInterface(ABC):
    """
    Abstract base class for storage interfaces for the following schema: "rank, count, relative frequency"
    It should provide the following methods:
    - insert
    - batch_insert
    - post_process
    """

    @abstractmethod
    def insert(self, entry: int):
        pass

    @abstractmethod
    def batch_insert(self, counter: Counter):
        pass

    @abstractmethod
    def store(self, filepath: Path, output_type: OutputType):
        pass

    @abstractmethod
    def remap_highest_freq_to_smallest_rank(self):
        pass


class SQLITEInterface(StorageInterface):
    """
    Wrapper for using SQLite as a in-memory DS
    """

    def __init__(self, total_samples: int):
        self.total_samples = total_samples
        self.con = sqlite3.connect(":memory:")
        self.con.execute("""
            CREATE TABLE sampling (
                entry INTEGER PRIMARY KEY,
                cnt INTEGER DEFAULT 0,
                rel_freq DOUBLE
            )
        """)

    def insert(self, entry: int):
        self.con.execute(f"""
            INSERT INTO sampling (entry, cnt) VALUES ({entry}, 1) 
            ON CONFLICT(entry) DO UPDATE set cnt = cnt + 1
        """)

    def batch_insert(self, counter: Counter):
        self.con.executemany("""
        INSERT INTO sampling (entry, cnt) VALUES (?, ?) 
        ON CONFLICT(entry) DO UPDATE SET cnt = cnt + excluded.cnt
    """, counter.items())


    def store(self, filepath: Path, output: OutputType):
        if output == OutputType.PARQUET:
            raise NotImplementedError("Parquet output not supported for SQLite")
        if output == OutputType.CSV:
            with open(filepath, 'x') as f:
                f.write("entry,cnt,rel_freq\n")
                for row in self.con.execute("SELECT * FROM sampling"):
                    f.write(f"{row[0]},{row[1]},{row[2]}\n")

class DuckDBInterface(StorageInterface):
    """
    Wrapper for using DuckDB as a in-memory DS
    """

    def __init__(self, total_samples: int):
        self.total_samples = total_samples
        self.con = duckdb.connect(":memory:")
        # Create a table without a generated column; recalculate rel_freq at the end
        self.con.execute("""
            CREATE TABLE sampling (
                entry INTEGER PRIMARY KEY,
                cnt INTEGER DEFAULT 0,
                rel_freq DOUBLE
            )
        """)

    def insert(self, entry: int): 
        self.con.execute(f"""
            INSERT INTO sampling (entry, cnt) VALUES ({entry}, 1) ON CONFLICT DO UPDATE SET cnt = cnt + 1 
        """)

    def batch_insert(self, entries: Counter):
        self.con.executemany("""
            INSERT INTO sampling (entry, cnt) VALUES (?, ?) 
            ON CONFLICT DO UPDATE SET cnt = cnt + excluded.cnt
        """, entries.items())
 
    def store(self, filepath : Path, output: OutputType):
        if output == OutputType.PARQUET:
            self.con.execute(f"""
                COPY sampling TO '{filepath}' (FORMAT 'parquet')
            """)
        if output == OutputType.CSV:
            self.con.execute(f"""
                COPY sampling TO '{filepath}' (FORMAT 'csv')
            """)
                    
class CounterInterface(StorageInterface):
    """
    Wrapper for using a counter as a in-memory DS
    """

    def __init__(self, total_samples: int):
        self.total_samples = total_samples
        self.data = Counter()
    
    def insert(self, entry: int):
        print("This is not implemented because a Counter is already used for batching mode and bucketing mode")
        pass

    def batch_insert(self, counter: Counter):
        # Just copy the reference
        self.data = counter 

    def store(self, filepath: Path, output: OutputType):
        if output == OutputType.PARQUET:
            raise NotImplementedError("Parquet output not supported for SortedDict")
        if output == OutputType.CSV:
            with open(filepath, 'x') as f:
                f.write("entry,cnt,rel_freq\n")
                for entry, cnt in sorted(self.data.items()):
                    f.write(f"{entry},{cnt},{cnt/self.total_samples}\n")

    def remap_highest_freq_to_smallest_rank(self):
        sorted_values = sorted(self.data.items(), key=lambda x: (-x[1], x[0]))
        mapping = {orig: new for new, (orig, _) in enumerate(sorted_values)}
        self.data = Counter({mapping[orig]: count for orig, count in self.data.items()})
                    
class PolarsInterface(StorageInterface):
    """
    Wrapper for using Polars as a in-memory DS
    """

    def __init__(self, total_samples: int):
        self.total_samples = total_samples
        self.data = pl.DataFrame({
            "entry": [],
            "cnt": []
        }).with_columns([
            pl.col("entry").cast(pl.Int64),
            pl.col("cnt").cast(pl.Int64)
        ])
    
    def insert(self, entry: int):
        if entry in self.data["entry"]:
            self.data = self.data.with_columns([
                pl.when(pl.col("entry") == entry)
                .then(pl.col("cnt") + 1)
                .otherwise(pl.col("cnt"))
                .alias("cnt")
            ])
        else:
            self.data = self.data.vstack(pl.DataFrame({
                "entry": [entry],
                "cnt": [1]
            }))

    def batch_insert(self, counter: Counter):
        for entry, cnt in counter.items():
            if entry in self.data["entry"]:
                self.data = self.data.with_columns([
                    pl.when(pl.col("entry") == entry)
                    .then(pl.col("cnt") + cnt)
                    .otherwise(pl.col("cnt"))
                    .alias("cnt")
                ])
            else:
                self.data = self.data.vstack(pl.DataFrame({
                    "entry": [entry],
                    "cnt": [cnt]
                    })
                )

    def store(self, filepath: Path, output: OutputType):
        if output == OutputType.PARQUET:
            self.data.write_parquet(filepath)
        if type(output) == OutputType.CSV:
            self.data.write_csv(filepath)