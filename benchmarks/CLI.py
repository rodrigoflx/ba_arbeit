from datetime import datetime
import os
import subprocess
import click
from collections import Counter
from definitions import ROOT_DIR, BATCH_SIZE
import csv
import io
import pandas as pd 
import re
import pathlib
from itertools import islice

from definitions import OutputType, StorageType, EnumChoice
from StorageInterface import DuckDBInterface, PolarsInterface, CounterInterface, SQLITEInterface

import jpype
import json

from YCSBSampler import YCSBSampler
from ApacheSampler import ApacheSampler
from FIOSampler import FIOSampler
from RJISampler import RJISampler
from LeanStoreSampler import LeanStoreSampler
from RejectionSampler import RejectionSampler
from MarsagliaSampler import MarsagliaSampler
from RustSampler import RustSampler
from SysbenchSampler import SysbenchSampler
from PgBenchSampler import PgBenchSampler

import scipy.stats as stats
import numpy as np

def start_jvm():
    jpype.startJVM(
        "-Xms1g",   
        "-Xmx4g",    
        jvmpath="/usr/lib/jvm/default-java/lib/server/libjvm.so", 
        classpath=[
            ROOT_DIR + "/jar/ApacheCommonRunner.jar", 
            ROOT_DIR + "/jar/YCSB-Runner.jar"
        ],
        convertStrings=True,
    )

@click.command()
@click.option('--generator', default='fio', help='Benchmark to use. The following are supported: "ycsb", "fio", "apache","rji", "lean", "base", "pg_bench", "sysbench", "rust"')
@click.option('--skew', default=1.0,  help='Skew factor of the Zipfian Distribution')
@click.option('--n', default=1, help='Range of items to sample from in the Zipfian in multiples of million (1.000.000)')
@click.option('--samples', default=1, help='Number of samples that should be taken from the distribution in multiples of million (1.000.000)')
@click.option('--output', type=EnumChoice(OutputType), default=OutputType.CSV.value, help='Defines the type of storage to use: "csv", "parquet"')
@click.option('--storage', type=EnumChoice(StorageType), default=StorageType.COUNTER.value, help='Defines the type of storage to use: "duckdb", "polars", "counter", "sqlite"')
@click.option('--buckets', default=100, help='Number of buckets to use to accumulate data')
def sample_zipf(generator : str, skew : float, n : int, samples: int , output : OutputType, storage: StorageType, buckets:int):
    """Program to run specified 'generator' option with the given Zipfian 'skew' factor using the item range in 'n'. This program outputs a CSV file with 
    the following filename format: 'results_generator_date.csv' and following column structure 'bucket_num, cnt, rel_freq'."""
    
    match storage:
        case StorageType.DUCKDB:
            ds = DuckDBInterface(samples)
        case StorageType.POLARS:
            ds = PolarsInterface(samples)
        case StorageType.COUNTER:   
            ds = CounterInterface(samples)
        case StorageType.SQLITE:
            ds = SQLITEInterface(samples)
        case _:
            click.echo(f"Unsupported storage type {storage}. Supported storage types are: 'duckdb', 'polars', 'counter', 'sqlite'")
    
    match generator:
        case "ycsb":
            start_jvm()
            sampler = YCSBSampler(n, samples, skew)
        case "apache":
            start_jvm()
            sampler = ApacheSampler(n, samples, skew)
        case "fio":
            sampler = FIOSampler(n, samples, skew)

            # block_size = 4096
            # total_space_gib = (n * block_size) / (1024**3)

            # gen_zipf_cmd = [
            #     "./shared/fio-genzipf",  
            #     "-t", "zipf",
            #     "-i", str(skew),
            #     "-g", str(total_space_gib),
            #     "-b", str(block_size),
            #     '-o', str(buckets),
            #     "-c"
            # ]

            # try:
            #     result = subprocess.run(
            #         gen_zipf_cmd, capture_output=True, text=True, check=True
            #     )

            # except subprocess.CalledProcessError as e:
            #     print(f"Error running gen-zipf: {e.stderr}")
            #     raise

            # reader = csv.reader(islice(io.StringIO(result.stdout), 2, None))

            # filepath = pathlib.Path(ROOT_DIR + f"/results/csv/{generator}/{n}_{samples}.csv")

            # with open(filepath, 'w', newline='') as csvfile:
            #     writer = csv.writer(csvfile)
            #     for row in reader:
            #         writer.writerow(row)

            # return 
        case "rji":
            sampler = RJISampler(n, samples, skew)
        case "lean":
            sampler = LeanStoreSampler(n, samples, skew)
        case "rejection": 
            sampler = RejectionSampler(n, samples, skew)
        case "marsaglia":
            sampler = MarsagliaSampler(n, samples, skew)
        case "pg_bench":
            sampler = PgBenchSampler(n, samples, skew)
        case "sysbench":
            sampler = SysbenchSampler(n, samples, skew)
        case "rust":   
            sampler = RustSampler(n, samples, skew)
        case _:
            click.echo(f"Unsupported generator {generator}. Supported generators are: 'ycsb', 'fio', 'apache', 'rji', 'lean', 'base', 'pg_bench', 'sysbench', 'rust'")
            
    match output:
        case OutputType.CSV:
            filepath = ROOT_DIR + f"/results/csv/{generator}/{n}_{samples}.csv"
        case OutputType.PARQUET:
            filepath = ROOT_DIR + f"/results/parquet/{generator}/{n}_{samples}.parquet"
    
    counter = Counter()

    if buckets != samples:
        for start in range(0, samples, BATCH_SIZE): 
            end = min(start + BATCH_SIZE, samples)
            for i in range(start, end):
                item = sampler.sample()
                index = item * buckets // n 
                if (index < buckets):
                    counter[index] += 1
            
            ds.batch_insert(counter)
    else:
        for _ in range(samples):
            item = sampler.sample()
            counter[item] += 1
            ds.batch_insert(counter) 

    # if generator == "fio":
    #     ds.remap_highest_freq_to_smallest_rank()

    ds.store(pathlib.Path(filepath), output)

    match generator:
        case "ycsb", "apache":
            jpype.shutdownJVM()
        
@click.command()
@click.option('--skew', default=1.0,  help='Skew factor of the Zipfian Distribution')
@click.option('--n', default=1, help='Range of items to sample from in the Zipfian in multiples of million (1.000.000)')
@click.option('--samples', default=1, help='Number of samples that should be taken from the distribution in multiples of million (1.000.000)')
def macrobenchmark(skew, n, samples):
    """Command to run all available generators with the given Zipfian 'skew' factor using the item range in 'n'."""

    start_jvm()

    benchmark_results = {
        "metadata": {
            "skew": skew,
            "n": n,
            "samples": samples,
            "timestamp": datetime.now().isoformat(),
        },
        "results": {}
    }

    for generator in []: #,SysbenchSampler, FIOSampler, ApacheSampler, YCSBSampler]:
        sampler = generator(n, samples, skew)
        generator_name = generator.__name__

        benchmark_results["results"][generator_name] = sampler.benchmark()


    # Output JSON to file
    output_path = ROOT_DIR + f"/results/benchmarks/perf_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(benchmark_results, f, indent=2)

    jpype.shutdownJVM()

@click.command()
@click.option('--input_file', required=True, help='Path to the Zipf distribution CSV file.')
@click.option('--skew', required=True, type=float, help='Skew factor of the Zipfian distribution.')
@click.option('--metric', type=click.Choice(['tvd', 'ks_stat', 'ks_p_value', 'all']), default='tvd', 
              help='Metric to output: total variation distance (tvd), KS statistic (ks_stat), KS p-value (ks_p_value), or all metrics.')
@click.option('--buckets', type=int, required=True, help="The number of buckets used")
def accuracy_zipf(input_file, skew, metric, buckets):
    """Evaluate accuracy (TVD, KS-test) for a single Zipf distribution CSV file."""
    
    # Extract support size and sample size from filename
    filename = os.path.basename(input_file)
    pattern = re.compile(r'(\d+[KM]?)[-_](\d+[KM]?)\.csv')
    match = pattern.match(filename)
    
    if match:
        support_str, sample_str = match.groups()
        
        if 'K' in support_str:
            support_str = support_str.replace('K', '000')
        if 'M' in support_str:
            support_str = support_str.replace('M', '000000')
    else:
        click.echo(f"Couldn't parse support and sample size from filename: {filename}")
        return
    
    # Read the CSV file
    df = pd.read_csv(input_file, skipinitialspace=True)
    
    # Get empirical probabilities
    empirical_probs = df["rel_freq"].values

    
    # Compute theoretical probabilities
    bucket_edges = np.linspace(0, int(support_str), num=buckets+1, dtype=int)
    harmonic_norm = np.sum(1 / np.arange(1, int(support_str) + 1) ** skew)
    
    theoretical_probs = [
        np.sum((1 / np.arange(start + 1, end + 1) ** skew) / harmonic_norm)
        for start, end in zip(bucket_edges[:-1], bucket_edges[1:])
    ]
    
    theoretical_probs = np.array(theoretical_probs)

    empirical_cdf = np.cumsum(empirical_probs)
    theoretical_cdf = np.cumsum(theoretical_probs)
    
    tvd = 0.5 * np.sum(np.abs(empirical_probs - theoretical_probs))
    ks_statistic = np.max(np.abs(empirical_cdf - theoretical_cdf))

    lambda_n = np.sqrt(int(sample_str)) * ks_statistic
    p_value = stats.kstwobign.sf(lambda_n)

    if metric == 'tvd' or metric == 'all':
        click.echo(f"TVD: {tvd}")
    
    if metric == 'ks_stat' or metric == 'all':
        click.echo("KS statistic: {0:.5f}".format(ks_statistic))
    
    if metric == 'ks_p_value' or metric == 'all':
        click.echo("KS p-value: {0:.5f}".format(p_value))
