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
polygon = read_csv(f"{storage_path}/eez_of_mexico.csv", usecols=['latitude','longitude'])
filtered_profiles = cluster_qc.get_profiles_within_polygon(data, polygon, storage_path=storage_path)
print("\033[92mProfiles filtered successfully!\033[0m")

print(filtered_profiles)