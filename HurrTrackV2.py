import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

from matplotlib.widgets import Slider

# ------------------------
# Storm Color by Intensity
# ------------------------
def get_color_by_wind(wind):
    if wind < 30:
        return "darkblue"       # Tropical Depression
    elif wind < 70:
        return "aqua"           # Tropical Storm
    elif wind < 80:
        return "lemonchiffon"   # Category 1
    elif wind < 95:
        return "navajowhite"    # Category 2
    elif wind < 110:
        return "darkorange"     # Category 3
    elif wind < 135:
        return "orangered"      # Category 4
    else:
        return "mediumpurple"   # Category 5

# ------------------------
# Parse HURDAT2 File
# ------------------------
def parse_hurdat2(filepath, selected_year):
    storms = []

    with open(filepath, "r") as file:
        lines = file.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if ',' in line:
            header_parts = line.split(',')
            storm_id = header_parts[0].strip()
            storm_name = header_parts[1].strip()
            try:
                num_points = int(header_parts[2].strip())
            except ValueError:
                i += 1
                continue

            year = int(storm_id[4:8])
            i += 1
            storm_points = []

            if year == selected_year:
                for _ in range(num_points):
                    if i >= len(lines):
                        break
                    parts = lines[i].strip().split(',')
                    if len(parts) < 7:
                        i += 1
                        continue

                    lat_str = parts[4].strip()
                    lon_str = parts[5].strip()
                    wind_str = parts[6].strip()

                    try:
                        lat = float(lat_str[:-1]) * (1 if lat_str[-1] == 'N' else -1)
                        lon = float(lon_str[:-1]) * (-1 if lon_str[-1] == 'W' else 1)
                        wind = int(wind_str)
                        storm_points.append({"lat": lat, "lon": lon, "wind": wind})
                    except ValueError:
                        pass

                    i += 1

                if storm_points:
                    storms.append({
                        "id": storm_id,
                        "name": storm_name,
                        "points": storm_points
                    })
            else:
                i += num_points
        else:
            i += 1

    return storms

# ------------------------
# Plot Storms on Map
# ------------------------
def plot_storms(storms, year, ax):
    ax.clear()
    ax.set_title(f"Atlantic Hurricane Tracks - {year}", fontsize=16)
    ax.set_extent([-100, -10, 0, 50], crs=ccrs.PlateCarree())

    ax.add_feature(cfeature.LAND, facecolor='lightgray')
    ax.add_feature(cfeature.OCEAN)
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.gridlines(draw_labels=True)

    for storm in storms:
        points = storm["points"]
        if len(points) < 2:
            continue

        for i in range(1, len(points)):
            prev = points[i - 1]
            curr = points[i]
            color = get_color_by_wind(curr["wind"])

            ax.plot(
                [prev["lon"], curr["lon"]],
                [prev["lat"], curr["lat"]],
                color=color,
                linewidth=2.2,
                transform=ccrs.PlateCarree()
            )
            
        ax.text(
            points[0]["lon"], points[0]["lat"], storm["name"],
            fontsize=10, color='black', ha='center', va='center', transform=ccrs.PlateCarree()
        )
    plt.draw()

# ------------------------
# Slider Update
# ------------------------
def update(value, hurdat_file, ax, fig):
    year = int(slider.val)
    storms = parse_hurdat2(hurdat_file, year)
    plot_storms(storms, year, ax)
    
    # Refresh Layout
    plt.draw()
    fig.canvas.flush_events()

# ------------------------
# Main Execution
# ------------------------
if __name__ == "__main__":
    initial_year = 1851  
    hurdat_file = "/home/jaredbaker/Documents/VSCode/Python/ESCI495/hurdat2-1851-2024-040425.txt" # Change this to the correct filepath

    fig, ax = plt.subplots(figsize=(12, 9), subplot_kw={'projection': ccrs.PlateCarree()})

    storms = parse_hurdat2(hurdat_file, initial_year)
    plot_storms(storms, initial_year, ax)
    
    ax_slider = plt.axes([0.1, 0.01, 0.8, 0.03], facecolor='lightgoldenrodyellow')
    slider = Slider(ax_slider, 'Year', 1851, 2024, valinit=initial_year, valstep=1)
    slider.on_changed(lambda val: update(val, hurdat_file, ax, fig))
    
    plt.tight_layout()
    plt.show()
