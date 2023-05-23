import pandas as pd
import json
import streamlit as st
from streamlit_folium import folium_static
import folium
from utils import *
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(layout='wide', initial_sidebar_state='expanded')

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
st.sidebar.header('Santa Clara University')

st.sidebar.subheader('Choose the Year')
# Read the data
data = pd.read_csv('assign2_wastedata.csv', parse_dates=['Date'], infer_datetime_format=True)

# Get the unique years from the data
years = data['Date'].dt.year.unique()
# Calculate the sum of waste weights for each year
yearly_weight_dict = {}
for year in years:
    yearly_weight_dict[year] = data[data['Date'].dt.year == year]['Weight'].sum()

# Sort the years based on the weight of waste
sorted_years = sorted(years, key=lambda year: yearly_weight_dict[year], reverse=True)

def get_available_buildings(year):
    
    # Convert 'Date' column to datetime type
    data['Date'] = pd.to_datetime(data['Date'])

    # Filter the data for the selected year
    data_selected_year = data[data['Date'].dt.year == year]

    # Get the unique building names for the selected year
    available_buildings = data_selected_year['Building'].unique()

    return available_buildings

# Update the selected_year variable with the sorted years
selected_year = st.sidebar.selectbox('Select Year', sorted_years)

# Filter the data for the selected year
filtered_data = data[data['Date'].dt.year == selected_year]

# Group the data by building and calculate the total weight
grouped_data = data.groupby('Building')['Weight'].sum().reset_index()

# Load the GeoJSON file with building polygons
with open('building_geojson.json') as f:
    geojson_data = json.load(f)


# Create a dictionary to store the sum of waste weights for each building
building_weight_dict = {}

# Calculate the sum of waste weights for each building
for building in filtered_data['Building'].unique():
    building_weight_dict[building] = filtered_data[filtered_data['Building'] == building]['Weight'].sum()

# Create a DataFrame from the building_weight_dict
building_weight_df = pd.DataFrame.from_dict(building_weight_dict, orient='index', columns=['Weight Sum'])
building_weight_df.index.name = 'Building'

# Reset the index to make 'Building' a column
building_weight_df.reset_index(inplace=True)

# Find the building with the highest waste in the selected year
building_with_highest_waste = building_weight_df.loc[building_weight_df['Weight Sum'].idxmax(), 'Building']
highest_waste = building_weight_df['Weight Sum'].max()

# Create the map centered at Santa Clara University
map_center = [37.3496, -121.9375]
m = folium.Map(location=map_center, zoom_start=16, tiles='CartoDB positron')
# Create a function to generate a donut chart of waste distribution



choropleth = folium.Choropleth(
    geo_data="building_geojson.json",
    data=building_weight_df,
    columns=['Building', 'Weight Sum'],
    key_on='feature.properties.Building',
    highlight=True,
    fill_color='YlGnBu',
    fill_opacity=1,
    line_opacity=0.2,
    legend_name='Weight Sum',
    nan_fill_color='lightgrey',  # Color for buildings with no data
    nan_fill_opacity=0.7,
).add_to(m)



# Adding weight of the waste to the tooltip
for feature in choropleth.geojson.data['features']:
    building = feature['properties']['Building']
    filtered_row = building_weight_df[building_weight_df['Building'] == building]
   
    weight_sum = filtered_row['Weight Sum'].values[0] if not filtered_row.empty else 'No Data'
    weight_sum = round(weight_sum, 2) if isinstance(weight_sum, float) else weight_sum
    feature['properties']['Weight'] = str(weight_sum)+' lbs'

choropleth.geojson.add_child(folium.features.GeoJsonTooltip(['Building', 'Weight']))
choropleth.geojson.add_to(m)



# Color the buildings with no data using the lightest color
for feature in choropleth.geojson.data['features']:
    building = feature['properties']['Building']
    weight = feature['properties']['Weight']
    if weight == 'No Data':
        feature['properties']['Weight'] = 'No Data'
        feature['properties']['style'] = {'fillColor': color_map.rgb_hex_str(0)}
st.header("Waste Analysis Santa Clara University")


# Calculate classification and missclassification
correct_class = get_waste_sum_by_category(selected_year)
missclassification = find_most_incorrectly_classified_stream(selected_year)
 


# Calculate Total Waste
total_waste= calculate_total_waste(selected_year)
def draw_missclassification_line_chart(year):
    # Read the data
    data = pd.read_csv('assign2_wastedata.csv')

    # Convert 'Date' column to datetime type
    data['Date'] = pd.to_datetime(data['Date'])

    # Filter the data for the selected year
    data_selected_year = data[data['Date'].dt.year == year]

    # Define the excluded streams
    excluded_streams = ['Landfill', 'Compost', 'Recycling']

    # Filter the data for streams other than the excluded ones
    data_filtered = data_selected_year[~data_selected_year['Stream'].isin(excluded_streams)]

    # Group the data by waste stream and building, and calculate the total weight
    grouped_data = data_filtered.groupby(['Stream', 'Building'])['Weight'].sum().reset_index()

    # Sort the data by the total weight in descending order
    grouped_data.sort_values('Weight', ascending=False, inplace=True)

    # Create the line chart
    plt.figure(figsize=(12, 6))

    # Generate unique colors for each waste stream
    num_streams = len(grouped_data['Stream'].unique())
    colors = sns.color_palette('tab10', n_colors=num_streams)

    # Loop through each waste stream and plot the line graph with shading
    for i, (stream, color) in enumerate(zip(grouped_data['Stream'].unique(), colors)):
        stream_data = grouped_data[grouped_data['Stream'] == stream]
        plt.plot(stream_data['Building'], stream_data['Weight'], marker='o', label=stream, color=color)
        plt.fill_between(stream_data['Building'], stream_data['Weight'], alpha=0.3, color=color)

    # Set the chart title and labels
    plt.title(f"Misclassification in {year}")
    plt.xlabel('Building')
    plt.ylabel('Weight')

    # Rotate the x-axis labels for better visibility
    plt.xticks(rotation=45)

    # Add a legend
    plt.legend()

    # Show the chart
    st.pyplot(plt)

def draw_correct_classification_donut_chart(year, building):
    # Read the data
    data = pd.read_csv('assign2_wastedata.csv')

    # Convert 'Date' column to datetime type
    data['Date'] = pd.to_datetime(data['Date'])

    # Filter the data for the selected year and building
    data_selected = data[(data['Date'].dt.year == year) & (data['Building'] == building)]

    # Calculate the correct classification weights
    landfill_weight = data_selected[data_selected['Stream'] == 'Landfill']['Weight'].sum()
    recycle_weight = data_selected[data_selected['Stream'] == 'Recycle']['Weight'].sum()
    compost_weight = data_selected[data_selected['Stream'] == 'Compost']['Weight'].sum()

    # Create the donut chart
    labels = ['Landfill', 'Recycle', 'Compost']
    sizes = [landfill_weight, recycle_weight, compost_weight]
    colors = ['#4adede', '#797ef6', '#e63b60']  # Attractive shades of blue and green
    explode = (0.1, 0, 0)  # explode the first slice (Landfill)
    radius = 0.7  # radius for the donut chart

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(sizes, labels=labels, colors=colors, explode=explode, autopct='%1.1f%%', startangle=90, wedgeprops=dict(width=radius))
    ax.set_title(f'Correct Classification of Waste in {year} ({building})')

    # Set aspect ratio to be equal to draw a circle
    ax.set_aspect('equal')

    # Show the chart
    plt.show()





# Row A

col1, col2, col3 = st.columns(3)
col1.metric("Total Waste in Year", "📆 "+str(total_waste) + " lbs",  str(selected_year))
col2.metric("Building With Highest Waste", "🏢 "+str(highest_waste.round(2)) + " lbs",  str(building_with_highest_waste))
col3.metric("Most missclassified waste stream","🗑️ "+ str(round(missclassification.get('Most Misclassified Stream')['Weight'],2)) + " lbs",missclassification.get('Most Misclassified Stream')['Stream'])

# Row B
seattle_weather = pd.read_csv('https://raw.githubusercontent.com/tvst/plost/master/data/seattle-weather.csv', parse_dates=['date'])
stocks = pd.read_csv('https://raw.githubusercontent.com/dataprofessor/data/master/stocks_toy.csv')

st.markdown('### Waste Distribution across Buildings in SCU')
folium_static(m)
# c1 = st.columns(1)
# with c1:
def draw_donut_chart(year, building):
    # Read the data
    data = pd.read_csv('assign2_wastedata.csv')

    # Convert 'Date' column to datetime type
    data['Date'] = pd.to_datetime(data['Date'])

    # Filter the data for the selected year and building
    data_selected_year_building = data[(data['Date'].dt.year == year) & (data['Building'] == building)]

    # Count the correct classification of Landfill, Recycle, and Compost
    correct_classification = data_selected_year_building[(data_selected_year_building['Stream'] == 'Landfill')
                                                         | (data_selected_year_building['Stream'] == 'Recycle')
                                                         | (data_selected_year_building['Stream'] == 'Compost')]

    # Calculate the total weight of the correct classification
    total_weight = correct_classification['Weight'].sum()

    # Calculate the weight distribution of the correct classification
    weight_distribution = correct_classification.groupby('Stream')['Weight'].sum()

    # Create the donut chart
    plt.figure(figsize=(8, 8))
    plt.pie(weight_distribution, labels=weight_distribution.index, autopct='%1.1f%%', startangle=90,
            colors=['#77BEDB', '#6ACCA7', '#99D2A0'], wedgeprops={'edgecolor': 'white'})
    plt.title(f"Correct Classification in {year} - {building}")

    # Draw a white circle at the center to make the chart hollow
    center_circle = plt.Circle((0, 0), 0.7, color='white')
    fig = plt.gcf()
    fig.gca().add_artist(center_circle)

    # Show the chart
    st.pyplot(fig)

def draw_donut_chart_miss(year, building):
    # Read the data
    data = pd.read_csv('assign2_wastedata.csv')

    # Convert 'Date' column to datetime type
    data['Date'] = pd.to_datetime(data['Date'])

    # Filter the data for the selected year and building
    data_selected_year_building = data[(data['Date'].dt.year == year) & (data['Building'] == building)]
    misclassified_weight = calculate_misclassified_weight(year)

    # Count the correct classification of Landfill, Recycle, and Compost
    correct_classification = data_selected_year_building[(data_selected_year_building['Stream'] == 'Landfill')
                                                         | (data_selected_year_building['Stream'] == 'Recycle')
                                                         | (data_selected_year_building['Stream'] == 'Compost')]

    # Calculate the total weight of the correct classification
    total_weight = misclassified_weight['Weight'].sum()

    # Calculate the weight distribution of the correct classification
    weight_distribution = misclassified_weight.groupby('Stream')['Weight'].sum()

    # Create the donut chart
    plt.figure(figsize=(8, 8))
    plt.pie(weight_distribution, labels=weight_distribution.index, autopct='%1.1f%%', startangle=90,
            colors=['#77BEDB', '#6ACCA7', '#99D2A0'], wedgeprops={'edgecolor': 'white'})
    plt.title(f"Correct Classification in {year} - {building}")

    # Draw a white circle at the center to make the chart hollow
    center_circle = plt.Circle((0, 0), 0.7, color='white')
    fig = plt.gcf()
    fig.gca().add_artist(center_circle)

    # Show the chart
    st.pyplot(fig)

def get_area_chart(year):
    # Filter the data for the selected year and exclude Compost, Landfill, and Recycling streams
    excluded_streams = ['Compost', 'Landfill', 'Recycling']
    data_selected_year = data[(data['Date'].dt.year == year) & (~data['Stream'].isin(excluded_streams))]

    # Group data by building and stream, summing the weights
    grouped_data = data_selected_year.groupby(["Building", "Stream"])["Weight"].sum().unstack()

    # Define the base colors
    # base_colors = ['#77BEDB', '#6ACCA7', '#99D2A0', '#797EF6', '#E63B60', '#1E2F97', '#FFE45C', '#29C5F6', '#5579C6']
    base_colors = ['#73C6B6','#5DADE2','#AF7AC5','#82E0AA','#F7DC6F','#F8C471','#138D75','#85C1E9']

    # Create a list to store the shades
    shades = []

    # Generate lighter shades for each base color
    for color in base_colors:
        light_shade = sns.light_palette(color, n_colors=1)[0]
        shades.append(light_shade)

    # Create stacked area chart with the shades
    fig, ax = plt.subplots(figsize=(10, 8))
    grouped_data.plot(kind="area", stacked=True, ax=ax, color=base_colors)

    # Set chart title and axis labels
    ax.set_title(f"Misclassification of Waste Streams Across Buildings at Santa Clara University - {year}")
    ax.set_xlabel("Year")
    ax.set_ylabel("Weight (lbs)")

    # Show the chart in Streamlit
    st.pyplot(fig)
    

def draw_donut_chart_miss(year, building):
    # Calculate the misclassified weight for the selected year and building
    misclassified_weight = calculate_misclassified_weight_chart(year, building)
    print(misclassified_weight)

    # Extract the weights for landfill, compost, and recycling
    landfill_weight = misclassified_weight['Landfill']
    compost_weight = misclassified_weight['Compost']
    recycling_weight = misclassified_weight['Recycling']

    # Create the donut chart
    plt.figure(figsize=(6, 6))
    labels = ['Landfill', 'Compost', 'Recycling']
    sizes = [landfill_weight, compost_weight, recycling_weight]
    colors = ['#2c7fb8', '#41b6c4', '#a1dab4']
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90, wedgeprops=dict(width=0.3))

    # Add a circle at the center to create a donut chart
    center_circle = plt.Circle((0, 0), 0.7, color='white')
    fig = plt.gcf()
    fig.gca().add_artist(center_circle)

    # Set the chart title
    plt.title(f"Missclassification in {year} - {building}")

    # Show the chart
    st.pyplot(plt)

# Read the data to get the available years
data = pd.read_csv('assign2_wastedata.csv')
data['Date'] = pd.to_datetime(data['Date'])  # Convert 'Date' column to datetime type
years = data['Date'].dt.year.unique() 
# Streamlit app code
st.title(f'Correctly Classified Waste in Buildings in {selected_year}')
col1, col2 = st.columns(2)

available_buildings = get_available_buildings(selected_year)
selected_building = col1.selectbox('Select a building', available_buildings)

if selected_year and selected_building:
        with col1:
            draw_donut_chart(selected_year, selected_building)
       
            

st.title(f'Misclassification of waste in year {selected_year}')
            # Draw the missclassification line chart
# draw_missclassification_line_chart(selected_year)
get_area_chart(selected_year)

def get_available_buildings(year):
    # Read the data
    data = pd.read_csv('assign2_wastedata.csv')

    # Convert 'Date' column to datetime type
    data['Date'] = pd.to_datetime(data['Date'])

    # Filter the data for the selected year
    data_selected_year = data[data['Date'].dt.year == year]

    # Get the unique building names for the selected year
    available_buildings = data_selected_year['Building'].unique()

    return available_buildings
