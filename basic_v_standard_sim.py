from blackjack_sim import (
    DumbassStrategy,
    Dealer,
    Game,
    Player,
    Shoe,
    StandardStrategy
)

# In this setup, only 5 out of the six decks are ever played. In 
# both cases, it is the same idiot playing without a counting 
# strategy. So, the second idiot is fortunate to start playing 
# one deck in. In expectation, he should lose ~20% less on average
# when he arrives late.

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
    return players[0].balance, players[1].balance

nsims = 2000
outcomes = [iter() for _ in range(nsims)]

player_1_avg = sum([i[0] for i in outcomes]) / nsims
player_2_avg = sum([i[1] for i in outcomes]) / nsims

print(f"Dumb Player Avg: {player_1_avg}")
print(f"Standard Player Avg: {player_2_avg}")