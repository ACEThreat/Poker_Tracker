from setuptools import setup, find_packages

setup(
    name="poker_tracker",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "customtkinter>=5.2.0",
        "sqlalchemy>=2.0.0",
        "pandas>=2.0.0",
        "matplotlib>=3.7.0",
        "plotly>=5.18.0"
    ],
    entry_points={
        "console_scripts": [
            "poker_tracker=gui.main_window:main",
        ],
    },
    python_requires=">=3.8",
)
