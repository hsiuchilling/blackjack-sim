import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from blackjack_sim import (
    DumbassStrategy,
    Dealer,
    Game,
    I18Strategy,
    Player,
    Shoe,
    StandardStrategy
)

def iter():
    dealer = Dealer()
    shoe = Shoe(n_decks=6, pen=.85)
    dumbass_strategy = DumbassStrategy(dealer=dealer, shoe=shoe)
    standard_strategy = StandardStrategy(dealer=dealer, shoe=shoe)
    i18_strategy = I18Strategy(dealer=dealer, shoe=shoe)
    players = [
        Player(strategy=dumbass_strategy),
        Player(strategy=standard_strategy),
        Player(strategy=i18_strategy),
    ]
    game = Game(
        dealer=dealer,
        shoe=shoe,
        players=players
    )
    game.play()
    return np.array([p.balance for p in players])

nsims = 5000
print(np.array([iter() for _ in range(nsims)]).mean(axis = 0))