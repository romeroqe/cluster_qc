import matplotlib.pyplot as plt

from numpy import arange
from pandas import to_datetime
from gsw import SA_from_SP, CT_from_t
from mpl_toolkits.basemap import Basemap
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

months = ["01","02","03","04","05","06","07","08","09","10","11","12"]
names = ["January","February","March","April","May","June","July","August","September","October","November","December"]

def plot_DMQC_vs_RTQC(data, xmin, xmax, ymin, ymax, storage_path, file, title):
    fig, axs = plt.subplots(4, 3, gridspec_kw={"hspace": .3, "wspace": .05}, figsize=(6.4, 7.2))
    # Plot 4x3 TS diagramas per month
    for i in [0,1,2,3]:
        for j in [0,1,2]:
            k = i * 3 + j
            axs[i,j].set_title(names[k], fontsize=10)
            axs[i,j].axis(xmin=xmin,xmax=xmax,ymin=ymin,ymax=ymax)
            axs[i,j].scatter(data[(data.MONTH==months[k]) & (data.DATA_MODE=="D")].PSAL, data[(data.MONTH==months[k]) & (data.DATA_MODE=="D")].TEMP, color="gold", s=1, marker=".")
            axs[i,j].scatter(data[(data.MONTH==months[k]) & (data.DATA_MODE!="D")].PSAL, data[(data.MONTH==months[k]) & (data.DATA_MODE!="D")].TEMP, color="indigo", s=1, marker=".")
            axs[i,j].set_ylabel("In situ temperature",fontsize=8)
            axs[i,j].set_xlabel("Practical salinity",fontsize=8)
    for ax in axs.flat:
        ax.label_outer()
    fig.suptitle(title)
    fig.savefig(f"{storage_path}/{file}.png", bbox_inches="tight")
    plt.clf()

def plot_filtered_profiles_data(polygon, filtered_profiles, data, storage_path):
    lat_max = polygon.latitude.max() + 1
    lat_min = polygon.latitude.min() - 1
    lon_max = polygon.longitude.max() + 1
    lon_min = polygon.longitude.min() - 1
    # Draw map
    fig, ax = plt.subplots()
    plt.title("Profiles within the polygon")
    map = Basemap(llcrnrlon=lon_min, llcrnrlat=lat_min, urcrnrlon=lon_max, urcrnrlat=lat_max, lat_0=(lat_max - lat_min)/2, lon_0=(lon_max-lon_min)/2, projection="mill", resolution="h", ax=ax)
    map.drawcoastlines()
    map.drawmapboundary(fill_color="white")
    map.fillcontinents(color="gray",lake_color="white")
    map.drawparallels(arange(-90,90,5),labels=[1,1,0,1])
    map.drawmeridians(arange(-180,180,5),labels=[1,1,0,1])
    # Original data
    lons, lats = map(data.longitude.values, data.latitude.values)
    map.plot(lons, lats, linestyle="None", marker=".", markersize=1, markeredgecolor="black", zorder=5)
    # Filtered profiles data
    lons, lats = map(filtered_profiles.longitude.values, filtered_profiles.latitude.values)
    map.plot(lons, lats, linestyle="None", marker=".", markersize=1, markeredgecolor="red", zorder=5)
    # Polygon
    lons, lats = map(polygon.longitude.values, polygon.latitude.values)
    map.plot(lons, lats, linewidth=1, color="royalblue", zorder=5)
    # Draw minimap
    axins = inset_axes(ax, width=1.3, height=0.9)
    map_w = Basemap(llcrnrlon=-180, llcrnrlat=-90, urcrnrlon=180, urcrnrlat=90, lat_0=90, lon_0=180, projection="mill", resolution="l", ax=axins)
    map_w.drawcoastlines(linewidth=.05)
    map_w.drawmapboundary(fill_color="white")
    map_w.fillcontinents(color="gray",lake_color="white")
    # Original data
    lons, lats = map_w(data.longitude.values, data.latitude.values)
    map_w.plot(lons, lats, linestyle="None", marker=".", markersize=0.01, markeredgecolor="black", zorder=5)
    # Filtered profiles data
    lons, lats = map_w(filtered_profiles.longitude.values, filtered_profiles.latitude.values)
    map_w.plot(lons, lats, linestyle="None", marker=".", markersize=0.01, markeredgecolor="red", zorder=5)
    # Polygon
    lons, lats = map_w(polygon.longitude.values, polygon.latitude.values)
    map_w.plot(lons, lats, linewidth=1, color="royalblue", zorder=5)
    fig.savefig(f"{storage_path}/study_area.png", bbox_inches="tight")
    plt.clf()

def plot_six_diagrams(measurements, storage_path):
    measurements = measurements.reset_index()
    length = len(measurements.CYCLE_NUMBER.unique())
    measurements["DATE"] = to_datetime(measurements.DATE)
    PLATFORM_NUMBER = measurements.PLATFORM_NUMBER[0]
    FIRST_DATE = measurements.DATE.min()
    LAST_DATE = measurements.DATE.max()
    coordinates = measurements.groupby(["CYCLE_NUMBER","LATITUDE","LONGITUDE"]).size().reset_index()
    measurements["PRES"] = -measurements.PRES
    # Calculate absolute salinity
    measurements["PSAL"] = SA_from_SP(measurements.PSAL, measurements.PRES, measurements.LONGITUDE, measurements.LATITUDE)
    # Calculate conservative temperature
    measurements["TEMP"] = CT_from_t(measurements.PSAL, measurements.TEMP, measurements.PRES)
    # Plot conservative temperature vs depth diagram
    for i in range(length):
        plt.plot(measurements[measurements.CYCLE_NUMBER == i].TEMP, measurements[measurements.CYCLE_NUMBER == i].PRES, linewidth=0.5)
    plt.ylim(measurements.PRES.min(),0)
    fig = plt.gcf()
    plt.title(f"Argo float {PLATFORM_NUMBER} {FIRST_DATE.strftime('%m/%d/%Y')}-{LAST_DATE.strftime('%m/%d/%Y')}")
    plt.xlabel("Conservative temperature, Θ(°C))")
    plt.ylabel("Depth (Meters)")
    fig.savefig(f"{storage_path}/tempvsdepth.png", bbox_inches="tight")
    plt.clf()
    # Plot absolute salinity vs depth diagram
    for i in range(length):
        plt.plot(measurements[measurements.CYCLE_NUMBER == i].PSAL, measurements[measurements.CYCLE_NUMBER == i].PRES, linewidth=0.5)
    plt.ylim(measurements.PRES.min(),0)
    fig = plt.gcf()
    plt.title(f"Argo float {PLATFORM_NUMBER} {FIRST_DATE.strftime('%m/%d/%Y')}-{LAST_DATE.strftime('%m/%d/%Y')}")
    plt.xlabel("Absolute salinity, Sᴀ(g kg⁻¹)")
    plt.ylabel("Depth (Meters)")
    fig.savefig(f"{storage_path}/salvsdepth.png", bbox_inches="tight")
    plt.clf()
    # Plot conservative temperature vs absolute salinity
    for i in range(length):
        plt.plot(measurements[measurements.CYCLE_NUMBER == i].PSAL, measurements[measurements.CYCLE_NUMBER == i].TEMP, linewidth=0.5)
    fig = plt.gcf()
    plt.title(f"Argo float {PLATFORM_NUMBER} {FIRST_DATE.strftime('%m/%d/%Y')}-{LAST_DATE.strftime('%m/%d/%Y')}")
    plt.xlabel("Conservative temperature, Θ(°C)")
    plt.ylabel("Absolute salinity, Sᴀ(g kg⁻¹)")
    fig.savefig(f"{storage_path}/tempvssal.png", bbox_inches="tight")
    plt.clf()
    # Plot trajectory
    lat_min = coordinates.LATITUDE.min() - .5
    lat_max = coordinates.LATITUDE.max() + .5
    lon_min = coordinates.LONGITUDE.min() - 2
    lon_max = coordinates.LONGITUDE.max() + 2
    fig, ax = plt.subplots()
    map = Basemap(llcrnrlon=lon_min, llcrnrlat=lat_min, urcrnrlon=lon_max, urcrnrlat=lat_max, lat_0=(lat_max - lat_min)/2, lon_0=(lon_max-lon_min)/2, projection="mill", resolution="h", ax=ax)
    map.drawcoastlines(linewidth=.5)
    map.drawmapboundary(fill_color="white")
    map.fillcontinents(color="gray",lake_color="white")
    map.drawparallels(arange(-90,90,5),labels=[1,1,0,1])
    map.drawmeridians(arange(-180,180,5),labels=[1,1,0,1])
    lons, lats = map(coordinates.LONGITUDE.values, coordinates.LATITUDE.values)
    map.plot(lons, lats, linestyle="dashed", linewidth=.5, color="gray", marker=".", markersize=1, markeredgecolor="black", zorder=5)
    fig = plt.gcf()
    plt.title(f"Argo float {PLATFORM_NUMBER} {FIRST_DATE.strftime('%m/%d/%Y')}-{LAST_DATE.strftime('%m/%d/%Y')}")
    plt.xlabel("")
    plt.ylabel("")
    fig.savefig(f"{storage_path}/trajectory.png", bbox_inches="tight")
    plt.clf()
    # Plot conservative temperature with respect to time.
    cm = plt.cm.get_cmap("plasma")
    sc = plt.scatter(measurements.CYCLE_NUMBER, measurements.PRES, c=measurements.TEMP, marker="_", cmap=cm)
    cbar = plt.colorbar(sc)
    plt.ylim(measurements.PRES.min(),0)
    fig = plt.gcf()
    plt.title("Conservative temperature, Θ(°C)")
    plt.xlabel("Cycles")
    plt.ylabel("Depth (Meters)")
    plt.xlim([measurements.CYCLE_NUMBER.min(), measurements.CYCLE_NUMBER.max()])
    fig.savefig(f"{storage_path}/temp.png", bbox_inches="tight")
    plt.clf()
    # Plot absolute salinity with respect to time.
    sc = plt.scatter(measurements.CYCLE_NUMBER, measurements.PRES, c=measurements.PSAL, marker="_")
    cbar = plt.colorbar(sc)
    plt.ylim(measurements.PRES.min(),0)
    fig = plt.gcf()
    plt.title("Absolute salinity, Sᴀ(g kg⁻¹)")
    plt.xlabel("Cycles")
    plt.ylabel("Depth (Meters)")
    plt.xlim([measurements.CYCLE_NUMBER.min(), measurements.CYCLE_NUMBER.max()])
    fig.savefig(f"{storage_path}/sal.png", bbox_inches="tight")
    plt.clf()

