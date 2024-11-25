import click

@click.command()
@click.option('--benchmark', default='fio', help='Benchmark to use. The following are supported: "ycsb", "fio", "apache"')
@click.option('--skew', default=1,  help='Skew factor of the Zipfian Distribution')
@click.option('--n', default=100, help='Range of items to sample from in the Zipfian in multiples of million (1.000.000)')
def run_benchmark(benchmark, skew, n):
    """Program to run specified 'benchmark' option with the given Zipfian 'skew' factor using the item range in 'n'. This program outputs a CSV file with 
    the following filename format: 'results_benchmark_date.csv' and following column structure 'bucket_num, cnt, rel_freq'."""
    
    click.echo("This program is not implemented")


@click.command()
@click.option('--skew', default=1,  help='Skew factor of the Zipfian Distribution')
@click.option('--n', default=100, help='Range of items to sample from in the Zipfian in multiples of million (1.000.000)')
def run_all_benchmarks(skew, n):
    """Program to run all supported benchmarks with the given Zipfian 'skew' factor using the item range in 'n'. This program outputs a series of  CSV file with 
    the following filename format: 'results_benchmark_date.csv' and following column structure 'bucket_num, cnt, rel_freq'."""
    
    click.echo("This program is not implemented")        


@click.command() 
@click.argument('filename')
def graph_result(filename):
    """Utility to plot graphs using an R script and output the results to a file with the following format: vis_benchmark_date.png. Expects a csv file named FILENAME"""
    click.echo("This program is not implemented")
