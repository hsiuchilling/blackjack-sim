from blackjack_sim import (
    DumbassStrategy,
    Dealer,
    Game,
    Player,
    Shoe,
    StandardStrategy
)

dealer = Dealer()
shoe = Shoe(n_decks=10, pen=.85)
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

print(game.player_balances)