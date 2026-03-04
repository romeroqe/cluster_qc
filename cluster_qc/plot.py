import gsw
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import cartopy

def plot_DMQC_vs_RTQC(data, xmin, xmax, ymin, ymax, title):
    month_names = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    fig, axs = plt.subplots(4, 3, figsize=(12, 16), gridspec_kw={"hspace": 0.25, "wspace": 0.08})

    for idx, month in enumerate(np.arange(1, 13)):
        i = idx // 3
        j = idx % 3

        ax = axs[i, j]
        ax.set_title(month_names[idx], fontsize=9)
        month_data = data[data["MONTH"] == month]

        if not month_data.empty:
            dmqc = month_data[month_data["DATA_MODE"] == "D"]
            rtqc = month_data[month_data["DATA_MODE"] != "D"]
            
            ax.scatter(dmqc.PSAL, dmqc.TEMP, color="gold", s=1, marker=".", label="DMQC")
            ax.scatter(rtqc.PSAL, rtqc.TEMP, color="indigo", s=1, marker=".", label="RTQC")

        ax.set_xlim(xmin, xmax)
        ax.set_ylim(ymin, ymax)

    for ax in axs[:, 0]:
        ax.set_ylabel("In situ temperature (°C)", fontsize=8)

    for ax in axs[-1, :]:
        ax.set_xlabel("Practical salinity", fontsize=8)

    for ax in axs.flat:
        ax.tick_params(labelsize=7)

    fig.suptitle(title, fontsize=12)

    return fig

def plot_filtered_profiles_data(polygon, filtered_profiles, data, proj=cartopy.crs.EqualEarth(), data_crs=cartopy.crs.PlateCarree()):
    lon_min = polygon.bounds[0] - 1
    lat_min = polygon.bounds[1] - 1
    lon_max = polygon.bounds[2] + 1
    lat_max = polygon.bounds[3] + 1
    extent = [lon_min, lon_max, lat_min, lat_max]
    poly_x, poly_y = polygon.exterior.xy

    fig = plt.figure(figsize=(8, 6))
    ax = plt.axes(projection=proj)
    set_map(ax, extent, data_crs)

    ax.scatter(data.longitude, data.latitude, s=1, color="black", transform=data_crs, zorder=3)
    ax.scatter(filtered_profiles.longitude, filtered_profiles.latitude, s=1, color="red", transform=data_crs, zorder=4)
    ax.plot(poly_x, poly_y, color="royalblue", linewidth=1.5, transform=data_crs, zorder=5)

    return fig

def plot_six_diagrams(measurements, proj=cartopy.crs.EqualEarth(), data_crs=cartopy.crs.PlateCarree()):
    measurements = measurements.copy()
    measurements["DATE"] = pd.to_datetime(measurements["DATE"])

    PLATFORM_NUMBER = measurements.PLATFORM_NUMBER.iloc[0]
    FIRST_DATE = measurements.DATE.min()
    LAST_DATE = measurements.DATE.max()
    cycles = measurements["CYCLE_NUMBER"].unique()

    measurements["Z"] = gsw.z_from_p(measurements.PRES.values, measurements.LATITUDE.values)
    measurements["PSAL"] = gsw.SA_from_SP(measurements.PSAL.values, measurements.PRES.values, measurements.LONGITUDE.values, measurements.LATITUDE.values)
    measurements["TEMP"] = gsw.CT_from_t(measurements.PSAL.values, measurements.TEMP.values, measurements.PRES.values)

    fig = plt.figure(figsize=(16, 8))

    gs = fig.add_gridspec(2, 3)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    ax3 = fig.add_subplot(gs[0, 2])
    ax4 = fig.add_subplot(gs[1, 0], projection=proj)
    ax5 = fig.add_subplot(gs[1, 1])
    ax6 = fig.add_subplot(gs[1, 2])

    # Temperature vs Depth
    for c in cycles:
        sub = measurements[measurements.CYCLE_NUMBER == c]
        ax1.plot(sub.TEMP, sub.Z, lw=0.6)
    ax1.set_ylim(measurements.Z.min(), 0)
    ax1.set_xlabel("Conservative temperature Θ (°C)")
    ax1.set_ylabel("Depth (m)")
    ax1.set_title("Temperature vs Depth")

    # Salinity vs Depth 
    for c in cycles:
        sub = measurements[measurements.CYCLE_NUMBER == c]
        ax2.plot(sub.PSAL, sub.Z, lw=0.6)
    ax2.set_ylim(measurements.Z.min(), 0)
    ax2.set_xlabel("Absolute salinity (g kg⁻¹)")
    ax2.set_ylabel("Depth (m)")
    ax2.set_title("Salinity vs Depth")

    # T-S diagram
    for c in cycles:
        sub = measurements[measurements.CYCLE_NUMBER == c]
        ax3.plot(sub.PSAL, sub.TEMP, lw=0.6)
    ax3.set_xlabel("Absolute salinity (g kg⁻¹)")
    ax3.set_ylabel("Conservative temperature Θ (°C)")
    ax3.set_title("T–S Diagram")

    # Trajectory map
    set_map(ax4, [measurements.LONGITUDE.min() - 1, measurements.LONGITUDE.max() + 1, measurements.LATITUDE.min() - 1, measurements.LATITUDE.max() + 1], data_crs=cartopy.crs.PlateCarree())
    ax4.plot(measurements.LONGITUDE, measurements.LATITUDE, transform=data_crs, color="black", lw=0.7, marker="o", markersize=2)
    ax4.set_title("Trajectory")

    # Temperature vs Cycle
    sc1 = ax5.scatter(measurements.CYCLE_NUMBER, measurements.Z, c=measurements.TEMP, cmap="plasma", s=4)
    ax5.set_ylim(measurements.Z.min(), 0)
    ax5.set_xlabel("Cycle number")
    ax5.set_ylabel("Depth (m)")
    ax5.set_title("Temperature evolution")
    fig.colorbar(sc1, ax=ax5, label="Θ (°C)")

    # Salinity vs Cycle
    sc2 = ax6.scatter(measurements.CYCLE_NUMBER, measurements.Z, c=measurements.PSAL, cmap="viridis", s=4)
    ax6.set_ylim(measurements.Z.min(), 0)
    ax6.set_xlabel("Cycle number")
    ax6.set_ylabel("Depth (m)")
    ax6.set_title("Salinity evolution")
    fig.colorbar(sc2, ax=ax6, label="SA (g kg⁻¹)")

    fig.suptitle(f"Argo Float {PLATFORM_NUMBER} | {FIRST_DATE:%Y-%m-%d} – {LAST_DATE:%Y-%m-%d}", fontsize=14, fontweight="bold")
    fig.tight_layout()

    return fig
    
def set_map(ax, extent, data_crs=cartopy.crs.PlateCarree()):
    ax.set_extent(extent, crs=data_crs)
    ax.coastlines(resolution="10m", linewidth=0.6)
    ax.add_feature(cartopy.feature.LAND, facecolor="lightgray")
    ax.add_feature(cartopy.feature.OCEAN, facecolor="white")
    gl = ax.gridlines(draw_labels=True, linewidth=0.3, linestyle="--")
    gl.top_labels = False
    gl.right_labels = False