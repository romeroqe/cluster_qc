import matplotlib.pyplot as plt

from pandas import DataFrame
from datetime import datetime
from scipy import interpolate
from numpy import array, unique
from sklearn.cluster import k_means

from .plot import plot_DMQC_vs_RTQC

months = ["01","02","03","04","05","06","07","08","09","10","11","12"]

def cluster_analysis(data, storage_path, depth):
	data["PRES"] = -data.PRES
	xmin = data.PSAL.min()
	xmax = data.PSAL.max()
	ymin = data.TEMP.min()
	ymax = data.TEMP.max()
	# Plot original data
	plot_DMQC_vs_RTQC(data, xmin, xmax, ymin, ymax, storage_path, "original", "Original")
	
	profilers = []
	filtered_measurements = DataFrame([], columns=data.columns)
	# Evaluate every month
	for month in months:
		temp_data = month_data = data[data.MONTH == month]
		if month_data[month_data.DATA_MODE != "D"].shape[0] > 0:
			flag = True
			# Cluster analysis up to a maximum of 10 iterations
			for _ in range(1,10):
				if(flag): 
					# kmeans() returns a flag that can stop the loop, original data, analyzed data and platform numbers that have had salinity drifts
					flag, original, temp_data, platform_numbers = kmeans(temp_data, depth)
				if(flag): 
					# If the loop continues, add the platform numbers to the profiler list
					profilers = profilers + platform_numbers
				else: break
		else: original = month_data
		# Join data
		rtqc = original[original.DATA_MODE != "D"]
		dmqc = month_data[month_data.DATA_MODE == "D"]
		filtered_measurements = filtered_measurements.append(rtqc)
		filtered_measurements = filtered_measurements.append(dmqc)

	filtered_measurements.insert(filtered_measurements.shape[1], "CLUSTER_QC", [2] * filtered_measurements.shape[0])
	profilers = unique(profilers)
	
	# Set CLUSTER_QC values
	def cluster_qc(row):
		if row["DATA_MODE"] == "D":
			return 1
		if not row["PLATFORM_NUMBER"] in profilers:
			return 1
		return 2

	filtered_measurements["CLUSTER_QC"] = filtered_measurements.apply(cluster_qc, axis=1)
	filtered_measurements.to_csv(f"{storage_path}/filtered_measurements.csv")
	# Plot CLUSTER_QC = 2 data
	plot_DMQC_vs_RTQC(filtered_measurements, xmin, xmax, ymin, ymax, storage_path, "cluster_qc_2", "CLUSTER_QC = 2")
	# Plot CLUSTER_QC = 1 data
	plot_DMQC_vs_RTQC(filtered_measurements[filtered_measurements.CLUSTER_QC == 1], xmin, xmax, ymin, ymax, storage_path, "cluster_qc_1", "CLUSTER_QC = 1")
	return(filtered_measurements)

def kmeans(data, depth):
	original = data
	data = data[data.PRES < depth] 
	if data[data.DATA_MODE != "D"].shape[0] > 0 and data[data.DATA_MODE == "D"].shape[0] > 0:
		# Get mid-range of DMQC and RTQC data
		rm_d = (data[data.DATA_MODE == "D"].PSAL.max() + data[data.DATA_MODE == "D"].PSAL.min()) / 2
		rm_r = (data[data.DATA_MODE != "D"].PSAL.max() + data[data.DATA_MODE != "D"].PSAL.min()) / 2
		# K means algorithm
		init = array([[rm_d],[rm_r]])
		centroid, labels, loss = k_means(data[["PSAL"]], 2, init=init, n_init=1)
	else: return(False, original, [], [])

	data.insert(data.shape[1], "LABEL", labels)
	# Get data from the second group
	gruped = data[data.LABEL == 1].groupby(["PLATFORM_NUMBER","CYCLE_NUMBER"]).size().reset_index()
	platform_numbers = gruped.PLATFORM_NUMBER.unique().tolist()
	temp_data = original[(original.PLATFORM_NUMBER.isin(gruped.PLATFORM_NUMBER)) & (original.CYCLE_NUMBER.isin(gruped.CYCLE_NUMBER))]
	# If the second group has DMQC data, the flag is False
	flag = False if temp_data[temp_data.DATA_MODE == "D"].shape[0] > 0 else True
	# Get data from the first group
	temp_data = original[~((original.PLATFORM_NUMBER.isin(gruped.PLATFORM_NUMBER)) & (original.CYCLE_NUMBER.isin(gruped.CYCLE_NUMBER)))]
	return(flag, original, temp_data, platform_numbers)
