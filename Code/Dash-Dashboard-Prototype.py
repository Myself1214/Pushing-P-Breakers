from dash import Dash
import pandas as pd

# I fixed your imports for dash.dcc and dash.html,  the reason you were getting a warning message was because the way you imported the library worked 
# but was an outdated method of doing it

from dash import dcc,html
import plotly.express as px
from dash.dependencies import Input, Output
import pymssql
import plotly.graph_objects as go
import numpy as np
import plotly.graph_objects as go

import warnings # The method used in class gives a warning when using pd.read_sql, this will ignore the warning message
warnings.simplefilter(action='ignore', category=UserWarning)

database = "Pushing-P-DB"
table = "dbo.Live_Feed"
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
        df['Rate Of Uninsured'] = (df['Uninsured Population']/df['City Population'])
        df['Rate Of Uninsured'] = df['Rate Of Uninsured'].round(decimals = 5)
        df['Insured Population'] = df['City Population'] - df['Uninsured Population']
        df['Insured Population'] = df['Insured Population'].round(decimals = 5)
        df['Rate Of Insured'] = df['Insured Population'] / df['City Population']
        df['Rate Of Insured'] = df['Rate Of Insured'].round(decimals = 5)

        # This is where I format the TimeStamp to "ms" and then I have to for some reason use ".dt.strftime('%Y-%m-%d %H:%M:%S')" because the format in the table chances when I print it out
#         df['TimeStamp'] = pd.to_datetime(df['TimeStamp'], unit='ms').dt.strftime('%Y-%m-%d %H:%M:%S')

        # This is where I order based off of timestamp for my fifth dataframe
#         df = df.sort_values(by='TimeStamp',ascending=False)

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

    county_name = df.County[0]

    # Here I set the colors I will be using for the visualizations
    colors = {
        'background': '#111111',
        'text': '#7FDBFF'
    }
#  1. GAUGE VISUAL PLACE
    df1 = df[['Uninsured Population','City Population']].sum()
    # df1

    fig_1 = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = df1[['Uninsured Population']].sum(),
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': f'Total Number of Uninsured for {county_name}', 'font': {'size': 24}},
        delta = {'reference': df1['City Population'], 'increasing': {'color': "RebeccaPurple"}},
        gauge = {
            'axis': {'range': [None, 1000000], 'tickwidth': 1, 'tickcolor': "red"},
            'bar': {'color': "darkblue"},
            'bgcolor': "red",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 500000], 'color': 'cyan'},
                {'range': [500000, 750000], 'color': 'yellow'}],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 1000000}}))

    fig_1.update_layout(paper_bgcolor = "#111111", font = {'color': "lightblue", 'family': "Arial"})


# 2. % OF UNINSURED VISUAL PLACE
    

    # # this is where I center the title for the visualization
    # fig_2.update_layout(
    #     title=dict(x=0.5), #set title in the center
    #     plot_bgcolor=colors['background'],
    #     paper_bgcolor=colors['background'],
    #     font_color=colors['text'],
    # )

   
# 3. LINE GRAPH MALE/FEMALE VS. TIMESTAMP VISUAL PLACE
    
    

#     # this is where I center the title for the visualization
#     fig_3.update_layout(
#         title=dict(x=0.5), #set title in the center
#         plot_bgcolor=colors['background'],
#         paper_bgcolor=colors['background'],
#         font_color=colors['text'],
#     )

    
# 4. BAR % UNINSURED VS. AGE
   
    df4= df[['State','County','City','NUI, Under 6 years', 'NUI, 6-18 years', 'NUI, 19 to 25 years',
    'NUI, 26 to 34 years', 'NUI, 35 to 44 years', 'NUI, 45 to 54 years',
    'NUI, 55 to 64 years', 'NUI, 65 years and older','Rate Of Uninsured']]

    df4 = df4 [['NUI, Under 6 years', 'NUI, 6-18 years', 'NUI, 19 to 25 years',
    'NUI, 26 to 34 years', 'NUI, 35 to 44 years', 'NUI, 45 to 54 years',
    'NUI, 55 to 64 years', 'NUI, 65 years and older']].sum()

    df4 = pd.DataFrame(df4)

    df4 = df4.reset_index()

    # Didnt use an equals sign because this just renames the existing dataframe instead of renaming a copy of the dataframe.
    df4.rename(columns = {'index':'Age', 0:'Number Of Uninsured'}, inplace = True)

    State_Uninsured = df['Uninsured Population'].sum()

    df4['Uninsured Rate By Age'] = df4['Number Of Uninsured']/State_Uninsured * 100

    df4['Uninsured Rate By Age'] = df4['Uninsured Rate By Age'].round(decimals = 2)


    fig_4 = px.bar(df4, x='Age', y='Uninsured Rate By Age',color_discrete_sequence=["green"], title= f'The Rate Of Uninsured By Age For {county_name}', height = 500, width = 700)
    fig_4.update_layout(xaxis={'categoryorder':'total descending'})


    # this is where I center the title for the visualization
    fig_4.update_layout(
        title=dict(x=0.5), #set title in the center
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
    )
   
# 5. BAR % UNINSURED VS. RACE
   
    df5= df[['NUI, White', 'NUI, African American','NUI, American Indian & Alaska Natives',
    'NUI, Asians','NUI, Native Hawaiians & Pacific Islanders', 'NUI, Other Races','Rate Of Uninsured']]

    df5.rename(columns = {'NUI, American Indian & Alaska Natives':'NUI, American I. & Alaska N.', 'NUI, Native Hawaiians & Pacific Islanders':'NUI, Native H. & Pacific I.'}, inplace = True)

    df5 = df5[['NUI, White', 'NUI, African American','NUI, American I. & Alaska N.',
    'NUI, Asians','NUI, Native H. & Pacific I.', 'NUI, Other Races']].sum()

    df5 = pd.DataFrame(df5)

    df5 = df5.reset_index()

    # # Didnt use an equals sign because this just renames the existing dataframe instead of renaming a copy of the dataframe.
    df5.rename(columns = {'index':'Race', 0:'Number Of Uninsured'}, inplace = True)

    State_Uninsured = df['Uninsured Population'].sum()

    df5['Uninsured Rate By Race'] = df5['Number Of Uninsured']/State_Uninsured * 100

    df5['Uninsured Rate By Race'] = df5['Uninsured Rate By Race'].round(decimals = 2)


    fig_5 = px.bar(df5, x='Race', y='Uninsured Rate By Race',color_discrete_sequence=["blue"], title= f'The Rate Of Uninsured By Race For {county_name}', height = 500, width = 700)
    fig_5.update_layout(xaxis={'categoryorder':'total descending'})

    # this is where I center the title for the visualization
    fig_5.update_layout(
        title=dict(x=0.7), #set title in the center
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
    )

# 6. TABLE TOP 10 UNINSURED CITIES VISUAL PLACE

    df6= df[['City','Uninsured Population','Rate Of Uninsured']]

    df6 = df6.sort_values(by='Rate Of Uninsured', ascending =False)

    df6 = df6.head(10)

    fig_6 = go.Figure(data=[go.Table(
        header=dict(values=df6.columns,
                    fill_color='#3F7674',
                    align='left'),
        cells=dict(values=[df6.City, df6['Rate Of Uninsured'], df6['Uninsured Population']],
                fill_color='black',
                align='left'))
    ])

    fig_6.update_layout(
        title = f'Top 10 Uninsured Cities by Rate in {county_name}', # this is where I add the title for my table
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color='white'
    )

    fig_6.update_layout(
        title=dict(x=0.5)
    )

# 7. DONUTS VISUAL ONE PLACE
    df7 = df

    df7['Employment Rate'] = 100 - df['Unemployment Rate (16 & Over)']

    df7.rename(columns = {'Unemployment Rate (16 & Over)': 'Unemployment Rate'}, inplace = True)

    df7 = df7[['County','Insured Population', 'Uninsured Population','Unemployment Rate','Employment Rate']].sum()

    df7 = pd.DataFrame(df7)

    df7 = df7.reset_index()

    df7.rename(columns = {'index':'Variables', 0:'Sum'}, inplace = True)

    df7 = df7.loc[1:]

    df7_1 = df7.iloc[:2,:]

    colors = ['lime','orange']
    fig_7 = go.Figure(data = go.Pie(values = df7_1.Sum, 
                            labels = df7_1.Variables, hole = 0.6,
                            marker_colors = colors,
                    ))
    fig_7.update_traces(
                    title_font=dict(size=30,family='Verdana', 
                                    color='white'),
                                    hoverinfo='label+percent',
                                    textinfo='percent', 
                                    textfont_size=20,
                    )

    fig_7.update_layout(legend=dict(y=1.1, x = 0.8), title = f'Insured and Uninsured Population in {county_name}',
    paper_bgcolor = '#111111', font = {'color': "white", 'family': "Arial"})
    fig_7.update_layout(title=dict(x=0.5), title_font=dict(size= 15)) #set title in the center)

# 8. DONUTS VISUAL TWO PLACE

    df7_2 = df7.iloc[2:4,:]

    colors = ['red','blue']
    fig_8 = go.Figure(data = go.Pie(values = df7_2.Sum, 
                            labels = df7_2.Variables, hole = 0.6,
                            marker_colors = colors,
                    ))
    fig_8.update_traces(
                    title_font=dict(size=30,family='Verdana', 
                                    color='white'),
                                    hoverinfo='label+percent',
                                    textinfo='percent', 
                                    textfont_size=20,
                    )

    fig_8.update_layout(legend=dict(y=1.1, x = 0.8), title = f'Employed and Unemployed Rate in {county_name}',
    paper_bgcolor = "#111111", font = {'color': "white", 'family': "Arial"})
    fig_8.update_layout(title=dict(x=0.5), title_font=dict(size= 15)) #set title in the center)

# 9. HEAT MAP % OF UNINSURED VISUAL PLACE




# 10. ML PREDICTION VISUAL










    return fig_1, fig_4, fig_5, fig_6, fig_7, fig_8

df = Get_Data()
fig_1, fig_4, fig_5, fig_6, fig_7, fig_8 = Make_Plots(df)


app = Dash(__name__)

app.layout = html.Div(
    # children=[
    #     html.Div(
    #         children=[
    #             # here I add the emoji
    #             html.P(children="🚓", style={'fontSize': "30px",'textAlign': 'center'}, className="header-emoji"), 
    #             #Header title
    #             html.H1(
    #                 children="The Metrics of Uninsured",style={'textAlign': 'center'}, className="header-title" 
    #             ),
    #             #Description below the header
    #             html.H2(
    #                 children="Analyzing Uninsurance Data",
    #                 className="header-description", style={'textAlign': 'center'},
    #             ),
    #         ],
    #         className="header",style={'backgroundColor':'#111111', 'color': '#7FDBFF'},
    #     ),
        
        
    #     html.Div(
    #         children=[
    #             html.Div(children = 'Name', style={'fontSize': "24px",'backgroundColor':'#111111', 'color': '#7FDBFF'},className = 'menu-title'),
    #             #the dropdown function
    #             dcc.Dropdown(
    #                 id = 'name-filter',
    #                 options = [
    #                     {'label': Name, 'value':Name}
    #                     for Name in df.Name.unique()
    #                 ],
    #                 value = df.Name,
    #                 clearable = True,
    #                 searchable = True,
    #                 className = 'dropdown', style={'fontSize': "18px",'textAlign': 'center', 'backgroundColor':'#111111', 'color': '#7FDBFF'},
    #             ),
    #         ],
    #         className = 'menu', style={'fontSize': "18px",'textAlign': 'center', 'backgroundColor':'#111111', 'color': '#423A38'},
    #     ),
        
        # the four graphs
            children=[
                html.Div(
                children = dcc.Graph(
                    id = 'Gauge',
                    figure = fig_1,
                  #  config={"displayModeBar": False},
                ),
                style={'width': '50%', 'height': '70%', 'display': 'inline-block'},
            ),
            #     html.Div(
            #     children = dcc.Graph(
            #         id = '',
            #         figure = fig_2,
            #         #config={"displayModeBar": False},
            #     ),
            #     style={'width': '50%', 'display': 'inline-block'},
            # ),
            #     html.Div(
            #     children = dcc.Graph(
            #         id = '',
            #         figure = fig_3,
            #         #config={"displayModeBar": False},
            #     ),
            #     style={'width': '50%', 'display': 'inline-block'},
            # ),
                html.Div(
                children = dcc.Graph(
                    id = '% UNINSURED VS AGE',
                    figure = fig_4,
                    #config={"displayModeBar": False},
                ),
                style={'width': '50%', 'display': 'inline-block'},    
            ),
                
                html.Div(
                children = dcc.Graph(
                    id = 'Race',
                    figure = fig_5,
                    # config={"displayModeBar": False},
                ),
                style={'width': '50%','display': 'inline-block'}, # height part of style doesn't work
            ),
                
                
                 html.Div(
                children = dcc.Graph(
                    id = 'Table',
                    figure = fig_6,
                    #config={"displayModeBar": False},
                ),
                style={'width': '40%', 'display': 'inline-block'},
            ),
                
                
                
                html.Div(
                children = dcc.Graph(
                    id = 'donut-1',
                    figure = fig_7,
                    #config={"displayModeBar": False},
                ),
                style={'width': '50%', 'display': 'inline-block'},
            ),
                
                
                
                html.Div(
                children = dcc.Graph(
                    id = 'donut-2',
                    figure = fig_8,
                    #config={"displayModeBar": False},
                ),
                style={'width': '50%', 'display': 'inline-block'},
            ),
                
                
                
            #     html.Div(
            #     children = dcc.Graph(
            #         id = '',
            #         figure = fig_9,
            #         #config={"displayModeBar": False},
            #     ),
            #     style={'width': '50%', 'display': 'inline-block'},
            # ),

            #     html.Div(
            #     children = dcc.Graph(
            #         id = '',
            #         figure = fig_10,
            #         #config={"displayModeBar": False},
            #     ),
            #     style={'width': '50%', 'display': 'inline-block'},
            # ),
                
                dcc.Interval(
                id='interval-component',
                interval= 5000, # in milliseconds (there will be an update once every minute)
                n_intervals=0)
        ],
        className = 'double-graph'
        # )
    # ]
)

# One callback will update all 5 figures
@app.callback(
    Output("Gauge", "figure"),
    # Output("", "figure"),
    # Output("", "figure"),
    Output("% UNINSURED VS AGE", "figure"),
    Output("Race", "figure"),
    Output("Table", "figure"),
    Output("donut-1", "figure"),
    Output("donut-2", "figure"),
    # Output("", "figure"),
    # Output("", "figure")), # the output is the map
    Input("interval-component", "n_intervals") # this input is the dcc.Interval id ("interval-component") and "n_intervals" 
)

def update_charts(n):

    df = Get_Data()

    fig_1, fig_4, fig_5, fig_6, fig_7, fig_8  = Make_Plots(df)

    return fig_1, fig_4, fig_5, fig_6, fig_7, fig_8


if __name__ == '__main__':
    app.run_server(debug = True)

