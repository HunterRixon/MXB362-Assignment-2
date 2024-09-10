import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import ast
from functools import reduce

# Read the CSV file and put into dataframe
steam_data = pd.read_csv("data\games.csv", encoding="latin-1", low_memory=False)

# I don't want to see duplicate game titles ruining my beautiful graphs
steam_data = steam_data.drop_duplicates(subset=['Name'])

steam_data = steam_data.dropna(subset=['Supported languages'])

# Define a function to map the age values to maturity ratings 
def map_age_to_rating(age):
    if 0 <= age < 10:
        return 'G'
    elif 10 <= age < 13:
        return 'PG'
    elif 13 <= age < 15:
        return 'M'
    elif 15 <= age < 17:
        return 'MA'
    elif 17 <= age < 21:
        return 'R'
    else:
        return 'X'
    

# Apply the function to create a new column 'Maturity Rating'
steam_data['Maturity Rating'] = steam_data['Required age'].apply(map_age_to_rating)

# There are so many values which are multiple cents thanks to international currency differences.
# It can be fixed by just rounding all of them up.
steam_data['Price'] = steam_data['Price'].round()

# Parse the 'TRUE' and 'FALSE' values to Python boolean format
#steam_data['Windows'] = steam_data['Windows'].map({'TRUE': True, 'FALSE': False})
#steam_data['Mac'] = steam_data['Mac'].map({'TRUE': True, 'FALSE': False})
#steam_data['Linux'] = steam_data['Linux'].map({'TRUE': True, 'FALSE': False})

# Calculate the merged reviews column (rounded to the nearest 10%)
steam_data['Merged Reviews'] = ((steam_data['Positive'] / (steam_data['Positive'] + steam_data['Negative'])) * 10).round() * 10

# Because of how these are stored, it is much easier to split them into lists in order to use them.
# Why? It has to do with the fact that their base format is like 'Single-player,Steam achievements,etc.'
steam_data['developers separated'] = steam_data['Developers'].str.split(',')
steam_data['publishers separated'] = steam_data['Publishers'].str.split(',')
steam_data['categories separated'] = steam_data['Categories'].str.split(',')
steam_data['genres separated'] = steam_data['Genres'].str.split(',')
steam_data['tags separated'] = steam_data['Tags'].str.split(',')

# Create a Dash web application
app = dash.Dash(__name__)

all_languages = []

for supported_languages in steam_data['Supported languages']:
    try:
        languages = ast.literal_eval(supported_languages)
        all_languages.extend(languages)
    except (ValueError, SyntaxError):
        # Handle invalid data gracefully (e.g., non-list values)
        pass

language_series = pd.Series(all_languages)

language_counts = language_series.value_counts().reset_index().head(50)
language_counts.columns = ['Language', 'Count']

# Create a bar chart using Plotly Express for language counts
language_chart = px.bar(
    language_counts,
    x='Language',
    y='Count',
    title='Language Counts'
)

# Update chart layout for interactivity
language_chart.update_layout(
    clickmode='event+select',
    showlegend=False
)

category_dropdown_style = {
    #'backgroundColor': 'white',  # Background color
    'border': '1px solid lightgray',     # Border style
    'color': 'black',               # Text color
}

success_dropdown_style = {
    #'backgroundColor': 'white',  # Background color
    'border': '1px solid blue',     # Border style
    'color': 'black',               # Text color
}

# Create a dropdown for selecting maturity ratings
maturity_rating_dropdown = html.Div([
    html.Label("Select Maturity Rating"),
    dcc.Dropdown(
        id='maturity-rating-dropdown',
        options=[
            {'label': 'G (General)', 'value': 'G'},
            {'label': 'PG (Parental Guidance)', 'value': 'PG'},
            {'label': 'M (Mature)', 'value': 'M'},
            {'label': 'MA (Mature 15+)', 'value': 'MA'},
            {'label': 'R (Adults Only)', 'value': 'R'},
            {'label': 'X (Adults Only - Explicit)', 'value': 'X'},
        ],
        multi=False,  # Allow a single selection
        value=None,  # Default to None
        style=category_dropdown_style
    )
])

price_ranges = steam_data['Price'].unique()
price_ranges = sorted(price_ranges, reverse=False)  # Ensure it goes in descending order
price_ranges = [int(price) if not pd.isna(price) else None for price in price_ranges]  # Round the price values to integers, replace NaN with None
price_range_dropdown = html.Div([
    html.Label("Select Price Range"),
    dcc.Dropdown(
        id='price-range-dropdown',
        options=[{'label': price, 'value': price} for price in price_ranges if price is not None],  # Filter out None values
        value=None, # price_ranges[0] if price_ranges and price_ranges[0] is not None else None  # Set default value to the first non-None value
        style=category_dropdown_style
    )
])

# Handle 'DLC count' values
# Note: This code block doesn't filter the values to integer, meaning it isn't properly ordered and doesn't function to full capacity.
#dlc_ranges = steam_data['DLC count'].unique()
#dlc_ranges = sorted(dlc_ranges, reverse=False)  # Ensure it goes in descending order
#dlc_range_dropdown = html.Div([
#    html.Label("Select No. of DLC's"),
#    dcc.Dropdown(
#        id='dlc-range-dropdown',
#        options=[{'label': dlc, 'value': dlc} for dlc in dlc_ranges if dlc is not None],  # Filter out None values
#        value=None # dlc_ranges[0] if dlc_ranges and dlc_ranges[0] is not None else None  # Set default value to the first non-None value
#    )
#])

# Create dropdowns for each platform
#windows_dropdown = html.Div([
#    html.Label("Windows Support?"),
#    dcc.Dropdown(
#        id='windows-dropdown',
#        options=[
#            {'label': 'True', 'value': True},
#            {'label': 'False', 'value': False},
#        ],
#        multi=False,
#        value=None,  # Default to None
#        style=category_dropdown_style
#    )
#])

#mac_dropdown = html.Div([
#    html.Label("Mac Support?"),
#    dcc.Dropdown(
#        id='mac-dropdown',
#        options=[
#            {'label': 'True', 'value': True},
#            {'label': 'Flase', 'value': False},
#        ],
#        multi=False,
#        value=None,  # Default to None
#        style=category_dropdown_style
#    )
#])

#linux_dropdown = html.Div([
#    html.Label("Linux Support?"),
#    dcc.Dropdown(
#        id='linux-dropdown',
#        options=[
#            {'label': 'True', 'value': True},
#            {'label': 'False', 'value': False},
#        ],
#        multi=False,
#        value=None,  # Default to None
#        style=category_dropdown_style
#    )
#])

# Handle 'Positive' values
#positive_ranges = steam_data['Positive'].unique()
#positive_ranges = [int(pos) if pd.notna(pos) and isinstance(pos, (int, float)) else None for pos in positive_ranges]
#positive_ranges = sorted(positive_ranges, reverse=False)  # Ensure it goes in descending order
#positive_range_dropdown = html.Div([
#    html.Label("No. of Positive Steam Ratings"),
#    dcc.Dropdown(
#        id='positive-range-dropdown',
#        options=[{'label': pos, 'value': pos} for pos in positive_ranges if pos is not None],  # Filter out None values
#        value=None  # Set default value to the first non-None value
#    )
#])

# Handle 'Negative' values
#negative_ranges = steam_data['Negative'].unique()
#negative_ranges = [int(neg) if pd.notna(neg) and isinstance(neg, (int, float)) else None for neg in negative_ranges]
#negative_ranges = sorted(negative_ranges, reverse=False)  # Ensure it goes in descending order
#negative_range_dropdown = html.Div([
#    html.Label("No. of Negative Steam Ratings"),
#    dcc.Dropdown(
#        id='negative-range-dropdown',
#        options=[{'label': neg, 'value': neg} for neg in negative_ranges if neg is not None],  # Filter out None values
#        value=None  # Set default value to the first non-None value
#    )
#])

# Create a dropdown for selecting the percentage of positive reviews
percentage_dropdown = html.Div([
    html.Label("Select Percentage of Positive Reviews"),
    dcc.Dropdown(
        id='percentage-dropdown',
        options=[
            {'label': f'{i}%', 'value': i}
            for i in range(10, 101, 10)  # Generate options for 10%, 20%, ..., 100%
        ],
        multi=False,
        value=None,  # Default to None
        style=category_dropdown_style
    )
])

# Handle 'Achievement' values
# Note: This code block doesn't filter the values to integer, meaning it isn't properly ordered and doesn't function to full capacity.
#achievement_ranges = steam_data['Achievements'].unique()
#achievement_ranges = sorted(achievement_ranges, reverse=False)  # Ensure it goes in descending order
#achievement_range_dropdown = html.Div([
#    html.Label("No. of Achievements"),
#    dcc.Dropdown(
#        id='achievement-range-dropdown',
#        options=[{'label': ach, 'value': ach} for ach in achievement_ranges if ach is not None],  # Filter out None values
#        value=None # achievement_ranges[0] if achievement_ranges and achievement_ranges[0] is not None else None  # Set default value to the first non-None value
#    )
#)

# Handle 'Recommendations' values
# Note: This code block doesn't filter the values to integer, meaning it isn't properly ordered and doesn't function to full capacity.
#recommendation_ranges = steam_data['Recommendations'].unique()
#recommendation_ranges = sorted(recommendation_ranges, reverse=False)  # Ensure it goes in descending order
#recommendation_range_dropdown = html.Div([
#    html.Label("No. of Recommendations"),
#    dcc.Dropdown(
#        id='recommendation-range-dropdown',
#        options=[{'label': rec, 'value': rec} for rec in recommendation_ranges if rec is not None],  # Filter out None values
#        value=None # recommendation_ranges[0] if recommendation_ranges and recommendation_ranges[0] is not None else None  # Set default value to the first non-None value
#    )
#])

# Create a multi-select dropdown for Developers
developers_dropdown = html.Div([
    html.Label("Select Developer/s"),
    dcc.Dropdown(
        id='developers-dropdown',
        options=[
            {'label': developer, 'value': developer}
            for developer_list in steam_data['developers separated'].dropna()
            for developer in developer_list
        ],
        multi=True,  # Allow multiple selections
        value=[],  # Set initial value to an empty list
        style=category_dropdown_style
    )
])

# Create a multi-select dropdown for Publishers
publishers_dropdown = html.Div([
    html.Label("Select Publishers"),
    dcc.Dropdown(
        id='publishers-dropdown',
        options=[
            {'label': publisher, 'value': publisher}
            for publisher_list in steam_data['publishers separated'].dropna()
            for publisher in publisher_list
        ],
        multi=True,  # Allow multiple selections
        value=[],  # Set initial value to an empty list
        style=category_dropdown_style
    )
])

# Create a multi-select dropdown for categories
categories_dropdown = html.Div([
    html.Label("Select Steam Categories"),
    dcc.Dropdown(
        id='categories-dropdown',
        options=[
            {'label': category, 'value': category}
            for category_list in steam_data['categories separated'].dropna()
            for category in category_list
        ],
        multi=True,  # Allow multiple selections
        value=[],  # Set initial value to an empty list
        style=category_dropdown_style
    )
])

# Create a multi-select dropdown for Genres
genres_dropdown = html.Div([
    html.Label("Select Steam Genres"),
    dcc.Dropdown(
        id='genres-dropdown',
        options=[
            {'label': genre, 'value': genre}
            for genre_list in steam_data['genres separated'].dropna()
            for genre in genre_list
        ],
        multi=True,  # Allow multiple selections
        value=[],  # Set initial value to an empty list
        style=category_dropdown_style
    )
])

# Create a multi-select dropdown for Tags
tags_dropdown = html.Div([
    html.Label("Select Steam Tags"),
    dcc.Dropdown(
        id='tags-dropdown',
        options=[
            {'label': tag, 'value': tag}
            for tag_list in steam_data['tags separated'].dropna()
            for tag in tag_list
        ],
        multi=True,  # Allow multiple selections
        value=[],  # Set initial value to an empty list
        style=category_dropdown_style
    )
])

# Add a Dropdown component for metric selection
success_metric_dropdown = html.Div([
    html.Label("Select Success Metric"),
    dcc.Dropdown(
        id='success-metric-dropdown',
        options=[
            {'label':'Peak CCU', 'value': 'Peak CCU'},
            {'label':'Metacritic score', 'value':'Metacritic score'},
            {'label':'User score', 'value':'User score'},
            {'label':'Recommendations', 'value':'Recommendations'},
            {'label':'Average playtime forever', 'value':'Average playtime forever'},
            {'label':'Median playtime forever', 'value':'Median playtime forever'},
            ],
            value='Peak CCU', # Set an initial default value
            style=success_dropdown_style
    )
])

alert_label = html.Div([
    html.H3(id='alert_label', style={'color': 'blue'})
])

# Arrange dropdowns in two columns (excluding Success Metric)
dropdowns_column1 = html.Div([
    maturity_rating_dropdown,
    price_range_dropdown,
    percentage_dropdown,
    #dlc_range_dropdown,
    #positive_range_dropdown,
    #negative_range_dropdown,
    developers_dropdown,
    #achievement_range_dropdown,
], style={'width': '49%', 'display': 'inline-block'})

dropdowns_column2 = html.Div([
    categories_dropdown,
    genres_dropdown,
    tags_dropdown,
    publishers_dropdown,
    #windows_dropdown,
    #mac_dropdown,
    #linux_dropdown,
], style={'width': '49%', 'display': 'inline-block'})

dropdowns_column3 = html.Div([
    success_metric_dropdown,
], style={'width': '98%', 'display': 'inline-block'})

# Define the layout with the language count chart and an empty top games chart
app.layout = html.Div([
    dcc.Graph(id='language-count-chart', figure=language_chart),
    dropdowns_column1,
    dropdowns_column2,
    dropdowns_column3,
    alert_label,
    dcc.Graph(id='top-games-chart'),
])

@app.callback(
    [Output('top-games-chart', 'figure'),
     Output('alert_label', 'children')],
    [Input('language-count-chart', 'selectedData'),
     Input('maturity-rating-dropdown', 'value'),
     Input('price-range-dropdown', 'value'),
     #Input('dlc-range-dropdown', 'value'),
     #Input('windows-dropdown', 'value'),
     #Input('mac-dropdown', 'value'),
     #Input('linux-dropdown', 'value'),
     #Input('positive-range-dropdown', 'value'),
     #Input('negative-range-dropdown', 'value'), 
     Input('percentage-dropdown', 'value'),
     #Input('achievement-range-dropdown', 'value'),
     #Input('recommendation-range-dropdown', 'value'),
     Input('developers-dropdown', 'value'),
     Input('publishers-dropdown', 'value'),
     Input('categories-dropdown', 'value'),
     Input('tags-dropdown', 'value'),
     Input('genres-dropdown', 'value'),
     Input('success-metric-dropdown','value')]
)
def update_top_games_chart(selectedData, selected_maturity_rating, selected_price_range, selected_percentage, selected_developers, selected_publishers, selected_categories, selected_genres, selected_tags, selected_metric): # selected_dlc_count, selected_windows, selected_mac, selected_linux, selected_positive, selected_negative, selected_achievements, selected_recommendations
    #if selected_windows is None and selected_mac is None and selected_linux is None:
    #    return {}  # Return an empty figure if all platform options are None

    if selectedData:
        # Extract the selected language
        selected_language = selectedData['points'][0]['x']
        print("Selected language:", selected_language)

        # Filter the DataFrame for the selected language
        filtered_df = steam_data[steam_data['Supported languages'].str.contains(selected_language)]

        # Debugging: Print some information about the filtered DataFrame
        print("Filtered DataFrame info:")
        print(filtered_df.info())

        if selected_maturity_rating is not None:
            filtered_df = filtered_df[filtered_df['Maturity Rating'] == selected_maturity_rating]

        # Only apply the 'Price' filter if a price range is selected
        if selected_price_range is not None:
            filtered_df = filtered_df[filtered_df['Price'] == selected_price_range]

        # Only apply the 'DLC count' filter if a dlc range is selected
        #if selected_dlc_count is not None:
        #    filtered_df = filtered_df[filtered_df['DLC count'] == selected_dlc_count]

        # Filter the DataFrame based on the selected platforms
        #platform_conditions = []

        #if selected_windows is not None:
        #    platform_conditions.append(filtered_df['Windows'] == selected_windows)
        #if selected_mac is not None:
        #    platform_conditions.append(filtered_df['Mac'] == selected_mac)
        #if selected_linux is not None:
        #    platform_conditions.append(filtered_df['Linux'] == selected_linux)

        #if platform_conditions:
            # Use logical OR to combine platform conditions
        #    platform_filter = reduce(lambda x, y: x | y, platform_conditions)
        #    filtered_df = filtered_df[platform_filter]

        # Only apply the 'Positive' filter if a positive range is selected
        #if selected_positive is not None:
        #    filtered_df = filtered_df[filtered_df['Positive'] == selected_positive]

        # Only apply the 'Negative' filter if a negative range is selected
        #if selected_negative is not None:
        #    filtered_df = filtered_df[filtered_df['Negative'] == selected_negative]

        if selected_percentage is not None:
            # Filter the DataFrame based on the selected percentage of positive reviews
            min_positive_percentage = selected_percentage - 10  # Adjust the range based on the selected percentage
            max_positive_percentage = selected_percentage

            filtered_df = filtered_df[(filtered_df['Merged Reviews'] >= min_positive_percentage) & (filtered_df['Merged Reviews'] <= max_positive_percentage)]

        # Only apply the 'Achievements' filter if an achievement range is selected
        #if selected_achievements is not None:
        #    filtered_df = filtered_df[filtered_df['Achievements'] == selected_achievements]

        # Only apply the 'Recommendations' filter if a recommendation range is selected
        #if selected_recommendations is not None:
        #    filtered_df = filtered_df[filtered_df['Recommendations'] == selected_recommendations]

        # Filter the DataFrame based on the selected developers
        if selected_developers:
            developer_conditions = []  # List to store individual developer conditions

            for selected_developer in selected_developers:
                developer_conditions.append(
                    filtered_df['developers separated'].apply(
                        lambda devs: selected_developer in devs if isinstance(devs, list) else False
                    )
                )

            # Combine the individual developer conditions using the logical AND operator
            if developer_conditions:
                developer_filter = reduce(lambda x, y: x & y, developer_conditions)
                filtered_df = filtered_df[developer_filter]

        # Filter the DataFrame based on the selected publishers
        if selected_publishers:
            publisher_conditions = []  # List to store individual publisher conditions

            for selected_publisher in selected_publishers:
                publisher_conditions.append(
                    filtered_df['publishers separated'].apply(
                        lambda pubs: selected_publisher in pubs if isinstance(pubs, list) else False
                    )
                )

            # Combine the individual publisher conditions using the logical AND operator
            if publisher_conditions:
                publisher_filter = reduce(lambda x, y: x & y, publisher_conditions)
                filtered_df = filtered_df[publisher_filter]    

        # Filter the DataFrame based on the selected categories
        if selected_categories:
            category_conditions = []  # List to store individual category conditions

            for selected_category in selected_categories:
                category_conditions.append(
                    filtered_df['categories separated'].apply(
                        lambda cats: selected_category in cats if isinstance(cats, list) else False
                    )
                )

            # Combine the individual category conditions using the logical AND operator
            if category_conditions:
                category_filter = reduce(lambda x, y: x & y, category_conditions)
                filtered_df = filtered_df[category_filter]

        # Filter the DataFrame based on the selected Genres
        if selected_genres:
            genre_conditions = []  # List to store individual genre conditions

            for selected_genre in selected_genres:
                genre_conditions.append(
                    filtered_df['genres separated'].apply(
                        lambda gens: selected_genre in gens if isinstance(gens, list) else False
                    )
                )

            # Combine the individual genre conditions using the logical AND operator
            if genre_conditions:
                genre_filter = reduce(lambda x, y: x & y, genre_conditions)
                filtered_df = filtered_df[genre_filter]

        # Filter the DataFrame based on the selected Tags
        if selected_tags:
            # Use apply and lambda to handle lists in the 'tags separated' column
            filtered_df = filtered_df[filtered_df['tags separated'].apply(
                lambda tags: any(tag in selected_tags for tag in tags) if isinstance(tags, list) else False
            )]

        # Update the 'success' metric column based on the selected metric
        if selected_metric == 'Peak CCU':
            filtered_df['success_metric'] = pd.to_numeric(filtered_df['Peak CCU'], errors='coerce')
        elif selected_metric == 'Metacritic score':
            filtered_df['success_metric'] = pd.to_numeric(filtered_df['Metacritic score'], errors='coerce')
        elif selected_metric == 'User score':
            filtered_df['success_metric'] = pd.to_numeric(filtered_df['User score'], errors='coerce')
        elif selected_metric == 'Recommendations':
            filtered_df['success_metric'] = pd.to_numeric(filtered_df['Recommendations'], errors='coerce')
        elif selected_metric == 'Average playtime forever':
            filtered_df['success_metric'] = pd.to_numeric(filtered_df['Average playtime forever'], errors='coerce')
        else:
            filtered_df['success_metric'] = pd.to_numeric(filtered_df['Median playtime forever'], errors='coerce')

        # Sort the filtered DataFrame by 'Peak CCU' in descending order
        top_15_games = filtered_df.sort_values(by='success_metric', ascending=False).head(15)

        if top_15_games.empty:
            fig = {}
            alert_text = "There are no items in the dataset which match your selection."
            return fig, alert_text
        elif selected_metric == "":
            fig = {}
            alert_text = "No 'Success Crtieria' has been selected."
            return fig, alert_text
        else:
            # Create a bar plot for the top 15 games
            fig = px.bar(
                top_15_games,
                x='Name',
                y='success_metric',
                title=f'Top 15 Games in {selected_language}',
                category_orders={"Name": top_15_games.sort_values(by='success_metric', ascending=False)["Name"]}  # Ensure the x-axis order matches the DataFrame order
            )
            alert_text = ""
            return fig, alert_text

    # If nothing is selected, return an empty figure, and the alert for the user to select a language
    return {}, "Please select a language."

if __name__ == '__main__':
    app.run_server(debug=True)