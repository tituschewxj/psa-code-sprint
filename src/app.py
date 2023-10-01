from dash import Dash, dcc, html, Input, Output, State, callback, callback_context, dash_table, no_update
import base64
import datetime
import io
import pandas as pd

class PortManagementDashboard:
    def __init__(self):
        self.app = Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])
        self.mean_ships = 0
        self.colors = {
            'background': '#111111',
            'text': '#7FDBFF'
        }
        self.layout()
        self.callbacks()

    def layout(self):
        self.app.layout = html.Div(style={
                'backgroundColor': self.colors['background'],
                'min-height': '98.3vh',
                'margin': '0',
                'padding': '0',
                'display': 'flex',
                'color': '#CCCCCC'
            },
            children=[
                html.Div(style={
                    'flex': '1',
                    'padding': '20px',
                }, children=[
                    html.H1(
                        children="Port Management Dashboard",
                        style={
                            'textAlign': 'center',
                            'color': self.colors['text']
                        }
                    ),
                    
                    html.Label(
                        'Temperature',
                        style={
                            'color': self.colors['text']
                        }
                    ),
                    html.Div(
                        children=[
                            dcc.Slider(id='temperature-slider', min=-10, max=50, value=25, marks={i: '{}°C'.format(i) for i in range(-10, 51, 10)}, step=0.1),
                            dcc.Input(id='temperature-input', type='number', value=25, min=-10, max=50, step=0.1),
                        ]
                    ),
                    
                    html.Label(
                        'Humidity (%)',
                        style={
                            'color': self.colors['text']
                        }
                    ),
                    html.Div(
                        children=[
                            dcc.Slider(id='humidity-slider', min=0, max=100, value=50, marks={i: str(i) for i in range(0, 101, 10)}, step=0.1),
                            dcc.Input(id='humidity-input', type='number', value=50, min=0, max=100, step=0.1),
                        ]
                    ),
                    
                    html.Label(
                        'Weather Condition',
                        style={
                            'color': self.colors['text']
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

                    html.Label(
                        "World Economic Growth Rate (%)",
                        style={
                            'color': self.colors['text']
                        }
                    ),
                    html.Div(
                        children=[
                            dcc.Slider(id='economic-growth-slider', min=0, max=10, value=3, marks={i: str(i) for i in range(0, 11, 1)}, step=0.1),
                            dcc.Input(id='economic-growth-input', type='number', value=3, min=0, max=10, step=0.1),
                        ]
                    ),

                    html.Label(
                        'Average Fuel Price (USD/mt)',
                        style={
                            'color': self.colors['text']
                        }
                    ),
                    dcc.Input(id='fuel-price-input', type='number', value=680, min=0, step=0.01),

                    # Upload component
                    html.Label(
                        'Historical Ship Arrivals',
                        style={
                            'color': self.colors['text']
                        }
                    ),
                    dcc.Upload(
                        id='upload-data',
                        children=html.Div([
                            'Drag and Drop or ',
                            html.A('Select Excel File'),
                            html.Div(id='uploaded-file-name')
                        ]),
                        style={
                            'width': '100%',
                            'height': '40px',
                            'lineHeight': '40px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center'
                        },
                        multiple=False
                    ),

                    html.Button(
                        'Run Simulation',
                        id='submit-button',
                        n_clicks=0,
                        style={
                            'margin-top': 40,
                            'color': self.colors['text']
                        }
                    )
                ]),
                
                html.Div(style={
                    'flex': '2',
                    'padding': '20px',
                    'maxWidth': '100%',
                    'overflow': 'auto'
                }, children=[
                    html.Div(
                        id='output-container',
                        style={
                            'color': self.colors['text']
                        }
                    ),
                    html.Br(),
                    # Map of PSA Tuas Port
                    dcc.Graph(
                        id='psa-port-map',
                        figure={
                            #'data': [
                            #    # Add ship annotations
                            #    {
                            #        'type': 'scattermapbox',
                            #        'lat': [1.2425, 1.2415],
                            #        'lon': [103.6173, 103.6164],
                            #        'mode': 'markers',
                            #        'marker': {
                            #            'size': 15,
                            #            'symbol': 'circle',
                            #            'color': 'red'
                            #        },
                            #        'text': ['Ship 1', 'Ship 2']
                            #    }
                            #],
                            'layout': {
                                'mapbox': {
                                    'center': {
                                        'lat': 1.236476,
                                        'lon': 103.631922
                                    },
                                    'zoom': 12.5,
                                    'style': 'open-street-map'
                                },
                                'margin': {'l': 0, 'r': 0, 'b': 0, 't': 0}
                            }
                        }
                    ),
                    html.Br(),
                    dash_table.DataTable(id='table',
                        page_size=10,
                        style_table={'overflowX': 'auto', 'color': '#000000'},
                        css=[{'selector': '.first-page, .previous-page, .next-page, .last-page', 'rule': 'color: #FFFF'}]
                    ),
                ])
            ]
        )

    # Define callback to synchronize temperature slider and input values
    @callback(
        [Output('temperature-slider', 'value'),
        Output('temperature-input', 'value')],
        [Input('temperature-slider', 'value'),
        Input('temperature-input', 'value')]
    )
    def sync_temperature(slider_value, input_value):
        ctx = callback_context
        if not ctx.triggered:
            return no_update
        else:
            input_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if input_id == 'temperature-slider':
            return slider_value, slider_value
        elif input_id == 'temperature-input':
            return input_value, input_value
        
    # Define callback to synchronize humidity slider and input values
    @callback(
        [Output('humidity-slider', 'value'),
        Output('humidity-input', 'value')],
        [Input('humidity-slider', 'value'),
        Input('humidity-input', 'value')]
    )
    def sync_humidity(slider_value, input_value):
        ctx = callback_context
        if not ctx.triggered:
            return no_update
        else:
            input_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if input_id == 'humidity-slider':
            return slider_value, slider_value
        elif input_id == 'humidity-input':
            return input_value, input_value
        
    # Define callback to synchronize economic-growth slider and input values
    @callback(
        [Output('economic-growth-slider', 'value'),
        Output('economic-growth-input', 'value')],
        [Input('economic-growth-slider', 'value'),
        Input('economic-growth-input', 'value')]
    )
    def sync_economic_growth(slider_value, input_value):
        ctx = callback_context
        if not ctx.triggered:
            return no_update
        else:
            input_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if input_id == 'economic-growth-slider':
            return slider_value, slider_value
        elif input_id == 'economic-growth-input':
            return input_value, input_value

    # Add a new callback to update the filename in the upload section
    @callback(
        Output('uploaded-file-name', 'children'),
        [Input('upload-data', 'filename')]
    )
    def update_filename(filename):
        if filename:
            return f"Uploaded: {filename}"
        return ""

    # Define callback to update output
    @callback(
        [
            Output(component_id='output-container', component_property='children'),
            Output(component_id='table', component_property='data'),
            Output(component_id='table', component_property='columns')
        ],
        [
            State(component_id='temperature-input', component_property='value'),
            State(component_id='humidity-input', component_property='value'),
            State(component_id='weather-dropdown', component_property='value'),
            State(component_id='economic-growth-input', component_property='value'),
            State(component_id='fuel-price-input', component_property='value'),
            State(component_id='upload-data', component_property='contents'),
            State(component_id='upload-data', component_property='filename')
        ],
        [
            Input(component_id='submit-button', component_property='n_clicks'),
        ]
    )
    def update_output(self, temp, humidity, weather, economic_growth, avg_fuel_price, contents, filename, n_clicks):
        if contents is None:
            return f'Temperature is: {temp}°C, Humidity is: {humidity}%, Weather condition is: {weather}, World economic growth is: {economic_growth}%, Avg fuel price is: USD {avg_fuel_price}', None, None
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        try:
            if 'csv' in filename:
                # Assume that the user uploaded a CSV file
                df = pd.read_csv(
                    io.StringIO(decoded.decode('utf-8')))
            elif 'xls' in filename:
                # Assume that the user uploaded an excel file
                df = pd.read_excel(io.BytesIO(decoded))
        except Exception as e:
            print(e)
            return f'Temperature is: {temp}°C, Humidity is: {humidity}%, Weather condition is: {weather}, World economic growth is: {economic_growth}%, Avg fuel price is: USD {avg_fuel_price}', None, None

        columns = [{"name": i, "id": i} for i in df.columns]
        data = df.to_dict('records')

        self.mean_ships = self.calculate_mean_ships(temp, humidity, weather, economic_growth, avg_fuel_price)

        return f'Temperature is: {temp}°C, Humidity is: {humidity}%, Weather condition is: {weather}, World economic growth is: {economic_growth}%, Avg fuel price is: USD {avg_fuel_price}, Predicted Number of Ships is: {self.mean_ships}', data, columns

    def calculate_mean_ships(temp, humidity, weather, economic_growth, avg_fuel_price):
        # Coefficients (hypothetical values, adjust as needed)
        gamma = 100
        delta = 80
        zeta = 200

        normal_temp = 25  # Example normal temperature in °C
        normal_humidity = 50  # Example normal humidity in %

        # Convert weather condition to a numerical factor
        weather_factors = {'Sunny': 1, 'Rainy': 0, 'Stormy': -1}
        weather_factor = weather_factors.get(weather, 0)

        # Calculate mean ships
        mean_ships = (zeta + 
                    max((-(temp - normal_temp)**2 + 1000) / 5, 0) + 
                    max((-(humidity - normal_humidity)**2 + 3000) / 20, 0) + 
                    gamma * weather_factor + 
                    delta * economic_growth + 
                    max(100000 / (avg_fuel_price - 1200) + 400, 0))
        
        # Ensure mean ships is not below 0
        mean_ships = round(max(mean_ships, 50))
        
        return mean_ships
    
    def get_mean_ships(self):
        return self.mean_ships

# Run the app
if __name__ == '__main__':
    dashboard = PortManagementDashboard()
    dashboard.run()

    # Return values from the model here - to be processed & rendered
    data = None
