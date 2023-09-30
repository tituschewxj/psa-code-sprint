# Import necessary libraries
from dash import Dash, dcc, html, Input, Output, callback
import pandas as pd

# Initialize the Dash app
app = Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

# Define the app layout
app.layout = html.Div(style={
        'backgroundColor': colors['background'],
        'color': '#77b0b1',
        'height': '100vh',
        'margin': '0',
        'padding': '0',
        'display': 'flex'
    },
    children=[
        html.Div(style={
            'flex': '1',
            'padding': '20px'
        }, children=[
            html.H1(
                children="Port Management Dashboard",
                style={
                    'textAlign': 'center',
                    'color': colors['text']
                }
            ),
            
            # Slider for Temperature
            html.Label(
                'Temperature',
                style={
                    'color': colors['text']
                }
            ),
            dcc.Slider(
                id='temperature-slider',
                min=-10,
                max=50,
                value=25,
                marks={i: '{}°C'.format(i) for i in range(-10, 51, 10)},
                step=0.5
            ),
            
            # Slider for Humidity
            html.Label(
                'Humidity',
                style={
                    'color': colors['text']
                }
            ),
            dcc.Slider(
                id='humidity-slider',
                min=0,
                max=100,
                value=50,
                marks={i: '{}%'.format(i) for i in range(0, 101, 10)},
                step=1
            ),
            
            # Drop-down for Weather Conditions
            html.Label(
                'Weather Condition',
                style={
                    'color': colors['text']
                }
            ),
            dcc.Dropdown(
                id='weather-dropdown',
                options=[
                    {'label': 'Sunny', 'value': 'Sunny'},
                    {'label': 'Rainy', 'value': 'Rainy'},
                    {'label': 'Stormy', 'value': 'Stormy'}
                ],
                value='Sunny'
            ),
        ]),
        
        html.Div(style={
            'flex': '2',  # Take up 2 portions of the available space
            'padding': '20px'
        }, children=[
            # Output
            html.Div(id='output-container'),
            # Map of PSA Tuas Port
            dcc.Graph(
                id='psa-port-map',
                figure={
                    'data': [
                        # Add ship annotations
                        {
                            'type': 'scattermapbox',
                            'lat': [1.2425, 1.2415],
                            'lon': [103.6173, 103.6164],
                            'mode': 'markers',
                            'marker': {
                                'size': 15,
                                'symbol': 'harbor',
                                'color': 'red'
                            },
                            'text': ['Ship 1', 'Ship 2']
                        }
                    ],
                    'layout': {
                        'mapbox': {
                            'center': {
                                'lat': 1.2419963411115098,
                                'lon': 103.61685812074866
                            },
                            'zoom': 14,
                            'style': 'open-street-map'
                        },
                        'margin': {
                            'l': 0,
                            'r': 0,
                            'b': 0,
                            't': 0
                        }
                    }
                }
            ),
        ])
    ]
)

# Define callback to update output
@callback(
    Output(component_id='output-container', component_property='children'),
    [
        Input(component_id='temperature-slider', component_property='value'),
        Input(component_id='humidity-slider', component_property='value'),
        Input(component_id='weather-dropdown', component_property='value')
    ]
)
def update_output(temp, humidity, weather):
    return f'Temperature is: {temp}°C, Humidity is: {humidity}%, Weather condition is: {weather}'

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
