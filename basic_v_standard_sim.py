import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from blackjack_sim import (
    DumbassStrategy,
    Dealer,
    Game,
    Player,
    Shoe,
    StandardStrategy
)

def iter():
    dealer = Dealer()
    shoe = Shoe(n_decks=6, pen=.85)
    dumbass_strategy = DumbassStrategy(dealer=dealer, shoe=shoe)
    standard_strategy = StandardStrategy(dealer=dealer, shoe=shoe)
    players = [
        Player(strategy=dumbass_strategy),
        Player(strategy=standard_strategy)
    ]
    game = Game(
        dealer=dealer,
        shoe=shoe,
        players=players
    )
    game.play()
    return game.player_balances

nsims = 100
outcomes = np.array([iter() for _ in range(nsims)])

df = pd.DataFrame({
    'time': np.tile(np.arange(outcomes.shape[2]), outcomes.shape[0]),
    'series': np.repeat(np.arange(outcomes.shape[0]), outcomes.shape[2]),
    'value': outcomes[:,1,:].ravel()
})
# print(df)
sns.lineplot(x='time', y='value', hue='series', data=df)
plt.show()