import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

from matplotlib.widgets import Slider

# ------------------------
# Storm Color by Intensity
# ------------------------
def get_color_by_wind(wind):
    if wind <= 30:
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
                    press_str = parts[7].strip()

                    try:
                        lat = float(lat_str[:-1]) * (1 if lat_str[-1] == 'N' else -1)
                        lon = float(lon_str[:-1]) * (-1 if lon_str[-1] == 'W' else 1)
                        wind = int(wind_str)
                        date = parts[0].strip()
                        time = parts[1].strip()
                        timestamp = f"{date} {time}"
                        pressure = int(press_str)
                        pressure = None if pressure == -999 else pressure
                        
                        storm_points.append({
                            "lat": lat, 
                            "lon": lon, 
                            "wind": wind,
                            "pressure": pressure,
                            "timestamp": timestamp
                        })
                        
                    except ValueError:
                        pressure = None
                        pass

                    i += 1

                if storm_points:
                    storms.append({
                        "id": storm_id,
                        "name": storm_name,
                        "points": storm_points,
                        "lines": []
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

            line_obj = ax.plot([prev["lon"], curr["lon"]], [prev["lat"], curr["lat"]],
                        color=color, linewidth=2.2, transform=ccrs.PlateCarree()
            )[0]
                        
            storm["lines"].append({
                "line": line_obj,
                "wind": curr["wind"],
                "timestamp": curr["timestamp"],
                "name": storm["name"],
                "lat": curr["lat"],
                "lon": curr["lon"],
                "pressure": curr["pressure"]
            })
            
        ax.text(
            points[0]["lon"], points[0]["lat"], storm["name"],
            fontsize=10, color='black', ha='center', va='center', transform=ccrs.PlateCarree()
        )
    plt.draw()

# ------------------------
# Hover Event
# ------------------------
def on_hover(event, current_storms, ax, tooltip):
    if event.inaxes != ax:
        tooltip.set_visible(False)
        plt.draw()
        return
    
    found = False
    
    for storm in current_storms:
        for segment in storm["lines"]:
            line = segment["line"]
            wind = segment["wind"]
            
            if line.contains(event)[0]:
                line.set_color("magenta")
                
                pressure = segment.get("pressure")
                pres_txt = f'Pressure: {segment["pressure"]} hPa' if segment["pressure"] is not None else 'Pressure: N/A'
                
                tooltip.xy = (segment["lon"], segment["lat"])
                tooltip.set_text(
                    f'{segment["name"]}\n'
                    f'{segment["timestamp"]}\n'
                    f'Wind: {segment["wind"]} kts\n'
                    f'{pres_txt}'
                )
                tooltip.set_visible(True)
                found = True
            else:
                line.set_color(get_color_by_wind(wind))
                
    if not found:
        tooltip.set_visible(False)
    plt.draw()

# ------------------------
# Click Event
# ------------------------
def on_click(event, current_storms, ax, tooltip):
    if event.inaxes != ax:
        return
    
    for storm in current_storms:
        for segment in storm["lines"]:
            
            line = segment["line"]
            
            if line.contains(event)[0]:
                print(f'Selected Storm: {storm["name"]}')
                ax.set_title(f'Selected Storm: {storm["name"]}', fontsize=16)
                plt.draw()

# ------------------------
# Slider Update
# ------------------------
def update(value, hurdat_file, ax, fig, events, tooltip):
    year = int(slider.val)
    data["storms"] = parse_hurdat2(hurdat_file, year)
    plot_storms(data["storms"], year, ax)
    
    tooltip = ax.annotate(
        "", xy=(0, 0), xytext=(10, 10), textcoords="offset points",
        bbox=dict(boxstyle="round", fc="w"), arrowprops=dict(arrowstyle="->"),
        ha="left", fontsize=9, visible=False
    )
    
    for cid in events:
        fig.canvas.mpl_disconnect(cid)
    
    hover_cid = fig.canvas.mpl_connect("motion_notify_event", lambda event: on_hover(event, data["storms"], ax, tooltip))
    click_cid = fig.canvas.mpl_connect("button_press_event", lambda event: on_click(event, data["storms"], ax, tooltip))
    
    events.clear()
    events.extend([hover_cid, click_cid])
    
    # Refresh Layout
    plt.draw()
    fig.canvas.flush_events()

# ------------------------
# Main Execution
# ------------------------
if __name__ == "__main__":
    initial_year = 1851  # Initial Year in the HURDAT2 Database
    hurdat_file = "/home/jaredbaker/Documents/VSCode/Python/ESCI495/hurdat2-1851-2024-040425.txt"

    fig, ax = plt.subplots(figsize=(12, 9), subplot_kw={'projection': ccrs.PlateCarree()})
    events = []

    data = {"storms": parse_hurdat2(hurdat_file, initial_year)}
    plot_storms(data["storms"], initial_year, ax)
    
    ax_slider = plt.axes([0.1, 0.01, 0.8, 0.03], facecolor='lightgoldenrodyellow')
    slider = Slider(ax_slider, 'Year', 1851, 2024, valinit=initial_year, valstep=1)
    slider.on_changed(lambda val: update(val, hurdat_file, ax, fig, events, tooltip))
    
    hover_cid = fig.canvas.mpl_connect("motion_notify_event", lambda event: on_hover(event, data["storms"], ax, tooltip))
    click_cid = fig.canvas.mpl_connect("button_press_event", lambda event: on_click(event, data["storms"], ax, tooltip))
    events.extend([hover_cid, click_cid])
    
    tooltip = ax.annotate(
        "", xy=(0, 0), xytext=(15, 15), textcoords="offset points",
        ha="left", va="bottom", bbox=dict(boxstyle="round", fc="w"),
        arrowprops=dict(arrowstyle="->")
    )
    tooltip.set_visible(False)
    
    plt.show()
