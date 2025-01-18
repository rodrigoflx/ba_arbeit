import os 
from enum import Enum
import click

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

class StorageType(Enum):
    GZIP_JSON = "gzip"
    DUCKSDB = "duckdb"
    CSV = "csv"

class PostProcessing(Enum):
    NONE = "none" 
    BUCKETIZE = "bucketize"

class EnumChoice(click.Choice):
    def __init__(self, enum_cls):
        self.enum_cls = enum_cls
        choices = [e.value for e in enum_cls]
        super().__init__(choices)

    def convert(self, value, param, ctx):
        value =  super().convert(value, param, ctx)
        return self.enum_cls(value)