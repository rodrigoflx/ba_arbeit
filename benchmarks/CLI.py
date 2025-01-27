from datetime import datetime
import os
import subprocess
import click
from sortedcontainers import SortedDict
from definitions import ROOT_DIR, BATCH_SIZE

from definitions import StorageType, PostProcessing, EnumChoice
from DictStorageInterface import GzipJSONStorage, DuckDBStorage, CSVStorage
from PostProcessingInterface import RawOutputPostProcessor, BucketingPostProcessor

import jpype

from YCSBSampler import YCSBSampler
from ApacheSampler import ApacheSampler
from FIOSampler import FIOSampler
from RJISampler import RJISampler
from LeanStoreSampler import LeanStoreSampler
from BaseSampler import BaseSampler
from NumpySampler import NumpySampler
from RustSampler import RustSampler
from SysbenchSampler import SysbenchSampler
from PgBenchSampler import PgBenchSampler

import json

import numpy as np
from scipy.stats import entropy, ks_2samp, zipfian


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
@click.option('--storage', type=EnumChoice(StorageType), default=StorageType.CSV.value, help='Defines the type of storage to use: "csv", "gzip", "duckdb"')
@click.option('--post', type=EnumChoice(PostProcessing), default=PostProcessing.NONE.value, help='Define the type of post processing to use: "none", "bucketize"')
def sample_zipf(generator : str, skew : float, n : int, samples: int , storage : StorageType, post : PostProcessing):
    """Program to run specified 'generator' option with the given Zipfian 'skew' factor using the item range in 'n'. This program outputs a CSV file with 
    the following filename format: 'results_generator_date.csv' and following column structure 'bucket_num, cnt, rel_freq'."""

    n *= 1_000_000
    samples *= 1_000_000

    start_jvm()
    
    match storage:
        case StorageType.CSV:
            storage_type = CSVStorage(ROOT_DIR + f"/results/csv/results_{generator}_{datetime.now().strftime('%Y-%m-%d-%H-%M')}.csv")
        case StorageType.GZIP_JSON:
            storage_type = GzipJSONStorage(ROOT_DIR + f"/results/gzip/results_{generator}_{datetime.now().strftime('%Y-%m-%d-%H-%M')}.json.gz")
        case StorageType.DUCKSDB:
            storage_type = DuckDBStorage(ROOT_DIR + f"/results/ducksdb/results_{generator}_{datetime.now().strftime('%Y-%m-%d-%H-%M')}.db", samples)

    match post:
        case PostProcessing.NONE:
            post_processing = RawOutputPostProcessor()
        case PostProcessing.BUCKETIZE:
            post_processing = BucketingPostProcessor(100)
    
    match generator:
        case "ycsb":
            sampler = YCSBSampler(n, samples, skew)
        case "apache":
            sampler = ApacheSampler(n, samples, skew)
        case "fio":
            sampler = FIOSampler(n, samples, skew)
        case "rji":
            sampler = RJISampler(n, samples, skew)
        case "lean":
            sampler = LeanStoreSampler(n, samples, skew)
        case "base": 
            sampler = BaseSampler(n, samples, skew)
        case "pg_bench":
            sampler = PgBenchSampler(n, samples, skew)
        case "sysbench":
            sampler = SysbenchSampler(n, samples, skew)
        case "rust":   
            sampler = RustSampler(n, samples, skew)
        case _:
            click.echo(f"Unsupported generator {generator}. Supported generators are: 'ycsb', 'fio', 'apache', 'rji', 'lean', 'base', 'pg_bench', 'sysbench', 'rust'")

    data = SortedDict()


    for start in range(0, samples, BATCH_SIZE):
        end = min(start + BATCH_SIZE, samples)
        for _ in range(end - start):
            item = sampler.sample()
            data[item] = data.get(item, 0) + 1

        batch_result = post_processing.process(data, n)
        storage_type.store(batch_result)
        data.clear()

    storage_type.finalize()

    del sampler

    jpype.shutdownJVM()


@click.command()
@click.option('--skew', default=1,  help='Skew factor of the Zipfian Distribution')
@click.option('--n', default=100, help='Range of items to sample from in the Zipfian in multiples of million (1.000.000)')
def run_all_benchmarks(skew, n):
    """Program to run all supported generators  with the given Zipfian 'skew' factor using the item range in 'n'. This program outputs a series of  CSV file with 
    the following filename format: 'results_generator_date.csv' and following column structure 'bucket_num, cnt, rel_freq'."""
    
    click.echo("This program is not implemented")   


@click.command()
@click.option('--skew', default=1.0,  help='Skew factor of the Zipfian Distribution')
@click.option('--n', default=1, help='Range of items to sample from in the Zipfian in multiples of million (1.000.000)')
@click.option('--samples', default=1, help='Number of samples that should be taken from the distribution in multiples of million (1.000.000)')
def perf_benchmark(skew, n, samples):
    """Program to run specified 'generator' option with the given Zipfian 'skew' factor using the item range in 'n'."""

    n *= 1_000_000
    samples *= 1_000_000

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

    for generator in [BaseSampler, RustSampler, PgBenchSampler, SysbenchSampler, RJISampler, FIOSampler, LeanStoreSampler, ApacheSampler, YCSBSampler]:
        sampler = generator(n, samples, skew)
        generator_name = generator.__name__

        benchmark_results["results"][generator_name] = sampler.benchmark()

    jpype.shutdownJVM()

    # Output JSON to file
    output_path = ROOT_DIR + f"/results/benchmarks/perf_{datetime.now().strftime('%Y-%m-%d-%H-%M')}.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(benchmark_results, f, indent=2)


@click.command()
@click.option('--skew', default=1,  help='Skew factor of the Zipfian Distribution')
@click.option('--n', default=100, help='Range of items to sample from in the Zipfian in multiples of million (1.000.000)')
def run_all_benchmarks(skew, n):
    """Program to run all supported generators  with the given Zipfian 'skew' factor using the item range in 'n'. This program outputs a series of  CSV file with 
    the following filename format: 'results_generator_date.csv' and following column structure 'bucket_num, cnt, rel_freq'."""
    
    click.echo("This program is not implemented")        


@click.command()
@click.option('--skew', default=1.0,  help='Skew factor of the Zipfian Distribution')
@click.option('--n', default=1, help='Range of items to sample from in the Zipfian in multiples of million (1.000.000)')
@click.option('--samples', default=1, help='Number of samples that should be taken from the distribution in multiples of million (1.000.000)')
def acc_benchmark(skew, n, samples):
    """Program to run specified 'generator' option with the given Zipfian 'skew' factor using the item range in 'n'."""

    n *= 1000000
    samples *= 1000000

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
    
    theoretical_probs = zipfian.pmf(np.arange(1, n + 1), a=skew, n=n)

    for generator in [BaseSampler, RustSampler, PgBenchSampler, SysbenchSampler, RJISampler, FIOSampler, LeanStoreSampler, ApacheSampler, YCSBSampler]:
        sampler = generator(n, samples, skew)
        generator_name = generator.__name__

        benchmark_results["results"][generator_name] = {}

        # Sample from generator and store it in a balanced binary tree
        empirical_counts = np.zeros(n)
        for _ in range(samples):
            item = sampler.sample()
            empirical_counts[item - 1] += 1

        empirical_probs = empirical_counts / samples

        #Kullback-Leibler Divergence
        kl = entropy(empirical_probs + 1e-12, theoretical_probs + 1e-12)  # Add epsilon to avoid log(0)

        # Kolmogorov-Smirnov Test
        ks, _ = ks_2samp(empirical_probs, theoretical_probs)

        benchmark_results["results"][generator_name]["kl_divergence"] = kl
        benchmark_results["results"][generator_name]["ks_test"] = float(ks)


    # Output JSON to file
    output_path = ROOT_DIR + f"/results/benchmarks/perf_{datetime.now().strftime('%Y-%m-%d-%H-%M')}.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(benchmark_results, f, indent=2)

    jpype.shutdownJVM()

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