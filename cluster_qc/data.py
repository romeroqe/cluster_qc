import os
import xarray as xr
import pandas as pd

from tqdm import tqdm
from shapely.geometry import Polygon
from shapely.vectorized import contains

from .plot import plot_filtered_profiles_data

def dataframe_to_polygon(df_polygon):
    coords = list(zip(df_polygon["longitude"], df_polygon["latitude"]))

    if coords[0] != coords[-1]:
        coords.append(coords[0])

    return Polygon(coords)

def extract_profile_data(file_path):
    try:
        with xr.open_dataset(file_path, decode_times=True) as ds:
            mode = ds["DATA_MODE"].values[0].decode().strip()

            if mode == "R":
                pres = ds["PRES"]
                temp = ds["TEMP"]
                psal = ds["PSAL"]
            else:
                pres = ds["PRES_ADJUSTED"]
                temp = ds["TEMP_ADJUSTED"]
                psal = ds["PSAL_ADJUSTED"]

            pres = pres.isel(N_PROF=0)
            temp = temp.isel(N_PROF=0)
            psal = psal.isel(N_PROF=0)

            valid = ((pres > 0) & (temp > 0) & (psal > 0))

            df = pd.DataFrame({
                "PLATFORM_NUMBER": ds["PLATFORM_NUMBER"].values[0].decode().strip(),
                "CYCLE_NUMBER": int(ds["CYCLE_NUMBER"].values[0]),
                "DATA_MODE": mode,
                "DATE": ds["JULD"].values[0],
                "LATITUDE": ds["LATITUDE"].values[0],
                "LONGITUDE": ds["LONGITUDE"].values[0],
                "PRES": pres.where(valid).dropna(dim="N_LEVELS").values,
                "TEMP": temp.where(valid).dropna(dim="N_LEVELS").values,
                "PSAL": psal.where(valid).dropna(dim="N_LEVELS").values,
            })

            return df

    except Exception as e:
        print(f"[ERROR] {file_path} -> {e}")
        return None

def get_data_from_source(files):
    dfs = []

    for file_path in tqdm(files, desc="Reading profiles", unit="file"):
        df = extract_profile_data(file_path)
        if df is not None:
            dfs.append(df)

    return pd.concat(dfs, ignore_index=True)

def get_profiles_within_polygon(data, polygon_df, storage_path, plot=True):
	fig = None
	polygon = dataframe_to_polygon(polygon_df)

	filtered_data = data[
		(data.latitude >= polygon.bounds[1]) &
		(data.latitude <= polygon.bounds[3]) &
		(data.longitude >= polygon.bounds[0]) &
		(data.longitude <= polygon.bounds[2])
	].reset_index(drop=True)

	mask = contains(
		polygon,
		filtered_data["longitude"].values,
		filtered_data["latitude"].values
	)

	filtered_profiles = filtered_data[mask]

	os.makedirs(f"{storage_path}", exist_ok=True)
	output_path = f"{storage_path}/filtered_profiles.csv"
	filtered_profiles.to_csv(output_path, index=False)

	if plot:
		fig = plot_filtered_profiles_data(polygon, filtered_profiles, data)

	return filtered_profiles, fig