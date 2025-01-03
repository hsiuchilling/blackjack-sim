from blackjack_sim import (
    DumbassStrategy,
    Dealer,
    Game,
    Player,
    Shoe,
)

# In this setup, only 5 out of the six decks are ever played. In 
# both cases, it is the same idiot playing without a counting 
# strategy. So, the second idiot is fortunate to start playing 
# one deck in. In expectation, he should lose ~20% less on average
# when he arrives late.

def iter_full():
    dealer = Dealer()
    shoe = Shoe(n_decks=6, pen=.85)
    dumbass_strategy = DumbassStrategy(dealer=dealer, shoe=shoe)
    players = [
        Player(strategy=dumbass_strategy),
    ]
    game = Game(
        dealer=dealer,
        shoe=shoe,
        players=players
    )
    game.play()
    return players[0].balance

def iter_part():
    # Same set up 
    dealer = Dealer()
    shoe = Shoe(idx=52, n_decks=6, pen=.85)
    dumbass_strategy = DumbassStrategy(dealer=dealer, shoe=shoe)
    players = [
        Player(strategy=dumbass_strategy),
    ]
    game = Game(
        dealer=dealer,
        shoe=shoe,
        players=players
    )
    game.play()
    return players[0].balance

nsims = 3000
full_outcomes = [iter_full() for _ in range(nsims)]
part_outcomes = [iter_part() for _ in range(nsims)]

print(sum(part_outcomes) / sum(full_outcomes))