import os
import csv
import subprocess
import matplotlib.pyplot as plt

from math import ceil
from tqdm import tqdm
from pandas import read_csv
from netCDF4 import Dataset, num2date
from multiprocessing import cpu_count, Process

from .plot import plot_filtered_profiles_data

def download_data(files, storage_path):
    # Download data from Argo rsync's server
    with tqdm(total=files.shape[0]) as pbar:
        for file in files:
            subprocess.call(["rsync", "-azh", f"vdmzrs.ifremer.fr::argo/{file}", storage_path])
            pbar.update(1)

def filter_point_in_polygon(data, start, end, polygon, thread, storage_path, file_name, source_path):
	N = len(polygon)
	with open(f'{storage_path}/{file_name}-{thread}.csv', 'a', newline='') as file:
		writer = csv.writer(file)
		for i in range(start, end):
			# Point-in-polygon filter
			if(is_inside_the_polygon(polygon, N, [data.latitude.values[i],data.longitude.values[i]])):
				writer.writerow(data.values[i])

def get_data_from_nc(data, start, end, polygon, thread, storage_path, file_name, source_path):
	with open(f'{storage_path}/{file_name}-{thread}.csv', 'a', newline='') as file:
		writer = csv.writer(file)
		measurements = []
		for k in range(start, end):
			try:
				# Extract data from NetCDF files
				nc = Dataset(f"{source_path}/{data.values[k]}")
				PLATFORM_NUMBER = nc.variables['PLATFORM_NUMBER'][:]
				CYCLE_NUMBER = nc.variables['CYCLE_NUMBER'][:]
				DATA_MODE = nc.variables['DATA_MODE'][:]
				JULD = nc.variables['JULD']
				JULD = num2date(JULD[:],JULD.units)
				LATITUDE = nc.variables['LATITUDE'][:]
				LONGITUDE = nc.variables['LONGITUDE'][:]
				PRES = nc.variables['PRES'][:]
				PRES_ADJUSTED = nc.variables['PRES_ADJUSTED'][:]
				TEMP = nc.variables['TEMP'][:]
				TEMP_ADJUSTED = nc.variables['TEMP_ADJUSTED'][:]
				PSAL = nc.variables['PSAL'][:]
				PSAL_ADJUSTED = nc.variables['PSAL_ADJUSTED'][:]
				for j in range(PRES_ADJUSTED.shape[1]):
					if(str(DATA_MODE[0], 'utf-8').strip() == 'R'):
						if(PRES[0][j] > 0 and TEMP[0][j] > 0 and PSAL[0][j] > 0):
							measurements.append([str(PLATFORM_NUMBER[0], 'utf-8').strip(),CYCLE_NUMBER[0],str(DATA_MODE[0], 'utf-8').strip(),JULD[0],LATITUDE[0],LONGITUDE[0],PRES[0][j],TEMP[0][j],PSAL[0][j]])
					else: 
						if(PRES_ADJUSTED[0][j] > 0 and TEMP_ADJUSTED[0][j] > 0 and PSAL_ADJUSTED[0][j] > 0):
							measurements.append([str(PLATFORM_NUMBER[0], 'utf-8').strip(),CYCLE_NUMBER[0],str(DATA_MODE[0], 'utf-8').strip(),JULD[0],LATITUDE[0],LONGITUDE[0],PRES_ADJUSTED[0][j],TEMP_ADJUSTED[0][j],PSAL_ADJUSTED[0][j]])
			except:
				print(f"File [error]: {data.values[k]}")
		writer.writerows(measurements)

def get_data_from_source(files, source_path, storage_path):
    columns = ['PLATFORM_NUMBER','CYCLE_NUMBER','DATA_MODE','DATE','LATITUDE','LONGITUDE','PRES','TEMP','PSAL']
    # Execute parallel computation with function "get_data_from_nc"
    exec_parallel_computation(files, columns, get_data_from_nc, storage_path, "measurements", source_path=source_path)

def get_index(storage_path):
    subprocess.call(["rsync", "-azh", "vdmzrs.ifremer.fr::argo-index/ar_index_global_prof.txt", storage_path])

def get_profiles_within_polygon(data, polygon, storage_path):
    # Maximum and minimum filter
    filtered_data = data[(data.latitude > polygon.latitude.min()) & (data.latitude < polygon.latitude.max()) & (data.longitude > polygon.longitude.min()) & (data.longitude < polygon.longitude.max())].reset_index()
    # Execute parallel computation
    exec_parallel_computation(filtered_data, filtered_data.columns, filter_point_in_polygon, storage_path, "filtered_profiles", polygon)
    filtered_profiles = read_csv(f"{storage_path}/filtered_profiles.csv")
    #Plot study area
    plot_filtered_profiles_data(polygon, filtered_profiles, data, storage_path)
    return filtered_profiles

def is_inside_the_polygon(polygon, N, p):
	xinters = 0
	counter = 0
	p1 = polygon.iloc[0]
	# Even-odd algorithm
	for i in range(1, N+1):
		p2 = polygon.iloc[i % N]
		if (p[0] > min(p1[0],p2[0])):
			if (p[0] <= max(p1[0],p2[0])):
				if (p[1] <= max(p1[1],p2[1])):
					if (p1[0] != p2[0]):
						xinters = (p[0]-p1[0])*(p2[1]-p1[1])/(p2[0]-p1[0])+p1[1]
						if (p1[1] == p2[1] or p[1] <= xinters):
							counter += 1
		p1 = p2
	return counter % 2 != 0

def exec_parallel_computation(data, columns, function, storage_path, file_name, polygon=[], source_path=""):
    # Get number of CPUs in the system
    processes = []
    cpucount = cpu_count()
    r_range = ceil(data.shape[0]/cpucount)
    # Parallel computation
    for i in range(cpucount):
        with open(f"{storage_path}/{file_name}-{i}.csv", 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(columns)
        start = i * r_range
        end = start + r_range
        if(end > data.shape[0]):
            end = data.shape[0]
        p = Process(target=function, args=(data, start, end, polygon, i, storage_path, file_name, source_path))
        processes.append(p)
        p.start()
    # Block threads until the process join() method is called
    for p in processes:
        p.join()
    # Collect parallel compute data
    filtered_profiles_path = f"{storage_path}/{file_name}.csv"
    with open(filtered_profiles_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(columns)
        for i in range(cpucount):
            writer.writerows(read_csv(f"{storage_path}/{file_name}-{i}.csv").values)
            os.remove(f"{storage_path}/{file_name}-{i}.csv")
