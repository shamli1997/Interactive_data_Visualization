import pandas as pd

def get_waste_sum_by_category(year):
    """
    Calculate the sum of waste collected in each category ('Recycling', 'Landfill', and 'Compost') based on correctly
    classified waste for a specific year.

    Args:
        year (int): The year for which the waste sum should be calculated.

    Returns:
        dict: A dictionary containing the sum of waste collected in each category and the total waste.
    """
    # Read the data from 'assign2_wastedata.csv' file
    dataframe = pd.read_csv('assign2_wastedata.csv', parse_dates=['Date'])

    # Filter the dataframe for the specified year
    filtered_data = dataframe[dataframe['Date'].dt.year == year]

    # Filter the dataframe for correctly classified waste
    correctly_classified_data = filtered_data[
        ((filtered_data['Stream'] == 'Recycling') & (~filtered_data['Substream'].str.contains('Landfill'))) |
        ((filtered_data['Stream'] == 'Landfill') & (~filtered_data['Substream'].str.contains('Recycling'))) |
        ((filtered_data['Stream'] == 'Compost') & (~filtered_data['Substream'].str.contains('Landfill')) & (~filtered_data['Substream'].str.contains('Recycling')))
    ]

    # Calculate the sum of waste weights for each category
    waste_sum_by_category = correctly_classified_data.groupby('Stream')['Weight'].sum().round(2).to_dict()

    # Calculate the total waste for correctly classified streams
    total_waste = correctly_classified_data['Weight'].sum().round(2)

    # Add the total waste to the dictionary
    waste_sum_by_category['Total Waste'] = f"{total_waste} lbs"

    # Add "lbs" postfix to the values in the dictionary
    waste_sum_by_category = {category: f"{weight} lbs" for category, weight in waste_sum_by_category.items()}

    return waste_sum_by_category



def calculate_total_waste(year):
    """
    Calculate the total waste generated in a selected year.

    Args:
        year (int): The year for which the total waste should be calculated.

    Returns:
        str: The total waste generated in the selected year, rounded to 2 decimal places with "lbs" postfix.
    """
    # Read the data from 'assign2_wastedata.csv' file
    data = pd.read_csv('assign2_wastedata.csv', parse_dates=['Date'], infer_datetime_format=True)

    # Filter the data for the selected year
    filtered_data = data[data['Date'].dt.year == year]

    # Calculate the total waste generated
    total_waste = filtered_data['Weight'].sum().round(2)

    # Add "lbs" postfix to the total waste value
    # total_waste = f"{total_waste} lbs"
    return total_waste



def find_most_incorrectly_classified_stream(selected_year):
    # Read the waste data from the CSV file
    waste_data = pd.read_csv('assign2_wastedata.csv')

    # Filter the waste data for the selected year
    waste_data['Date'] = pd.to_datetime(waste_data['Date'])
    waste_data = waste_data[waste_data['Date'].dt.year == selected_year]

    # Dictionary to store the misclassification weights for each stream
    misclassification_weights = {'Compost': 0, 'Landfill': 0, 'Recycling': 0}

    # Iterate over the rows of the filtered waste data
    for _, row in waste_data.iterrows():
        stream = row['Stream']
        weight = row['Weight']

        # Check misclassification and add weight accordingly
        if ' in ' in stream:
            parts = stream.split(' in ')
            if len(parts) == 2:
                category1 = parts[0]
                category2 = parts[1]

                # Add weight to the corresponding categories based on misclassification
                if category1 == 'Landfill':
                    if category2 == 'Compost' or category2 == 'Recycling':
                        misclassification_weights[category1] += weight
                elif category1 == 'Compost':
                    if category2 == 'Landfill' or category2 == 'Recycling':
                        misclassification_weights[category1] += weight
                elif category1 == 'Recycling':
                    if category2 == 'Landfill' or category2 == 'Compost':
                        misclassification_weights[category1] += weight

    # Find the stream with the highest misclassification weight
    most_incorrect_stream = max(misclassification_weights, key=misclassification_weights.get)
    most_incorrect_weight = misclassification_weights[most_incorrect_stream]

    # Create a dictionary of all misclassified streams and their weights
    misclassified_streams = {k: v for k, v in misclassification_weights.items() if v > 0}

    # Add the most misclassified stream and its weight to the dictionary
    misclassified_streams['Most Misclassified Stream'] = {
        'Stream': most_incorrect_stream,
        'Weight': most_incorrect_weight
    }

    return misclassified_streams


def calculate_misclassified_weight(year):

    data = pd.read_csv('assign2_wastedata.csv')

#     # Convert 'Date' column to datetime type
    data['Date'] = pd.to_datetime(data['Date'])

#     # Filter the data for the selected year
    data_selected_year = data[data['Date'].dt.year == year]

    # Initialize the total misclassified weight and total weight for each category to 0
    misclassified_weight = {
        'Recycling': 0,
        'Compost': 0,
        'Landfill': 0,
        'Total Misclassified Waste': 0
    }

    # Iterate over the rows of the data for the selected year
    for _, row in data_selected_year.iterrows():
        stream = row['Stream']

        # Check if the stream contains both Recycling and Landfill or Compost
        if 'Recycling' in stream and ('Landfill' in stream or 'Compost' in stream):
            if 'Landfill' in stream:
                misclassified_weight['Landfill'] += round(row['Weight'], 2)
                misclassified_weight['Total Misclassified Waste'] += round(row['Weight'], 2)
        elif 'Landfill' in stream and ('Recycling' in stream or 'Compost' in stream):
            misclassified_weight['Landfill'] += round(row['Weight'], 2)
            misclassified_weight['Total Misclassified Waste'] += round(row['Weight'], 2)
        elif 'Compost' in stream and ('Recycling' in stream or 'Landfill' in stream):
            if 'Landfill' in stream:
                misclassified_weight['Compost'] += round(row['Weight'], 2)
                misclassified_weight['Total Misclassified Waste'] += round(row['Weight'], 2)
        else:
            continue

    # Round the misclassified weight values to two decimal places and add 'lbs' unit
    misclassified_weight = {category: weight for category, weight in misclassified_weight.items()}

   
    return misclassified_weight

def calculate_misclassified_weight_chart(year, building):
    data = pd.read_csv('assign2_wastedata.csv')

    # Convert 'Date' column to datetime type
    data['Date'] = pd.to_datetime(data['Date'])

    # Filter the data for the selected year and building
    data_selected_year_building = data[(data['Date'].dt.year == year) & (data['Building'] == building)]

    # Initialize the total misclassified weight for each category to 0
    misclassified_weight = {
        'Recycling': 0,
        'Compost': 0,
        'Landfill': 0
    }

    # Iterate over the rows of the data for the selected year and building
    for _, row in data_selected_year_building.iterrows():
        stream = row['Stream']

        # Check if the stream contains both Recycling and Landfill or Compost
        if 'Recycling' in stream and ('Landfill' in stream or 'Compost' in stream):
            if 'Landfill' in stream:
                misclassified_weight['Landfill'] += round(row['Weight'], 2)
        elif 'Landfill' in stream and ('Recycling' in stream or 'Compost' in stream):
            misclassified_weight['Landfill'] += round(row['Weight'], 2)
        elif 'Compost' in stream and ('Recycling' in stream or 'Landfill' in stream):
            if 'Landfill' in stream:
                misclassified_weight['Compost'] += round(row['Weight'], 2)

    # Round the misclassified weight values to two decimal places and add 'lbs' unit
    misclassified_weight = {category: weight for category, weight in misclassified_weight.items()}

    return misclassified_weight







