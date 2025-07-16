# Import required libraries
import pandas as pd
from dash import Dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px


# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = Dash(__name__)

launch_sites = spacex_df['Launch Site'].unique()
dropdown_options = (
    [{'label':'All Sites','value':'ALL'}] +
    [{'label': site,'value':site} for site in launch_sites]
)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                dcc.Dropdown(
                                    id='site-dropdown',
                                    options=dropdown_options,
                                    value='ALL',
                                    placeholder="Select a Launch Site",
                                    searchable=True
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=min_payload,
                                    max=max_payload,
                                    step=1000,
                                    marks={
                                        0: '0',
                                        2500: '2500',
                                        5000: '5000',
                                        7500: '7500',
                                        10000: '10000'
                                    },
                                    value=[min_payload, max_payload]),
                                html.Br(),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# TASK 2: Add callback for 'site-dropdown' → update 'success-pie-chart'
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        # for ALL: count successes at each site
        df = spacex_df[spacex_df['class'] == 1]  # only successful launches
        fig = px.pie(
            df, 
            names='Launch Site', 
            title='Total Successful Launches by Site'
        )
    else:
        # for a specific site: show success vs. failure counts
        df = spacex_df[spacex_df['Launch Site'] == selected_site]
        counts = df['class'].value_counts().rename_axis('outcome').reset_index(name='count')
        # map 1→Success, 0→Failure
        counts['outcome'] = counts['outcome'].map({1:'Success', 0:'Failure'})
        fig = px.pie(
            counts, 
            names='outcome', 
            values='count',
            title=f'Total Success vs. Failure for site {selected_site}'
        )
    return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
# TASK 4: callback for payload‐scatter‐chart
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [
      Input(component_id='site-dropdown', component_property='value'),
      Input(component_id='payload-slider', component_property='value')
    ]
)
def update_scatter_chart(selected_site, payload_range):
    low, high = payload_range
    
    # start with full DF
    df = spacex_df.copy()
    
    # filter by site if not ALL
    if selected_site != 'ALL':
        df = df[df['Launch Site'] == selected_site]
    
    # filter by payload mass
    df = df[(df['Payload Mass (kg)'] >= low) &
            (df['Payload Mass (kg)'] <= high)]
    
    # build scatter
    title = (
        "Correlation between Payload and Success "
        + ("for all Sites" if selected_site == 'ALL' else f"for site {selected_site}")
    )
    fig = px.scatter(
        df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title=title
    )
    return fig


# Run the app
if __name__ == '__main__':
    app.run()       
