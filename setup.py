from setuptools import setup, find_packages

setup(
    name="tradebot-nse",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'pandas',
        'numpy',
        'tradingview-ta',
        'requests',
        'plotly',
    ],
    entry_points={
        'console_scripts': [
            'tradebot=src.main:main',
        ],
    },
)
