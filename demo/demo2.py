import os
import cluster_qc
from pandas import read_csv

# Get the path of the demo directory
dirname, filename = os.path.split(os.path.abspath(__file__))
storage_path=f"{dirname}/data"

# Get the profile directory file of the Argo Global Data Assembly Center
print("\033[93mDownloading ar_index_global_prof.txt...\033[0m")
cluster_qc.get_index(storage_path=storage_path)
print("\033[92mar_index_global_prof.txt downloaded successfully!\033[0m")

# Filter the profile directory file by point-in-polygon algorithm
print("\033[93mFiltering profiles...\033[0m")
data = read_csv(f"{storage_path}/ar_index_global_prof.txt", skiprows=8)
polygon = read_csv(f"{storage_path}/off_bcs.csv", usecols=['latitude','longitude'])
filtered_profiles = cluster_qc.get_profiles_within_polygon(data, polygon, storage_path=storage_path)
print("\033[92mProfiles filtered successfully!\033[0m")

# Download source files
print("\033[93mDownloading source files...\033[0m")
cluster_qc.download_data(filtered_profiles.file, storage_path=f"{storage_path}/files")
print("\033[92mSource files downloaded successfully!\033[0m")

# Getting data from source files
print("\033[93mExtracting data from source files...\033[0m")
files = filtered_profiles.file.str.split("/", expand=True).iloc[:,-1] # Splitting file path to get only the name of the file
cluster_qc.get_data_from_source(files=files, source_path=f"{storage_path}/files", storage_path=storage_path)
print("\033[92mData extracted successfully!\033[0m")
