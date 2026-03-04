import gsw
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

from .plot import plot_DMQC_vs_RTQC

def cluster_analysis(data, storage_path, depth):
    data = data.copy()

    # Ensure depth (Z) exists
    if "Z" not in data.columns:
        data["Z"] = gsw.z_from_p(data.PRES.values, data.LATITUDE.values)

    xmin, xmax = data.PSAL.min(), data.PSAL.max()
    ymin, ymax = data.TEMP.min(), data.TEMP.max()

    profilers = []
    filtered_list = []

    # Monthly analysis 
    for month in range(1, 13):
        month_data = data[data.MONTH == month]

        if month_data.empty:
            continue

        if (month_data.DATA_MODE != "D").any():
            temp_data = month_data.copy()
            flag = True

			# Cluster analysis up to a maximum of 10 iterations
            for _ in range(10):
                if not flag:
                    break
                
				# kmeans() returns a flag that can stop the loop, original data, analyzed data and platform numbers that have had salinity drifts
                flag, original, temp_data, platform_numbers = kmeans_step(temp_data, depth)
                
				# If the loop continues, add the platform numbers to the profiler list
                if flag:
                    profilers.extend(platform_numbers)
        else:
            original = month_data
            
		# Join data
        rtqc = original[original.DATA_MODE != "D"]
        dmqc = month_data[month_data.DATA_MODE == "D"]
        filtered_list.extend([rtqc, dmqc])

    filtered_measurements = pd.concat(filtered_list, ignore_index=True)

	# Set CLUSTER_QC values
    profilers = np.unique(profilers)
    filtered_measurements["CLUSTER_QC"] = 2
    mask_good = ((filtered_measurements["DATA_MODE"] == "D") | (~filtered_measurements["PLATFORM_NUMBER"].isin(profilers)))

    filtered_measurements.loc[mask_good, "CLUSTER_QC"] = 1

    # Plots
    fig1 = plot_DMQC_vs_RTQC(data, xmin, xmax, ymin, ymax, "Original")
    fig2 = plot_DMQC_vs_RTQC(filtered_measurements, xmin, xmax, ymin, ymax, "CLUSTER_QC = 2")
    fig3 = plot_DMQC_vs_RTQC(filtered_measurements[filtered_measurements.CLUSTER_QC == 1], xmin, xmax, ymin, ymax, "CLUSTER_QC = 1")

    return filtered_measurements, [fig1, fig2, fig3]

def kmeans_step(data, depth):
    original = data
    data = data[data.Z < depth]

    if not ((data.DATA_MODE != "D").any() and (data.DATA_MODE == "D").any()):
        return False, original, pd.DataFrame(), []

	# Get mid-range of DMQC and RTQC data
    rm_d = data.loc[data.DATA_MODE == "D", "PSAL"].mean()
    rm_r = data.loc[data.DATA_MODE != "D", "PSAL"].mean()
	
	# K means algorithm
    init = np.array([[rm_d], [rm_r]])
    model = KMeans(n_clusters=2, init=init, n_init=1, random_state=0)
    labels = model.fit_predict(data[["PSAL"]])
    
	# Get data from the second group
    data = data.assign(LABEL=labels)
    grouped = (data[data.LABEL == 1].groupby(["PLATFORM_NUMBER", "CYCLE_NUMBER"]).size().reset_index())
    platform_numbers = grouped.PLATFORM_NUMBER.unique().tolist()
    
    mask = (original.PLATFORM_NUMBER.isin(grouped.PLATFORM_NUMBER) & original.CYCLE_NUMBER.isin(grouped.CYCLE_NUMBER))
    temp_data = original[mask]
    remaining = original[~mask]
    
    flag = not (temp_data.DATA_MODE == "D").any()
    
    return flag, original, remaining, platform_numbers