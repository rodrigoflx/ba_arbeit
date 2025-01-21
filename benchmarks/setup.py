from setuptools import setup

setup(
    name='benchmarking',
    version='1.0',
    py_modules=['runner'],
    install_requires=[
        'Click',
        "matplotlib",
        "pandas",
        "JPype1",
        "sortedcontainers",
        "numpy",
        "scipy"
    ],
    entry_points={
        'console_scripts': [
            'sample_zipf = CLI:sample_zipf',
            'run_all_benchmarks = CLI:run_all_benchmarks',
            'perf_benchmark = CLI:perf_benchmark',
            'acc_benchmark = CLI:acc_benchmark',
            'graph_result = CLI:graph_result',
            'graph_results_pairwise = CLI:graph_results_pairwise',
        ],
    },
)
