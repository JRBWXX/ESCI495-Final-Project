# ESCI495-Final-Project
Repository for the final project in ESCI495 Data Analysis and Visualization

This repository is for easy access to these files across different devices and shows the process in creating the final project for my Data Analysis and Visualization class. This project tracks previous Atlantic Hurricanes using the National Hurricane Center's Atlantic Hurricane Database (HURDAT2).

Version 1 of the program is a demonstration of the Tropycal Python package for individual hurricane season analysis, individual storm tracks, and gridded analyses of tropical cyclone data. This utilizes both the HURDAT and IBTrACS Datasets to create these plots. _Visualized in a Jupyter Notebook as Tropycal would not output when running in a terminal_.

Version 2 of the program is a made from scratch hurricane track plotter using Matplotlib and Cartopy which parses the HURDAT2 text file courtesy of the NHC to extract the storm name, date and time, data points, and wind speeds and plots them using a function which determines the colors of each line segment based on the wind speeds of the data point(s). A slider is included at the bottom which enables users to pick the year from 1851-2024.

Version 3 is similar to Version 2 but it adds more interactivity allowing the user to hover over segments of the tracks which highlights the track segment and displaying storm information (name, date & time, wind speed, atmospheric pressure) at that specific point. Additionally, users can click on the track to change the title to the clicked storm.

Additional features are planned and are in progress!
