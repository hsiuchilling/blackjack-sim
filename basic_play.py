from blackjack_sim.src import (
    DumbassStrategy,
    Dealer,
    Game,
    Player,
    Shoe,
)

dealer = Dealer()
shoe = Shoe(n_decks=6)
dumbass_strategy = DumbassStrategy(dealer=dealer, shoe=shoe)
players = [
    Player(strategy=dumbass_strategy),
    Player(strategy=dumbass_strategy),
    Player(strategy=dumbass_strategy)
]
game = Game(
    dealer=dealer,
    shoe=shoe,
    players=players
)
game.play()

print(players[0].balance)
print(players[1].balance)
print(players[2].balance)