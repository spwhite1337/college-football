import pandas as pd
import numpy as np
from scipy.special import expit
from sports_bettors.dashboard.params import params

from sports_bettors.api import SportsPredictor

from config import Config


def win_probability(predictor, league: str, variable: str, feature_set: str, parameters: dict, team: str,
                    opponent: bool):
    """
    Return df of win probability with fields []
    """
    records = []
    for var in params[Config.version]['variable-ranges'][league][variable]:
        # Configure inputs
        input_set = {
            'random_effect': 'team' if not opponent else 'opponent',
            'feature_set': feature_set,
            'inputs': {'RandomEffect': team, variable: var}
        }
        input_set['inputs'].update(parameters)

        # Predict
        output = predictor.predict(**input_set)[('team' if not opponent else 'opponent', feature_set, 'Win')]

        # Wrangle output
        record = {
            'RandomEffect': team,
            variable: var,
            'WinLB': expit(output['mu']['lb']),
            'Win': expit(output['mu']['mean']),
            'WinUB': expit(output['mu']['ub'])
        }
        records.append(record)

    return pd.DataFrame().from_records(records)


def populate(league: str, feature_set: str, team: str, opponent: str, variable: str, parameters: dict):
    """
    Generate a json friendly dataframe of sports-bettors outputs
    """
    if not all([league, feature_set, team, opponent, variable]):
        return pd.DataFrame().from_records([])

    # Select a match-up (team_a and team_b)
    # Plot results for team_a as 'team' and team_b as 'opponent' (inverted)

    # Define a 'variable' for each feature_set, then rest of the conditions are parameters
    # Calculate WinProbability / UB / LB for a range of "variable" values at the fixed parameters
    # For each slice of variable, parameters -> calculate probability of winning by various margins,
    #   loss margins, win-margins
    # Result will be 4 dfs:
    #   - Win Probability as variable is changed
    #       - [variable, parameters, WinProb, WinProbUB, WinProbLB, team]
    #   - Margin Likelihood as variable is changed
    #       - [variable, parameters, margin, CumProb, CumProbLB, CumProbUB, team]
    #   - WinMargin Likelihood
    #   - LossMargin Likelihood

    # Normalize probabilities across teams
    #   - Combine margins for an expected margin
    #   - Combine Win/Loss margins

    assert league in ['college_football', 'nfl']
    predictor = SportsPredictor(league=league)
    predictor.load()
    team_win = win_probability(predictor, league, variable, feature_set, parameters, team, opponent=False)
    opponent_win = win_probability(predictor, league, variable, feature_set, parameters, opponent, opponent=True)

    return pd.DataFrame.from_records(team_win)

