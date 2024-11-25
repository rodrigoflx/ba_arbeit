from setuptools import setup

setup(
    name='benchmarking',
    version='1.0',
    py_modules=['runner'],
    install_requires=[
        'Click',
    ],
    entry_points={
        'console_scripts': [
            'run_benchmark = runner:run_benchmark',
            'run_all_benchmarks = runner:run_all_benchmarks',
            'graph_result = runner:graph_result'
        ],
    },
)
