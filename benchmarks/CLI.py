from datetime import datetime
import os
import subprocess
import click
from collections import Counter
from definitions import ROOT_DIR, BATCH_SIZE
import csv
import io

from definitions import OutputType, StorageType, EnumChoice
from StorageInterface import DuckDBInterface, PolarsInterface, CounterInterface, SQLITEInterface

import jpype
import json

from YCSBSampler import YCSBSampler
from ApacheSampler import ApacheSampler
from FIOSampler import FIOSampler
from RJISampler import RJISampler
from LeanStoreSampler import LeanStoreSampler
from BaseSampler import BaseSampler
from RustSampler import RustSampler
from SysbenchSampler import SysbenchSampler
from PgBenchSampler import PgBenchSampler

from scipy.stats import entropy, ks_2samp, zipfian
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

            block_size = 4096
            total_space_gib = (n * block_size) / (1024**3)

            gen_zipf_cmd = [
                "./shared/fio-genzipf",  
                "-t", "zipf",
                "-i", str(skew),
                "-g", str(total_space_gib),
                "-b", str(block_size),
                '-o', str(buckets),
                "-c"
            ]

            try:
                result = subprocess.run(
                    gen_zipf_cmd, capture_output=True, text=True, check=True
                )

            except subprocess.CalledProcessError as e:
                print(f"Error running gen-zipf: {e.stderr}")
                raise

            reader = csv.reader(io.StringIO(result.stdout))
            now = datetime.now()
            timestamp = now.strftime('%Y-%m-%d-%H-%M')

            with open(f"results_fio_{timestamp}.csv", 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                for row in reader:
                    writer.writerow(row)
            return
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
            
    match output:
        case OutputType.CSV:
            filepath = ROOT_DIR + f"/results/csv/{generator}_{datetime.now().strftime('%Y-%m-%d-%H-%M')}.csv"
        case OutputType.PARQUET:
            filepath = ROOT_DIR + f"/results/parquet/{generator}_{datetime.now().strftime('%Y-%m-%d-%H-%M')}.parquet"
    
    counter = Counter()

    if buckets != samples:
        for start in range(0, samples, BATCH_SIZE): 
            end = min(start + BATCH_SIZE, samples)
            for i in range(start, end):
                item = sampler.sample()
                index = item * buckets // n 
                if (index < buckets):
                    counter[index] += 1
                else:
                    print(f"{item}")
            
            ds.batch_insert(counter)
    else:
        for _ in range(samples):
            item = sampler.sample()
            counter[item] += 1
            ds.batch_insert(counter) 

    ds.store(filepath, output)

    match generator:
        case "ycsb", "apache":
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


    # Output JSON to file
    output_path = ROOT_DIR + f"/results/benchmarks/perf_{datetime.now().strftime('%Y-%m-%d-%H-%M')}.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(benchmark_results, f, indent=2)

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
def acc_benchmark(skew, n, samples):
    """Program to run specified 'generator' option with the given Zipfian 'skew' factor using the item range in 'n'."""

    # n *= 1000000
    # samples *= 1000000

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
        empirical_counts = Counter()
        for _ in range(samples):
            item = sampler.sample()
            empirical_counts[item - 1] += 1

        empirical_counts = np.array([empirical_counts[i] for i in range(n)]) 

        empirical_probs = empirical_counts / samples

        #Kullback-Leibler Divergence
        kl = entropy(empirical_probs + 1e-12, theoretical_probs + 1e-12) 

        # Total Variation Distance
        tvd = 0.5 * np.sum(np.abs(empirical_probs - theoretical_probs))

        # Kolmogorov-Smirnov Test
        ks, _ = ks_2samp(empirical_probs, theoretical_probs)

        benchmark_results["results"][generator_name]["kl_divergence"] = kl
        benchmark_results["results"][generator_name]["tvd"] = tvd
        benchmark_results["results"][generator_name]["ks_test"] = float(ks)

    # Output JSON to file
    output_path = ROOT_DIR + f"/results/benchmarks/perf_{datetime.now().strftime('%Y-%m-%d-%H-%M')}.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(benchmark_results, f, indent=2)

    jpype.shutdownJVM()

@click.command()
@click.option('--skew', type=float, required=True)
@click.option('--samples', type=int, required=True)
@click.option('--n', type=int, required=True)
@click.argument("filenames", nargs=-1) 
def graph_result(skew : float, samples : int, n : int, filenames : tuple[str]):
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
            [
                'Rscript', 
                r_script_path, 
                "--skew", str(skew),
                "--samples", str(samples),
                "--n", str(n)
            ] + list(filenames),
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


if __name__ == "__main__":
    sample_zipf(['--generator', 'rji', '--skew', 0.8, '--n', 1, '--samples', 1, '--storage', 'csv', '--storage', 'duckdb', '--post', 'none'])