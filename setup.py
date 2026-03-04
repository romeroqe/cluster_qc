from setuptools import setup, find_packages

setup(
    name="cluster_qc",
    version="2.0.0",
    author="Emmanuel Romero",
    author_email="romeroqe@gmail.com",
    description=(
        "A package for spatial filtering of Argo profiles using a "
        "point-in-polygon algorithm and cluster-based quality control analysis."
    ),
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/romeroqe/cluster_qc",
    packages=find_packages(),
    install_requires=[
      "numpy",
      "pandas",
      "matplotlib",
      "cartopy",
      "gsw",
      "xarray",
      "scikit-learn",
      "tqdm",
      "shapely"
    ],
    license="CC-BY-4.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
)