# run this app with 'python app.py' and 
# visit http://127.0.0.1:8050/ in your web browswer

import warnings

warnings.simplefilter(action='ignore', category=UserWarning) # Ignore User Warning regarding Shapely
# In addition, ignore the warning message when using pd.read_sql
from dash import Dash
from shapely import wkb, speedups
from dash import dcc,html
from dash.dependencies import Input, Output
import pymssql
import plotly.graph_objects as go
import pandas as pd
import geopandas as gpd
import plotly.express as px
speedups.disable()
from tobler.area_weighted import area_interpolate
import warnings 
warnings.simplefilter(action='ignore', category=UserWarning)


database = 'Pushing-P-DB'
table2 = 'dbo.NJ_Census_Tracts'
table3 = 'dbo.NJ_County_Info'
table4 = 'dbo.Live_Feed'
user = 'pushing_p'
password  = 't3stP@ssword'
server = 'gen10-data-fundamentals-22-02-sql-server.database.windows.net'

col_dict = {
'NUI, Under 6 years': '% Uninsured, Under 6 years',
'NUI, 6-18 years': '% Uninsured, 6-18 years',
'NUI, 19 to 25 years': '% Uninsured, 19 to 25 years',
'NUI, 26 to 34 years': '% Uninsured, 26 to 34 years',
'NUI, 35 to 44 years': '% Uninsured, 35 to 44 years',
'NUI, 45 to 54 years': '% Uninsured, 45 to 54 years',
'NUI, 55 to 64 years': '% Uninsured, 55 to 64 years',
'NUI, 65 years and older': '% Uninsured, 65 years and older',
'NUI, Men': '% Uninsured, Men',
'NUI, Women': '% Uninsured, Women',
'NUI, White': '% Uninsured, White',
'NUI, African American': '% Uninsured, African American',
'NUI, American Indian & Alaska Natives': '% Uninsured, American Indian & Alaska Natives',
'NUI, Asians': '% Uninsured, Asians',
'NUI, Native Hawaiians & Pacific Islanders': '% Uninsured, Native Hawaiians & Pacific Islanders',
'NUI, Other Races': '% Uninsured, Other Races'}

percent_cols = list(col_dict.values())
numeric_cols = list(col_dict.keys())


def Get_Data(table):
    try:
        conn = pymssql.connect(server,user,password,database)

        # Query select all rows from SQL tables to insert into their respective DataFrames
        query = f'SELECT * FROM {table}'

        df = pd.read_sql(query, conn)

        def convert_to_polygon(hex):
            return wkb.loads(hex, hex=True)

        df['geometry'] = df['geometry'].apply(convert_to_polygon)
        
        df.dropna(inplace=True)

        df[['City Population','Uninsured Population']] = df[['City Population','Uninsured Population']].astype(int)

        df[numeric_cols] = df[numeric_cols].astype(float)

        df[percent_cols] = df[numeric_cols].div(df['Uninsured Population'], axis=0)

        df[percent_cols] = df[percent_cols].apply(lambda x: x * 100)

        # converting to geopandas dataframe
        df = gpd.GeoDataFrame(df, geometry=df['geometry'], crs = 'epsg:4269')

        # This is where I format the TimeStamp to "ms" and then I have to for some reason use ".dt.strftime('%Y-%m-%d %H:%M:%S')" because the format in the table chances when I print it out
#         df['TimeStamp'] = pd.to_datetime(df['TimeStamp'], unit='ms').dt.strftime('%Y-%m-%d %H:%M:%S')

        # This is where I order based off of timestamp for my fifth dataframe
#         df = df.sort_values(by='TimeStamp',ascending=False)

        return df

    except Exception as e:
        raise e


tracts = Get_Data(table2)
counties = Get_Data(table3)
live_feed = Get_Data(table4)



def Make_Plots(counties, cities, tracts):

    county_name = live_feed.at[0, 'County']
    counties = counties.loc[counties['County'] == county_name]
    counties = counties.set_index('County')

    # County Map
    px.set_mapbox_access_token('pk.eyJ1IjoiYWhhZGg3NjIiLCJhIjoiY2wzaTBqbnQ2MGU2cjNqbzZpNXFiZHk1eSJ9.UTxbELXv9gk6QiowY1VgqA')
    fig1 = px.choropleth_mapbox(counties, geojson=counties.__geo_interface__, locations=counties.index, color='% Uninsured, Asians',
                            mapbox_style="outdoors", color_continuous_scale='Viridis_r',
                            zoom=6, center = {"lat": 40.058300, "lon": -74.405700},  # Lat long is centerpoint of NJ State
                            )

    fig1.update_layout(
        margin=dict(l=35, r=35, t=35, b=35), # change margin dimensions
        title = f'NUI, Asians in {county_name}',
        width = 380,
        height = 380,
        paper_bgcolor="LightSteelBlue", # set background color
        coloraxis_showscale=False, # hides colorscale
        title_x = 0.5 # centers title
    )

    fig1['layout']['title']['font'] = dict(size=14) # Set title fontsize

    fig1.update_geos(fitbounds="locations")

    # Get Centerpoint of County
    lon = float(counties.centroid.x.values[0])
    lat = float(counties.centroid.y.values[0])

    cities = cities.set_index('City')

    # City Map
    fig2 = px.choropleth_mapbox(cities, geojson=cities.__geo_interface__, locations=cities.index, color='% Uninsured, Asians',
                            mapbox_style="outdoors", color_continuous_scale='Viridis_r',
                            zoom=7.0, center = {"lat": lat , "lon": lon},
                            )

    fig2.update_layout(
        margin=dict(l=35, r=35, t=35, b=35),
        title = f'NUI, Asians in {county_name} Cities',
        width = 500,
        height = 380,
        paper_bgcolor="LightSteelBlue",
        title_x = 0.5
        )

    fig2['layout']['title']['font'] = dict(size=14)
    fig2.update_geos(fitbounds="locations")


    # Predicted Census Tracts Map
    tracts = tracts.loc[tracts['County'] == county_name]
    tracts = tracts.set_index('Census Tract')

    extensive_variables = numeric_cols + ['Uninsured Population']
    model = area_interpolate(source_df=cities, target_df=tracts, intensive_variables = ['Unemployment Rate (16 & Over)'], extensive_variables = extensive_variables)

    model[percent_cols] = model[numeric_cols].div(model['Uninsured Population'], axis=0)
    model[percent_cols] = model[percent_cols].apply(lambda x: x * 100)

    model = model.set_index(tracts.index.copy())

    fig3 = px.choropleth_mapbox(model, geojson=model.__geo_interface__, locations=model.index, color='% Uninsured, White',
                            mapbox_style="outdoors", color_continuous_scale='Viridis_r',
                            zoom=7.8, center = {"lat": lat , "lon": lon},
                            )

    fig3.update_layout(
        margin=dict(l=35, r=35, t=35, b=35),
        title = f'% Uninsured, White in {county_name} Census Tracts (Predicted)',  title_x = 0.5,
        width = 380,
        height = 380,
        paper_bgcolor="LightSteelBlue")

    fig3['layout']['title']['font'] = dict(size=14)
    fig3.update_geos(fitbounds="locations")


    # Actual Census Tracts Map
    fig4 = px.choropleth_mapbox(tracts, geojson=tracts.__geo_interface__, locations=tracts.index, color='% Uninsured, White',
                            mapbox_style="outdoors", color_continuous_scale='Viridis_r',
                            zoom=7.8, center = {"lat": lat , "lon": lon},
                            )

    fig4.update_layout(
        margin=dict(l=35, r=35, t=35, b=35),
        title = f'% Uninsured, White in {county_name} Census Tracts (Actual)',  title_x = 0.5,
        width = 380,
        height = 380,
        paper_bgcolor="LightSteelBlue")

    fig4['layout']['title']['font'] = dict(size=14)
    fig4.update_geos(fitbounds="locations")


    return fig1, fig2, fig3, fig4


fig1, fig2, fig3, fig4 = Make_Plots(counties, live_feed, tracts)

# CSS Styling

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(
    external_stylesheets=external_stylesheets)

# Dash Application Layout
app.layout = html.Div(children = [
        
    dcc.Graph(id = 'County Map',
    figure = fig1),

    dcc.Graph(id = 'City Map',
    figure = fig2),

    dcc.Graph(id = 'Predicted Census Tract Map',
    figure = fig3),

    dcc.Graph(id = 'Actual Census Tract Map',
    figure = fig4)
    



])

# Update All Plots
# @app.callback([Output('Pokemon Point Map', 'figure'),
#                 Output('Pokemon Heat Map', 'figure'),
#                 Output('Most Popular Pokemon', 'figure'),
#                 Output('Most Popular Type', 'figure'),
#                 Output('100 Most-Recent Pokemon', 'figure')],
#               Input('interval-component', 'n_intervals'))

# def Update_Plots(n):
#     fig1, fig2, fig3, fig4, fig5 = Make_Plots()

#     return fig1, fig2, fig3, fig4, fig5


# Execute Program
if __name__ == '__main__':
    app.run_server(debug=False)