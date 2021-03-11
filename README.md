# cluster_qc
<a href="https://github.com/romeroqe/cluster_qc"><img src="https://shields.io/github/v/release/romeroqe/cluster_qc" alt="Release"></a>
<a href="http://creativecommons.org/licenses/by/4.0/"><img src="https://shields.io/github/license/romeroqe/cluster_qc" alt="License"></a>
<a href="https://doi.org/10.5281/zenodo.4595803"><img src="https://zenodo.org/badge/DOI/10.5281/zenodo.4595803.svg" alt="DOI"></a>

It's a package that filters profiles using a point-in-polygon algorithm, downloads source files, generates diagrams, and filters data in RTQC through cluster analysis.


## Installation

To install this package, first clone it on your computer or download the zip file. Then access to its root folder and install it with the command:

```
pip install .
```

<a href="https://www.gnu.org/software/wget/">wget</a> and <a href="https://rsync.samba.org/">rsync</a> are required for file download.

## Demos

To see package demos go to the `demo` folder and run the files:

- demo1.py: Download the list of profiles and filter them using the point-in-polygon algorithm, with the polygon of the Exclusive Economic Zone of Mexico.
- demo2.py: Download the list of profiles, filter them using the point-in-polygon algorithm, download the source files of these profiles and extract their data from NetCDF files to CSV, with the polygon of a zone off Baja California Sur, Mexico.
- demo3.py: Plot six diagrams of the data from a hydrographic autonomous profiler.
- demo4.py: Perform group analysis on the data to filter the data in RTQC that contains the same patterns as the DMQC data.

The demos files must be executed in order. Downloading the profile source files may take some time, depending on your Internet connection.

## Argo data acknowledgment
These data were collected and made freely available by the International Argo Program and the national programs that contribute to it. ([http://www.argo.ucsd.edu](http://www.argo.ucsd.edu), [http://argo.jcommops.org](http://argo.jcommops.org)). The Argo Program is part of the Global Ocean Observing System.

## License

<a rel="license" href="http://creativecommons.org/licenses/by/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International License</a>.
