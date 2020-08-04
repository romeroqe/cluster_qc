import os
import cluster_qc
from pandas import read_csv

# Get the path of the demo directory
dirname, filename = os.path.split(os.path.abspath(__file__))
storage_path=f"{dirname}/data"
measurements = read_csv(f"{storage_path}/measurements.csv")

# Plotting diagrams for profiler "4901635"
print("\033[93mPlotting six diagrams for profiler \"4901635\"...\033[0m")
cluster_qc.plot_six_diagrams(measurements[measurements.PLATFORM_NUMBER==4901635], storage_path=storage_path)
print("\033[92mDiagrams plotted successfully!\033[0m")
