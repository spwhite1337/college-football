import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd

from sports_bettors.dashboard.params import params, utils
from sports_bettors.dashboard.callbacks import ConfigCallbacks, DataCallbacks, PlotCallbacks


from config import Config


def add_sb_dash(server, routes_pathname_prefix: str = '/api/dash/sportsbettors/'):
    """
    Add a sports-bettors dashboard over a flask app at the provided endpoint
    """
    dashapp = dash.Dash(
        __name__,
        routes_pathname_prefix=routes_pathname_prefix,
        server=server
    )

    dashapp.layout = html.Div(children=[
        html.H1('Hi From Dash (sports bettors)'),
        html.Div(id='selectors', children=[
            dcc.Dropdown(id='league', options=params[Config.sb_version]['league-opts'], value='college_football'),
            dcc.Dropdown(id='team', style=utils['no_show']),
            dcc.Dropdown(id='opponent', style=utils['no_show']),
        ]),

        # History
        html.Div(id='history', children=[
            html.Div(id='history-data', style=utils['no_show'], children=pd.DataFrame().to_json()),
            dcc.Dropdown(id='history-x', style=utils['no_show']),
            dcc.Dropdown(id='history-y', style=utils['no_show']),
            html.Button('Update History', id='update-history-data', n_clicks=0),
            dcc.Graph(id='history-fig'),
        ]),

        # Results
        html.Div(id='results', children=[
            html.Div(id='results-win-data', style=utils['no_show'], children=pd.DataFrame().to_json()),
            html.Div(id='results-conditioned-margin-data', style=utils['no_show'], children=pd.DataFrame().to_json()),
            dcc.Dropdown(id='feature-sets', style=utils['no_show']),
            dcc.Dropdown(id='variable', style=utils['no_show']),
            dcc.Input(id='parameter-1', style=utils['no_show']),
            dcc.Input(id='parameter-2', style=utils['no_show']),
            dcc.Input(id='parameter-3', style=utils['no_show']),
            dcc.Input(id='parameter-4', style=utils['no_show']),
            html.Button('Update Results', id='update-results-data', n_clicks=0),
            dcc.Graph(id='win-fig', figure=utils['empty_figure']),
            dcc.Graph(id='conditioned-margin-fig', figure=utils['empty_figure'])
        ]),
    ])

    # Drop down configuration
    @dashapp.callback(
        [
            Output('team', 'options'),
            Output('team', 'style'),
            Output('opponent', 'options'),
            Output('opponent', 'style'),
            Output('feature-sets', 'options'),
            Output('feature-sets', 'style'),
        ],
        [
            Input('league', 'value')
        ]
    )
    def config_dropdowns(league):
        return ConfigCallbacks.dropdowns(league)

    # Variable Selection
    @dashapp.callback(
        [
            Output('variable', 'options'),
            Output('variable', 'style')
        ],
        [
            Input('league', 'value'),
            Input('feature-sets', 'value'),
        ]
    )
    def config_variables(league, feature_set):
        return ConfigCallbacks.variables(league, feature_set)

    # Parameter Selection
    @dashapp.callback(
        [
            Output('parameter-1', 'label'),
            Output('parameter-2', 'label'),
            Output('parameter-3', 'label'),
            Output('parameter-4', 'label'),
            Output('parameter-1', 'placeholder'),
            Output('parameter-2', 'placeholder'),
            Output('parameter-3', 'placeholder'),
            Output('parameter-4', 'placeholder'),
            Output('parameter-1', 'style'),
            Output('parameter-2', 'style'),
            Output('parameter-3', 'style'),
            Output('parameter-4', 'style')
        ],
        [
            Input('feature-sets', 'value'),
            Input('variable', 'value')
        ],
        [
            State('league', 'value')
        ]
    )
    def config_parameters(feature_set, variable, league):
        return ConfigCallbacks.parameters(feature_set, variable, league)

    # Populate with history
    @dashapp.callback(
        [
            Output('history-data', 'children'),
            Output('history-x', 'options'),
            Output('history-y', 'options')
        ],
        [
            Input('update-history-data', 'n_clicks'),
            Input('league', 'value'),
        ],
        [
            State('team', 'value'),
            State('opponent', 'value')
        ]
    )
    def history_data(trigger, league, team, opponent):
        return DataCallbacks.history(league, team, opponent)

    # Make the figure
    @dashapp.callback(
        [
            Output('history-fig', 'figure'),
            Output('history-x', 'style'),
            Output('history-y', 'style')
         ],
        [
            Input('history-data', 'children'),
            Input('history-x', 'value'),
            Input('history-y', 'value')
        ]
    )
    def history_figures(df, x, y):
        return PlotCallbacks.history(df, x, y)

    # Populate with results
    @dashapp.callback(
        [
            Output('results-win-data', 'children'),
            Output('results-conditioned-margin-data', 'children'),
        ],
        [
            Input('update-results-data', 'n_clicks')
        ],
        [
            State('league', 'value'),
            State('feature-sets', 'value'),
            State('team', 'value'),
            State('opponent', 'value'),
            State('variable', 'value'),
            State('parameter-1', 'label'),
            State('parameter-1', 'value'),
            State('parameter-2', 'label'),
            State('parameter-2', 'value'),
            State('parameter-3', 'label'),
            State('parameter-3', 'value'),
            State('parameter-4', 'label'),
            State('parameter-4', 'value')
        ]
    )
    def results_data(trigger, league, feature_set, team, opponent, variable, *parameters):
        return DataCallbacks.results(league, feature_set, team, opponent, variable, *parameters)

    # Win figure
    @dashapp.callback(
        Output('win-fig', 'figure'),
        [
            Input('results-win-data', 'children')
        ],
        [
            State('variable', 'value')
        ]
    )
    def win_figure(df, variable):
        return PlotCallbacks.win_figure(df, variable)

    # conditioned-margin figure
    @dashapp.callback(
        Output('conditioned-margin-fig', 'figure'),
        [
            Input('results-conditioned-margin-data', 'children'),
            Input('win-fig', 'hoverData')
        ]
    )
    def conditioned_margin_figure(df, variable_val):
        return PlotCallbacks.conditioned_margin_figure(df, variable_val)

    return dashapp.server
