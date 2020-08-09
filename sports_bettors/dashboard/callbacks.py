import pandas as pd
import plotly.express as px

from sports_bettors.dashboard.params import params, utils
from sports_bettors.dashboard.utils.history import populate as history_populate
from sports_bettors.dashboard.utils.results import populate as results_populate

from config import Config


class ConfigCallbacks(object):
    """
    Configure the layout to create inputs and display html elements
    """
    @staticmethod
    def dropdowns(league: str):
        team_opts = params[Config.version]['team-opts'][league]
        feature_set_opts = params[Config.version]['feature-sets-opts'][league]
        return team_opts, utils['show'], team_opts, utils['show'], feature_set_opts, utils['show']

    @staticmethod
    def variables(league: str, feature_set: str):
        """
        Populate and show a drop down that selects the "variable" to span for results
        """
        if (league is None) or (feature_set is None):
            return [], utils['no_show']
        variable_opts = params[Config.version]['variable-opts'][league][feature_set]
        return variable_opts, utils['show']

    @staticmethod
    def parameters(feature_set: str, variable: str, league: str):
        """
        Populate and show inputs for defining parameters of the input model
        """
        if (league is None) or (feature_set is None) or (variable is None):
            return [None] * 4 + [None] * 4 + [utils['no_show']] * 4
        # Get parameters except for variable
        parameters = [
            p['label'] for p in params[Config.version]['variable-opts'][league][feature_set] if p['value'] != variable
        ]
        # Fill displays and Nones
        displays = [utils['show']] * len(parameters) + [utils['no_show']] * (4 - len(parameters))
        parameters += [None] * (4 - len(parameters))

        return parameters + parameters + displays


class DataCallbacks(object):
    """
    Generate the historical and results-based data to display in the dashboard
    """
    @staticmethod
    def history(league: str, team: str, opponent: str):
        """
        Load data for historical matchups
        """
        df, x_opts, y_opts = history_populate(league, team, opponent)
        return df.to_json(), x_opts, y_opts

    @staticmethod
    def results(league: str, feature_set: str, team: str, opponent: str, variable: str, *parameters):
        """
        Calculate probabilities
        """
        # Drop nones
        parameters = [p for p in parameters if p]
        # Convert to dictionary
        parameters = {k: v for k, v in zip(parameters[::2], parameters[1::2])} if len(parameters) > 1 else {}

        # Get results
        df = results_populate(
            league=league,
            feature_set=feature_set,
            team=team,
            opponent=opponent,
            variable=variable,
            parameters=parameters
        )
        return df.to_json()


class PlotCallbacks(object):
    """
    Generate plotly figures from history and results
    """
    @staticmethod
    def history(df, x: str, y: str):
        """
        Plot historical data
        """
        df = pd.read_json(df, orient='records')
        if df.shape[0] == 0:
            return utils['empty_figure'], utils['no_show'], utils['no_show']
        x = df.columns[0] if not x else x
        y = df.columns[0] if not y else y
        fig = px.scatter(df, x=x, y=y, color='Winner')
        return fig, utils['show'], utils['show']

    @staticmethod
    def results(df):
        """
        Plot results
        """
        df = pd.read_json(df, orient='records')
        if df.shape[0] == 0:
            return utils['empty_figure'], utils['empty_figure']
        fig = px.line(df, x='total_points', y='Win')
        return fig, fig

