import os 
from enum import Enum
import click

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BATCH_SIZE = 100000000

class OutputType(Enum):
    PARQUET = "parquet"
    CSV = "csv"

class PostProcessing(Enum):
    NONE = "none" 
    BUCKETIZE = "bucketize"

class StorageType(Enum):
    POLARS = "polars"
    DUCKDB = "duckdb"
    COUNTER = "counter"
    SQLITE = "sqlite"

class EnumChoice(click.Choice):
    def __init__(self, enum_cls):
        self.enum_cls = enum_cls
        choices = [e.value for e in enum_cls]
        super().__init__(choices)

    def convert(self, value, param, ctx):
        value =  super().convert(value, param, ctx)
        return self.enum_cls(value)