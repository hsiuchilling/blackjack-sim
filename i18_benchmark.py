from collections import Counter
from copy import deepcopy
import numpy as np

from blackjack_sim import (
    DumbassStrategy,
    Dealer,
    Game,
    I18Strategy,
    Player,
    Shoe,
    StandardStrategy
)

def run_strat(strat_class, shoe):
    dealer = Dealer()
    strat = strat_class(dealer=dealer, shoe=shoe)
    players = [
        Player(strategy=strat)
    ]
    game = Game(
        dealer=dealer,
        shoe=shoe,
        players=players
    )
    game.play()
    return players[0].balance

def iter():
    shoe = Shoe(n_decks=6, pen=.85)
    balances = []
    balances.append(run_strat(DumbassStrategy, deepcopy(shoe)))
    balances.append(run_strat(StandardStrategy, deepcopy(shoe)))
    balances.append(run_strat(I18Strategy, deepcopy(shoe)))
    return np.array(balances)

nsims = 2000
print(np.array([iter() for _ in range(nsims)]).mean(axis = 0))