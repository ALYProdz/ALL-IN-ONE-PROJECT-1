import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
from numpy.polynomial.polynomial import Polynomial
pip install dash




# Load workout data
data = pd.read_csv("./Downloads/workout_data.csv")

# Convert Date column to datetime format
data['Date'] = pd.to_datetime(data['Date'])

# Add a calculated column for Workout Volume (Weight * Reps)
data['Volume'] = data['Weight'] * data['Reps']

# Add a calculated column for 1 Rep Max (Epley Formula)
data['1RM'] = data['Weight'] * (1 + data['Reps'] / 30)

# Initialize Dash app
app = dash.Dash(__name__)

# Layout
app.layout = html.Div([
    html.H1("Workout Insights - Interactive Dashboard", style={'text-align': 'center', 'font-size': '30px', 'font-family': 'Arial'}),
    # Dropdown for Muscle Group
    html.Div([
        html.Label("Category:"),
        dcc.Dropdown(
            id='muscle-dropdown',
            options=[{'label': muscle, 'value': muscle} for muscle in data['Category'].unique()],
            value='Chest',
            multi=False,
            clearable=False
        ),
    ], style={'width': '50%', 'margin': '0 auto'}),
    # Dropdown for Exercise
    html.Div([
        html.Label("Exercise:"),
        dcc.Dropdown(
            id='exercise-dropdown',
            multi=False,
            clearable=False
        ),
    ], style={'width': '50%', 'margin': '20px auto'}),
    # Dropdown for Data Attribute
    html.Div([
        html.Label("Data to Visualize:"),
        dcc.Dropdown(
            id='attribute-dropdown',
            options=[
                {'label': 'Performance Analysis - 1 Rep Max (1RM)', 'value': '1RM'},
                {'label': 'Volume Analysis', 'value': 'Volume'},
                {'label': 'Frequency Analysis - Sets & Reps', 'value': 'Reps'}
            ],
            value='1RM',
            multi=False,
            clearable=False
        ),
    ], style={'width': '50%', 'margin': '20px auto'}),
    # Date range filter
    html.Div([
        html.Label("Duration Mode", style={'font-size': '18px', 'font-family': 'Arial'}),
        dcc.RadioItems(
            id='duration-mode',
            options=[
                {'label': 'All Duration', 'value': 'all'},
                {'label': 'Specific Duration', 'value': 'specific'}
            ],
            value='all',
            inline=True,
            style={'margin-bottom': '10px'}
        ),
        dcc.DatePickerRange(
            id='date-picker',
            start_date=data['Date'].min(),
            end_date=data['Date'].max(),
            display_format='DD MMM YYYY'
        )
    ], style={'width': '50%', 'margin': '20px auto', 'text-align': 'center'}),
    # Insights Section
    html.Div(id='insights', style={'text-align': 'center', 'margin': '20px'}),
    # Graph
    dcc.Graph(id='workout-graph')
])

# Callback to update the date picker based on the duration mode
@app.callback(
    [Output('date-picker', 'start_date'),
     Output('date-picker', 'end_date'),
     Output('date-picker', 'disabled')],
    Input('duration-mode', 'value')
)
def toggle_date_picker(duration_mode):
    if duration_mode == 'all':
        return data['Date'].min(), data['Date'].max(), True  # Reset to all dates and disable
    else:
        return data['Date'].min(), data['Date'].max(), False  # Enable date picker


# Callback to update Exercise dropdown based on selected Muscle Group
@app.callback(
    Output('exercise-dropdown', 'options'),
    Input('muscle-dropdown', 'value')
)
def update_exercise_dropdown(selected_muscle):
    exercises = data[data['Category'] == selected_muscle]['Exercise'].unique()
    return [{'label': exercise, 'value': exercise} for exercise in exercises]

# Callback for insights and visualization
@app.callback(
    [Output('insights', 'children'),
     Output('workout-graph', 'figure')],
    [Input('muscle-dropdown', 'value'),
     Input('exercise-dropdown', 'value'),
     Input('attribute-dropdown', 'value'),
     Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date')]
)
def update_dashboard(selected_muscle, selected_exercise, selected_attribute, start_date, end_date):
    # Filter data by muscle group, exercise, and date range
    filtered_data = data[(data['Category'] == selected_muscle) &
                         (data['Exercise'] == selected_exercise) &
                         (data['Date'] >= start_date) &
                         (data['Date'] <= end_date)]

    # Check if filtered data is empty
    if filtered_data.empty:
        return [
            html.H3("No data available for the selected filters."),
            px.scatter(title="No Data Available")
        ]

    # Group data by Date for maximum, minimum, and average calculations
    grouped_data = filtered_data.groupby('Date').agg(
        TotalVolume=('Volume', 'sum'),
        TotalReps=('Reps', 'sum'),
        Max1RM=('1RM', 'max'),
        Min1RM=('1RM', 'min')
    ).reset_index()

    # Retrieve actual weight and reps for max 1RM
    tooltip_data = filtered_data.loc[filtered_data.groupby('Date')['1RM'].idxmax()][['Date', 'Weight', 'Reps', '1RM']]

    # Add custom tooltip information
    tooltip_data['Tooltip'] = tooltip_data.apply(
        lambda row: f"1RM: {row['1RM']:.1f} kgs (Breakdown: {row['Weight']} kgs x {row['Reps']} reps)", axis=1
    )

    # Merge tooltip information back into grouped_data
    grouped_data = grouped_data.merge(tooltip_data[['Date', 'Tooltip']], on='Date', how='left')

    # Dynamically handle selected attribute
    if selected_attribute == '1RM':
        grouped_data = grouped_data[['Date', 'Max1RM', 'Tooltip']].rename(columns={'Max1RM': 'Value'})
        y_label = '1 Rep Max (kg)'
        title = f"1 Rep Max Progression for {selected_exercise}"

        # Add trendline for 1RM
        grouped_data['Date_Ordinal'] = grouped_data['Date'].apply(lambda x: x.toordinal())
        coefs = Polynomial.fit(grouped_data['Date_Ordinal'], grouped_data['Value'], 1).convert().coef
        slope = coefs[1]
        trendline_y = coefs[0] + coefs[1] * grouped_data['Date_Ordinal']
        grouped_data['Trendline'] = trendline_y

        # Determine trendline color
        trend_color = 'green' if slope > 0.05 else 'yellow' if slope > -0.05 else 'red'

        # Generate line graph with trendline
        fig = px.line(grouped_data, x='Date', y='Value',
                      title=title,
                      labels={'Value': y_label, 'Date': 'Workout Date'})
        fig.add_scatter(x=grouped_data['Date'], y=grouped_data['Trendline'],
                        mode='lines', line=dict(dash='dot', color=trend_color),
                        name='Trend Line')

        # Adjust hover detail for 1RM
        fig.update_traces(
            hovertemplate="<b>Date:</b> %{x}<br>%{customdata}<extra></extra>",
            customdata=grouped_data['Tooltip']
        )

        highest = grouped_data['Value'].max()
        lowest = grouped_data['Value'].min()
        avg = grouped_data['Value'].mean()

        # Generate insights
        insight_text = [
            html.H2(f"{selected_attribute} Insights for {selected_exercise}"),
            html.P(f"Highest {selected_attribute} in the Specified Duration: {highest:.1f} kgs"),
            html.P(f"Lowest {selected_attribute} in the Specified Duration: {lowest:.1f} kgs"),
            html.P(f"Average {selected_attribute} in the Specified Duration: {avg:.1f} kgs")
        ]

    elif selected_attribute == 'Volume':
        y_label = 'Total Volume (kgs) per Workout'
        title = f"Total Volume Progression for {selected_exercise}"
        fig = px.area(grouped_data, x='Date', y='TotalVolume',
                      title=title,
                      labels={'TotalVolume': y_label, 'Date': 'Workout Date'})
        highest = grouped_data['TotalVolume'].max()
        lowest = grouped_data['TotalVolume'].min()
        avg = grouped_data['TotalVolume'].mean()

        # Generate insights
        insight_text = [
            html.H2(f"Total {selected_attribute} Insights for {selected_exercise}"),
            html.P(f"Highest Total {selected_attribute} per Workout in the Specified Duration: {highest:.1f} kgs"),
            html.P(f"Lowest Total {selected_attribute} per Workout in the Specified Duration: {lowest:.1f} kgs"),
            html.P(f"Average Total {selected_attribute} per Workout in the Specified Duration: {avg:.1f} kgs")
        ]

    elif selected_attribute == 'Reps':
        y_label = 'Total Reps per Workout'
        title = f"Total Reps and Sets Breakdown for {selected_exercise}"

        # Calculate total reps for each workout date
        grouped_reps = filtered_data.groupby('Date').agg(TotalReps=('Reps', 'sum')).reset_index()

        # Add a column to indicate set number for each row
        filtered_data['SetNumber'] = filtered_data.groupby('Date').cumcount() + 1
        filtered_data['TotalSets'] = filtered_data.groupby('Date')['SetNumber'].transform('max')

        # Calculate totals
        total_workouts = filtered_data['Date'].nunique()
        total_sets = filtered_data['SetNumber'].max()
        total_sets_in_duration = filtered_data['SetNumber'].count()
        total_reps = filtered_data['Reps'].sum()

        # Add custom hover information
        filtered_data['Tooltip'] = filtered_data.apply(
            lambda row: f"Workout Date: {row['Date'].strftime('%b %d, %Y')}<br>"
                        f"Total Reps: {grouped_reps[grouped_reps['Date'] == row['Date']]['TotalReps'].values[0]}<br>"
                        f"Set {row['SetNumber']} of {row['TotalSets']}<br>"
                        f"Reps in Current Set: {row['Reps']}",
            axis=1
        )

        # Generate bar graph with detailed hover information
        fig = px.bar(
            filtered_data,
            x='Date',
            y='Reps',
            title=title,
            labels={'Reps': y_label, 'Date': 'Workout Date'}
        )

        # Update hover template
        fig.update_traces(
            hovertemplate="%{customdata}<extra></extra>",
            customdata=filtered_data['Tooltip']
        )

        highest_in_set = filtered_data['Reps'].max()
        lowest_in_set = filtered_data['Reps'].min()
        avg_in_set = filtered_data['Reps'].mean()

        highest_in_workout = grouped_reps['TotalReps'].max()
        lowest_in_workout = grouped_reps['TotalReps'].min()
        avg_in_workout = grouped_reps['TotalReps'].mean()

        # Updated insights for reps
        insight_text = [
            html.H2(f"Sets and Reps Insights for {selected_exercise}"),
            html.H3(f"Total Workouts in the Specified Duration: {total_workouts}"),
            html.H3(f"Total Sets in the Specified Duration: {total_sets_in_duration}"),
            html.H3(f"Total Reps in the Specified Duration: {total_reps}"),
            html.P([
                "Highest Reps in a Set: ", f"{highest_in_set:.0f}",
                html.Span(" ", style={'display': 'inline-block', 'width': '1.5cm'}),
                "Highest Reps in a Workout: ", f"{highest_in_workout:.0f}"
            ]),
            html.P([
                "Average Reps in a Set: ", f"{avg_in_set:.0f}",
                html.Span(" ", style={'display': 'inline-block', 'width': '1.5cm'}),
                "Average Reps in a Workout: ", f"{avg_in_workout:.0f}"
            ]),
            html.P([
                "Lowest Reps in a Set: ", f"{lowest_in_set:.0f}",
                html.Span(" ", style={'display': 'inline-block', 'width': '1.5cm'}),
                "Lowest Reps in a Workout: ", f"{lowest_in_workout:.0f}"
            ])
        ]

    return insight_text, fig

# Run app
if __name__ == '__main__':
    app.run()
    #app.run_server(host="0.0.0.0", port=8050)