import os
import cluster_qc
from pandas import read_csv

# Get the path of the demo directory
dirname, filename = os.path.split(os.path.abspath(__file__))
storage_path=f"{dirname}/data"
polygon = read_csv(f"{storage_path}/off_bcs.csv", usecols=["latitude","longitude"])
measurements = read_csv(f"{storage_path}/measurements.csv")

# Cluster analysis
print("\033[93mAnalyzing real-time quality control data...\033[0m")
date = measurements["DATE"].str.split("-", n=2, expand=True)
measurements["YEAR"] = date[0]
measurements["MONTH"] = date[1]
measurements = cluster_qc.cluster_analysis(measurements, storage_path, depth=-1700)
print("\033[92mAnalyzed successfully!\033[0m")

filtered_measurements = read_csv(f"{storage_path}/filtered_measurements.csv")
print(filtered_measurements[filtered_measurements.CLUSTER_QC == 1])
print(filtered_measurements[filtered_measurements.CLUSTER_QC == 2])