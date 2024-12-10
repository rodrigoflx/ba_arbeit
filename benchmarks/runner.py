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
@click.option('--generator', default='fio', help='Benchmark to use. The following are supported: "ycsb", "fio", "apache"')
@click.option('--skew', default=1.0,  help='Skew factor of the Zipfian Distribution')
@click.option('--n', default=1, help='Range of items to sample from in the Zipfian in multiples of million (1.000.000)')
@click.option('--samples', default=1, help='Number of samples that should be taken from the distribution in multiples of million (1.000.000)')
def run_benchmark(generator, skew, n, samples):
    """Program to run specified 'generator' option with the given Zipfian 'skew' factor using the item range in 'n'. This program outputs a CSV file with 
    the following filename format: 'results_generator_date.csv' and following column structure 'bucket_num, cnt, rel_freq'."""

    n *= 1_000_000
    samples *= 1_000_000
    
    match generator:
        case "ycsb":
            jar_path = os.path.join(os.path.dirname(__file__), 'ycsb', 'YCSB-Runner.jar')
            try:
                result = subprocess.run(
                    ['java', '-jar', jar_path, str(n), str(samples), str(skew)],
                    capture_output=True,
                    text=True,
                    check=True
                )
            except subprocess.CalledProcessError as e:
                print(f"Error running YCSB-Runner: {e.stderr}")
        case "apache":
            jar_path = os.path.join(os.path.dirname(__file__), 'apache', 'ApacheCommonRunner.jar')
            try:
                result = subprocess.run(
                    ['java', '-jar', jar_path, str(n), str(samples), str(skew)],
                    capture_output=True,
                    text=True,
                    check=True
                )
            except subprocess.CalledProcessError as e:
                print(f"Error running ApacheCommonRunner: {e.stderr}")
        case "fio":
            block_size = 4096
            total_space_gib = (n * block_size) / (1024**3)

            gen_zipf_cmd = [
                "./fio/fio-genzipf",  
                "-t", "zipf",
                "-i", str(skew),
                "-g", str(total_space_gib),
                "-b", str(block_size),
                "-c"
            ]

            try:
                result = subprocess.run(
                    gen_zipf_cmd, capture_output=True, text=True, check=True
                )

                reader = csv.reader(io.StringIO(result.stdout))
                now = datetime.now()
                timestamp = now.strftime('%Y-%m-%d-%H-%M')

                with open(f"results_fio_{timestamp}.csv", 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    for row in reader:
                        writer.writerow(row)

            except subprocess.CalledProcessError as e:
                print(f"Error running gen-zipf: {e.stderr}")
                raise
        case "rji":
            buckets = rji_runner_lib.sample_into_buckets_wrapper(n, samples, skew)    
            now = datetime.now()
            timestamp = now.strftime('%Y-%m-%d-%H-%M')
            rji_runner_lib.buckets_to_csv_wrapper(n, buckets, ctypes.c_char_p(f"results_rji_{timestamp}.csv".encode("utf-8")))
        case "lean":
            buckets = lean_runner_lib.sample_into_buckets_wrapper(n, samples, skew)
            now = datetime.now()
            timestamp = now.strftime('%Y-%m-%d-%H-%M')
            lean_runner_lib.buckets_to_csv_wrapper(n, buckets, ctypes.c_char_p(f"results_lean_{timestamp}.csv".encode("utf-8"))) 
        case _:
            click.echo(f"Unsupported generator {generator}. Make sure you tipped it in correctly!")

@click.command()
@click.option('--skew', default=1,  help='Skew factor of the Zipfian Distribution')
@click.option('--n', default=100, help='Range of items to sample from in the Zipfian in multiples of million (1.000.000)')
def run_all_benchmarks(skew, n):
    """Program to run all supported generators  with the given Zipfian 'skew' factor using the item range in 'n'. This program outputs a series of  CSV file with 
    the following filename format: 'results_generator_date.csv' and following column structure 'bucket_num, cnt, rel_freq'."""
    
    click.echo("This program is not implemented")        


@click.command() 
@click.argument('filename')
def graph_result(filename):
    """Utility to plot graphs using an R script and output the results to a file with the following format: vis_generator_date.png. Expects a csv file named FILENAME"""
    r_script_path = os.path.join(os.path.dirname(__file__), 'plot.r')
    try:
        result = subprocess.run(
            ['Rscript', r_script_path, filename],
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error running the R script for generating the graph: {e.stderr}")
        
