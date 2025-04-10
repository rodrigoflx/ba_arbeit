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
            'macrobenchmark = CLI:macrobenchmark',
            'accuracy_zipf = CLI:accuracy_zipf',
        ],
    },
)
