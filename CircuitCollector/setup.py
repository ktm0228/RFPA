from setuptools import setup, find_packages

setup(
    name="CircuitCollector",
    version="0.1",
    # auto find modules
    packages=find_packages(),
    install_requires=[
        "jinja2",
        "toml",
        "numpy",
        "fastapi==0.118.0",
        "pydantic",
        "redis",
        "uvicorn==0.35.0",
        "anyio>=4.8,<5",
    ],
    python_requires=">=3.11",
    author="Jiyuan",
    description="Analog circuit testbench generator and simulation framework.",
)
