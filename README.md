# cluster_qc
<a href="https://github.com/romeroqe/cluster_qc"><img src="https://shields.io/github/v/release/romeroqe/cluster_qc" alt="Release"></a>
<a href="http://creativecommons.org/licenses/by/4.0/"><img src="https://shields.io/github/license/romeroqe/cluster_qc" alt="License"></a>
<a href="https://doi.org/10.5281/zenodo.4595802"><img src="https://zenodo.org/badge/DOI/10.5281/zenodo.4595802.svg" alt="DOI"></a>

Argo data goes through two quality processes, in real time and in delayed mode. This library contains the code used to develop the methodology of a publication that is currently under review, filters profiles within a given irregular polygon and offers two filtering methods to discard only the real time quality control data that present salinity drifts, this allows researchers to have a greater amount of data within the study area of their interest in a matter of minutes, as opposed to waiting for quality control in delayed mode that takes up to 12 months to complete. In addition, it provides tools to facilitate the download of the source files of this data and to generate diagrams.


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

## How to cite

> [!IMPORTANT]
> _If you use this repository, please include a reference to the following:_
> 
> Romero, E., Tenorio-Fernandez, L., Castro, I., and Castro, M.: Filtering method based on cluster analysis to avoid salinity drifts and recover Argo data in less time, Ocean Sci., 17, 1273–1284, https://doi.org/10.5194/os-17-1273-2021, 2021.

## Argo data acknowledgment
These data were collected and made freely available by the International Argo Program and the national programs that contribute to it. ([http://www.argo.ucsd.edu](http://www.argo.ucsd.edu), [http://argo.jcommops.org](http://argo.jcommops.org)). The Argo Program is part of the Global Ocean Observing System.

## License

<a rel="license" href="http://creativecommons.org/licenses/by/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International License</a>.
