from dash import Dash
import pandas as pd

# I fixed your imports for dash.dcc and dash.html,  the reason you were getting a warning message was because the way you imported the library worked 
# but was an outdated method of doing it

from dash import dcc,html
import plotly.express as px
from dash.dependencies import Input, Output
import pymssql
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

import warnings # The method used in class gives a warning when using pd.read_sql, this will ignore the warning message
warnings.simplefilter(action='ignore', category=UserWarning)

database = "Pushing-P-DB"
table = "dbo.Master_Table" # It does not like hyphens for some reason
user = "pushing_p"
password  = "t3stP@ssword"
server = "gen10-data-fundamentals-22-02-sql-server.database.windows.net"


# Make function to retrieve data from database
def Get_Data():
    try:
        conn = pymssql.connect(server,user,password,database)

        query = f"SELECT * FROM {table}"

        df = pd.read_sql(query, conn)

        # converting to pandas dataframe
        df = pd.DataFrame(df)

        


        # # This is where I format the TimeStamp to "ms" and then I have to for some reason use ".dt.strftime('%Y-%m-%d %H:%M:%S')" because the format in the table chances when I print it out
        # df['TimeStamp'] = pd.to_datetime(df['TimeStamp'], unit='ms').dt.strftime('%Y-%m-%d %H:%M:%S')

        # # This is where I order based off of timestamp for my fifth dataframe
        # df = df.sort_values(by='TimeStamp',ascending=False)

        return df

    except Exception as e:
        raise e


# Here I set the colors I will be using for the visualizations
colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

# You can put all of the code for making each of your plots inside of one function
# Then just call the function get each of your figures
# This is useful for simplifying the callback, now we only need one callback function instead of 5
def Make_Plots(df):

    # This is my map of Pokemon Locations
    fig = px.scatter_mapbox(df, lat="Latitude", lon="Longitude",
                    color_continuous_scale=px.colors.cyclical.IceFire, size_max=50, zoom=9,
                    color_discrete_sequence=["red"], hover_name="Name", mapbox_style="carto-positron",
                    title = 'Map of Pokemon Locations')

    # this is where I center the title for the visualization
    fig.update_layout(
        title=dict(x=0.5), #set title in the center
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
    )

    fig_2 = px.density_mapbox(df,lat='Latitude', lon='Longitude',
                        zoom = 9, title= "Heatmap of Pokemon Locations", hover_name="Name",
                        # this is the style I use for my graph
                        mapbox_style="stamen-terrain")
                        # fig_2.show() # outputting graph

    # this is where I center the title for the visualization
    fig_2.update_layout(
        title=dict(x=0.5), #set title in the center
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
    )

    # The Most Popular Pokemon
    df_3= df.groupby(['Name'])['Name'].count().reset_index(name='Count')


    fig_3 = px.bar(df_3, x='Name', y='Count',color_discrete_sequence=["green"], title='The Most Popular Pokemon', labels=dict(Name='Name of the Pokemon', Count='Count of Each Pokemon'))
    fig_3.update_layout(xaxis={'categoryorder':'total descending'})
    # fig_3.update_layout(width= 1150, height=700)
    # fig_3.show()

    # this is where I center the title for the visualization
    fig_3.update_layout(
        title=dict(x=0.5), #set title in the center
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
    )

    # Most Popular Pokemon Types
    df_4= df.groupby(['Type'])['Type'].count().reset_index(name='Count of Type')

    fig_4 = px.bar(df_4, x='Type', y='Count of Type',color_discrete_sequence=["blue"], title='Most Popular Pokemon Types', labels=dict(Name='Type of Pokemon', Count='Count of Type of Pokemon'))
    fig_4.update_layout(xaxis={'categoryorder':'total descending'})
    # fig_4.update_layout(width= 700, height=500)
    # fig_4.show()

    # this is where I center the title for the visualization
    fig_4.update_layout(
        title=dict(x=0.5), #set title in the center
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
    )

    # This is where I order based off of timestamp for my fifth dataframe
    df_5 = df.head(100)

    fig_5 = go.Figure(data=[go.Table(
        header=dict(values=list(df_5.columns),
                    fill_color='#3F7674',
                    align='left'),
        cells=dict(values=[df_5.ID, df_5.Name, df_5.Type, df_5.Weight, df_5.Height, df_5.TimeStamp, df_5.Restaurant, df_5.Longitude, df_5.Latitude],
                fill_color='black',
                align='left'))
    ])
    # fig_5.show()

    fig_5.update_layout(
        title = "The 100 Most Recently Added Pokemon", # this is where I add the title for my table
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
    )

    return fig, fig_2, fig_3, fig_4, fig_5

df = Get_Data()
fig, fig_2, fig_3, fig_4, fig_5 = Make_Plots(df)


app = Dash(__name__)

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                # here I add the emoji
                html.P(children="🚓", style={'fontSize': "30px",'textAlign': 'center'}, className="header-emoji"), 
                #Header title
                html.H1(
                    children="Metrics of Uninsured in New Jersey",style={'textAlign': 'center'}, className="header-title" 
                ),
                #Description below the header
                html.H2(
                    children="Analyzing Pokemon Data",
                    className="header-description", style={'textAlign': 'center'},
                ),
            ],
            className="header",style={'backgroundColor':'#111111', 'color': '#7FDBFF'},
        ),
        
        
        html.Div(
            children=[
                html.Div(children = 'Name', style={'fontSize': "24px",'backgroundColor':'#111111', 'color': '#7FDBFF'},className = 'menu-title'),
                #the dropdown function
                dcc.Dropdown(
                    id = 'name-filter',
                    options = [
                        {'label': Name, 'value':Name}
                        for Name in df.Name.unique()
                    ],
                    value = df.Name,
                    clearable = True,
                    searchable = True,
                    className = 'dropdown', style={'fontSize': "18px",'textAlign': 'center', 'backgroundColor':'#111111', 'color': '#7FDBFF'},
                ),
            ],
            className = 'menu', style={'fontSize': "18px",'textAlign': 'center', 'backgroundColor':'#111111', 'color': '#423A38'},
        ),
        
        # my four graphs
        html.Div(
            children=[
                html.Div(
                children = dcc.Graph(
                    id = 'Map-of-location',
                    figure = fig,
                  #  config={"displayModeBar": False},
                ),
                style={'width': '50%', 'display': 'inline-block'},
            ),
                html.Div(
                children = dcc.Graph(
                    id = 'heatmap',
                    figure = fig_2,
                    #config={"displayModeBar": False},
                ),
                style={'width': '50%', 'display': 'inline-block'},
            ),
                html.Div(
                children = dcc.Graph(
                    id = 'barchart',
                    figure = fig_3,
                    #config={"displayModeBar": False},
                ),
                style={'width': '50%', 'display': 'inline-block'},
            ),
                html.Div(
                children = dcc.Graph(
                    id = 'barchart-2',
                    figure = fig_4,
                    #config={"displayModeBar": False},
                ),
                style={'width': '50%', 'display': 'inline-block'},
            ),
                html.Div(
                children = dcc.Graph(
                    id = 'table',
                    figure = fig_5,
                    # config={"displayModeBar": False},
                ),
                style={'width': '100%', 'height': '70%','display': 'inline-block', 'backgroundColor':'#111111', 'color': '#7FDBFF'}, # height part of style doesn't work
            ),
                dcc.Interval(
                id='interval-component',
                interval= 5000, # in milliseconds (there will be an update once every minute)
                n_intervals=0)
        ],
        className = 'double-graph',
        ),
    ]
)

# One callback will update all 5 figures
@app.callback(
    [Output("Map-of-location", "figure"),
    Output("heatmap", "figure"),
    Output("barchart", "figure"),
    Output("barchart-2", "figure"),
    Output("table", "figure")], # the output is the map
    [Input("name-filter", "value"), # the input is the dcc.Dropdown id ("name-filter") and "value"
    Input("interval-component", "n_intervals")], # this input is the dcc.Interval id ("interval-component") and "n_intervals" 
)

def update_charts(n, interval):

    df = Get_Data()

    # If a value is selected from the button
    if n != None:
        df = df[df["Name"] == n] #the graph/dataframe will be filtered by "Name"


    fig, fig_2, fig_3, fig_4, fig_5 = Make_Plots(df)

    return fig, fig_2, fig_3, fig_4, fig_5


if __name__ == '__main__':
    app.run_server(debug = True)