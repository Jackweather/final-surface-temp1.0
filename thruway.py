from flask import Flask, send_file, render_template
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import requests
import io

# Changed app to application for Vercel compatibility
application = Flask(__name__)  

# Function to parse XML from a file or URL and extract data
def get_temperature_data_from_xml(xml_data):
    root = ET.fromstring(xml_data)

    latitudes = []
    longitudes = []
    surface_temperatures = []

    for site in root.findall('SWIS_SITE'):
        latitude = float(site.find('LATITUDE').text)
        longitude = float(site.find('LONGITUDE').text)
        surface_temp = float(site.find('SURFACE_TEMPERATURE').text)

        latitudes.append(latitude)
        longitudes.append(longitude)
        surface_temperatures.append(surface_temp)

    return latitudes, longitudes, surface_temperatures

# Function to set the color based on temperature
def get_temperature_color(surface_temp):
    if surface_temp < 32:
        return 'darkblue'  # Below freezing
    elif surface_temp <= 40:
        return 'yellow'  # Near freezing
    else:
        return 'black'  # Above freezing

# API endpoint to fetch the map
@application.route('/temperature-map', methods=['GET'])
def temperature_map():
    # Fetch XML data from a URL
    url = "https://www.thruway.ny.gov/xml/netdata/swis.xml"
    response = requests.get(url)
    xml_data = response.text

    # Get temperature data from the XML
    latitudes, longitudes, surface_temperatures = get_temperature_data_from_xml(xml_data)

    # Create a map of New York and surrounding areas
    plt.figure(figsize=(12, 10))

    # Set up a Basemap for New York and neighboring states
    m = Basemap(projection='merc', llcrnrlat=39.0, urcrnrlat=45.5,
                llcrnrlon=-80.0, urcrnrlon=-71.0, resolution='i')

    # Draw map elements
    m.drawcoastlines()
    m.drawcountries()
    m.drawstates()
    m.drawcounties()

    # Convert lat/lon to map projection
    x, y = m(longitudes, latitudes)

    # Assign custom colors based on temperature
    colors = [get_temperature_color(temp) for temp in surface_temperatures]

    # Plot surface temperature data with the custom colors
    scatter = m.scatter(x, y, c=colors, marker='o', s=100, edgecolors="black", alpha=0.7)

    # Save the plot to a BytesIO object instead of a file
    img_io = io.BytesIO()
    plt.title("Surface Temperature of New York and Neighboring States")
    plt.savefig(img_io, format='png')
    img_io.seek(0)
    plt.close()

    # Return the image as a response
    return send_file(img_io, mimetype='image/png')

# Root route to display the HTML page
@application.route('/')
def index():
    return render_template('index.html')

# Removed the __main__ block as it is not required for Vercel deployment
