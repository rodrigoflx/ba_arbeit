from datetime import datetime
import os
import subprocess
import click
from sortedcontainers import SortedDict
import time

from definitions import StorageType, PostProcessing, EnumChoice
from DictStorageInterface import GzipJSONStorage, DuckDBStorage, CSVStorage
from PostProcessingInterface import RawOutputPostProcessor, BucketingPostProcessor

from YCSBSampler import YCSBSampler
from ApacheSampler import ApacheCommonRunner
from FIOSampler import FIOSampler
from RJISampler import RJISampler
from LeanStoreSampler import LeanStoreSampler
from BaseSampler import BaseSampler

from definitions import ROOT_DIR

@click.command()
@click.option('--generator', default='fio', help='Benchmark to use. The following are supported: "ycsb", "fio", "apache","rji", "lean"')
@click.option('--skew', default=1.0,  help='Skew factor of the Zipfian Distribution')
@click.option('--n', default=1, help='Range of items to sample from in the Zipfian in multiples of million (1.000.000)')
@click.option('--samples', default=1, help='Number of samples that should be taken from the distribution in multiples of million (1.000.000)')
@click.option('--storage', type=EnumChoice(StorageType), default=StorageType.CSV.value, help='Defines the type of storage to use: "csv", "gzip", "duckdb"')
@click.option('--post', type=EnumChoice(PostProcessing), default=PostProcessing.NONE.value, help='Define the type of post processing to use: "none", "bucketize"')
def sample_zipf(generator : str, skew : float, n : int, samples: int , storage : StorageType, post : PostProcessing):
    """Program to run specified 'generator' option with the given Zipfian 'skew' factor using the item range in 'n'. This program outputs a CSV file with 
    the following filename format: 'results_generator_date.csv' and following column structure 'bucket_num, cnt, rel_freq'."""

    n *= 1_000_000
    samples *= 1_000_000

    
    match storage:
        case StorageType.CSV:
            storage_type = CSVStorage(ROOT_DIR + f"/results/csv/results_{generator}_{datetime.now().strftime('%Y-%m-%d-%H-%M')}.csv")
        case StorageType.GZIP_JSON:
            storage_type = GzipJSONStorage(ROOT_DIR + f"/results/gzip/results_{generator}_{datetime.now().strftime('%Y-%m-%d-%H-%M')}.json.gz")
        case StorageType.DUCKSDB:
            storage_type = DuckDBStorage(ROOT_DIR + f"/results/ducksdb/results_{generator}_{datetime.now().strftime('%Y-%m-%d-%H-%M')}.db")

    match post:
        case PostProcessing.NONE:
            post_processing = RawOutputPostProcessor()
        case PostProcessing.BUCKETIZE:
            post_processing = BucketingPostProcessor(100)
    
    match generator:
        case "ycsb":
            sampler = YCSBSampler(n, samples, skew)
        case "apache":
            sampler = ApacheCommonRunner(n, samples, skew)
        case "fio":
            sampler = FIOSampler(n, samples, skew)
        case "rji":
            sampler = RJISampler(n, samples, skew)
        case "lean":
            sampler = LeanStoreSampler(n, samples, skew)
        case "base": 
            sampler = BaseSampler(n, samples, skew)
        case _:
            click.echo(f"Unsupported generator {generator}. Supported generators are: 'ycsb', 'fio', 'apache', 'rji', 'lean'")

    data = SortedDict()

    for i in range(samples):
        item = sampler.sample()
        data[item] = data.get(item, 0) + 1

    processed_data = post_processing.process(data, n)
    storage_type.store(processed_data, n)
    storage_type.finalize()

    del sampler


@click.command()
@click.option('--skew', default=1,  help='Skew factor of the Zipfian Distribution')
@click.option('--n', default=100, help='Range of items to sample from in the Zipfian in multiples of million (1.000.000)')
def run_all_benchmarks(skew, n):
    """Program to run all supported generators  with the given Zipfian 'skew' factor using the item range in 'n'. This program outputs a series of  CSV file with 
    the following filename format: 'results_generator_date.csv' and following column structure 'bucket_num, cnt, rel_freq'."""
    
    click.echo("This program is not implemented")        


@click.command()
@click.option('--generator', default='fio', help='Benchmark to use. The following are supported: "ycsb", "fio", "apache","rji", "lean"')
@click.option('--skew', default=1.0,  help='Skew factor of the Zipfian Distribution')
@click.option('--n', default=1, help='Range of items to sample from in the Zipfian in multiples of million (1.000.000)')
@click.option('--samples', default=1, help='Number of samples that should be taken from the distribution in multiples of million (1.000.000)')
def perf_benchmark(generator, skew, n, samples):
    """Program to run specified 'generator' option with the given Zipfian 'skew' factor using the item range in 'n'. This program outputs a CSV file with 
    the following filename format: 'results_generator_date.csv' and following column structure 'bucket_num, cnt, rel_freq'."""

    n *= 1_000_000
    samples *= 1_000_000

    match generator:
        case "ycsb":
            sampler = YCSBSampler(n, samples, skew)
        case "apache":
            sampler = ApacheCommonRunner(n, samples, skew)
        case "fio":
            sampler = FIOSampler(n, samples, skew)
        case "rji":
            sampler = RJISampler(n, samples, skew)
        case "lean":
            sampler = LeanStoreSampler(n, samples, skew)
        case "base":
            sampler = BaseSampler(n, samples, skew)
        case _:
            click.echo(f"Unsupported generator {generator}. Supported generators are: 'ycsb', 'fio', 'apache', 'rji', 'lean'")

    t1 = time.perf_counter()

    for i in range(samples):
        sampler.sample()
    
    t2 = time.perf_counter()

    elapsed_time_ms = (t2 - t1) * 1000

    click.echo(f"Time taken to sample {samples} items: {elapsed_time_ms:.3f} ms")

@click.command()
@click.argument('filenames', nargs=-1)  # Accept one or more filenames
def graph_result(filenames):
    """
    Utility to plot graphs using an R script and output the results to files with the format:
    vis_generator_date.png. Expects one or more CSV files named FILENAMES.
    """
    if not filenames:
        print("Error: Please provide at least one CSV file.")
        return

    r_script_path = os.path.join(os.path.dirname(__file__), 'plot.r')

    try:
        # Call the R script with all provided filenames
        result = subprocess.run(
            ['Rscript', r_script_path] + list(filenames),
            capture_output=True,
            text=True,
            check=True,
        )
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running the R script for generating the graph: {e.stderr}")

@click.command()
@click.argument("base", type=click.Path(exists=True))
@click.argument("to_be_compared", nargs=-1, type=click.Path(exists=True))
def graph_results_pairwise(base, to_be_compared):
    """
    Utility to plot graphs using an R script and output the results to files with the format:
    vis_generator_date.png. Expects one or more CSV files named FILENAMES.
    """
    if not to_be_compared:
        print("Error: Please provide at least one CSV file.")
        return

    r_script_path = os.path.join(os.path.dirname(__file__), 'plot_pairwise.r')

    try:
        # Call the R script with all provided filenames
        result = subprocess.run(
            ['Rscript', r_script_path, base] + list(to_be_compared),
            capture_output=True,
            text=True,
            check=True,
        )
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running the R script for generating the graph: {e.stderr}")