from datetime import datetime
import os
import subprocess
import click
import csv 
import math
import io


import ctypes
from ctypes import c_long, c_double, c_char_p, Structure

class Buckets(Structure):
    _fields_ = [("arr", c_long * 100), ("sum", c_long)]

rji_runner_lib = ctypes.CDLL('./rji/librunner.so')
rji_runner_lib.sample_into_buckets_wrapper.argtypes = [c_long, c_long, c_double]
rji_runner_lib.sample_into_buckets_wrapper.restype = Buckets

rji_runner_lib.buckets_to_csv_wrapper.argtypes = [c_long, Buckets, c_char_p]
rji_runner_lib.buckets_to_csv_wrapper.restype = None

lean_runner_lib = ctypes.CDLL('./lean_store/librunner.so')
lean_runner_lib.sample_into_buckets_wrapper.argtypes = [c_long, c_long, c_double]
lean_runner_lib.sample_into_buckets_wrapper.restype = Buckets

lean_runner_lib.buckets_to_csv_wrapper.argtypes = [c_long, Buckets, c_char_p]
lean_runner_lib.buckets_to_csv_wrapper.restype = None


@click.command()
@click.option('--generator', default='fio', help='Benchmark to use. The following are supported: "ycsb", "fio", "apache","rji", "lean"')
@click.option('--skew', default=1.0,  help='Skew factor of the Zipfian Distribution')
@click.option('--n', default=1, help='Range of items to sample from in the Zipfian in multiples of million (1.000.000)')
@click.option('--samples', default=1, help='Number of samples that should be taken from the distribution in multiples of million (1.000.000)')
@click.option('--bucketize', default=False, help='If set, the program will output results in 100 buckets, otherwise each rank will be returned')
def run_benchmark(generator, skew, n, samples, bucketize):
    """Program to run specified 'generator' option with the given Zipfian 'skew' factor using the item range in 'n'. This program outputs a CSV file with 
    the following filename format: 'results_generator_date.csv' and following column structure 'bucket_num, cnt, rel_freq'."""

    n *= 1_000_000
    samples *= 1_000_000
    
    match generator:
        case "ycsb":
            jar_path = os.path.join(os.path.dirname(__file__), 'ycsb', 'YCSB-Runner.jar')
            try:
                result = subprocess.run(
                    ['java', '-jar', jar_path, str(n), str(samples), str(skew), str(bucketize)],
                    capture_output=True,
                    text=True,
                    check=True,
                    cwd='csv'
                )
            except subprocess.CalledProcessError as e:
                print(f"Error running YCSB-Runner: {e.stderr}")
        case "apache":
            jar_path = os.path.join(os.path.dirname(__file__), 'apache', 'ApacheCommonRunner.jar')
            try:
                result = subprocess.run(
                    ['java', '-jar', jar_path, str(n), str(samples), str(skew), str(bucketize)],
                    capture_output=True,
                    text=True,
                    check=True,
                    cwd='csv'
                )
            except subprocess.CalledProcessError as e:
                print(f"Error running ApacheCommonRunner: {e.stderr}")
        case "fio":
            block_size = 4096
            total_space_gib = (n * block_size) / (1024**3)
            fio_path = os.path.join(os.path.dirname(__file__), "fio", "fio-genzipf")

            if bucketize:
                gen_zipf_cmd = [
                    fio_path,
                    "-t", "zipf",
                    "-i", str(skew),
                    "-g", str(total_space_gib),
                    "-b", str(block_size),
                ]
            else:
                gen_zipf_cmd = [
                    fio_path,
                    "-t", "zipf",
                    "-i", str(skew),
                    "-g", str(total_space_gib),
                    "-b", str(block_size),
                    "c"
                ]

            try:
                result = subprocess.run(
                    gen_zipf_cmd, capture_output=True, text=True, check=True, cwd='csv'
                )

                reader = csv.reader(io.StringIO(result.stdout))
                now = datetime.now()
                timestamp = now.strftime('%Y-%m-%d-%H-%M')

                with open(f"csv/results_fio_{timestamp}.csv", 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    for row in reader:
                        writer.writerow(row)

            except subprocess.CalledProcessError as e:
                print(f"Error running gen-zipf: {e.stderr}")
                raise
        case "rji":
            if bucketize:
                buckets = rji_runner_lib.sample_into_buckets_wrapper(n, samples, skew)
                now = datetime.now()
                timestamp = now.strftime('%Y-%m-%d-%H-%M')
                rji_runner_lib.buckets_to_csv_wrapper(n, buckets, ctypes.c_char_p(f"csv/results_rji_{timestamp}.csv".encode("utf-8")))
            else:
                rji_runnner_lib.sample_raw(n,samples,skew)  
        case "lean":
            if bucketize:
                buckets = lean_runner_lib.sample_into_buckets_wrapper(n, samples, skew)
                now = datetime.now()
                timestamp = now.strftime('%Y-%m-%d-%H-%M')
                lean_runner_lib.buckets_to_csv_wrapper(n, buckets, ctypes.c_char_p(f"csv/results_lean_{timestamp}.csv".encode("utf-8"))) 
            else:
                rji_runner_lib.sample_raw(n,samples,skew)
        case _:
            click.echo(f"Unsupported generator {generator}. Supported generators are: 'ycsb', 'fio', 'apache', 'rji', 'lean'")

@click.command()
@click.option('--skew', default=1,  help='Skew factor of the Zipfian Distribution')
@click.option('--n', default=100, help='Range of items to sample from in the Zipfian in multiples of million (1.000.000)')
def run_all_benchmarks(skew, n):
    """Program to run all supported generators  with the given Zipfian 'skew' factor using the item range in 'n'. This program outputs a series of  CSV file with 
    the following filename format: 'results_generator_date.csv' and following column structure 'bucket_num, cnt, rel_freq'."""
    
    click.echo("This program is not implemented")        


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