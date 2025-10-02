from setuptools import setup, find_packages

setup(
    name="tradebot-nse",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "numpy",
        "requests",
        "beautifulsoup4",
        "nsepython",
        "plotly",
        "python-dotenv"
    ]
)
