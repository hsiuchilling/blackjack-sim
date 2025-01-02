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

print("==============")
print("Final Balances")
print("==============")
print(f"Player 1: {players[0].balance}")
print(f"Player 2: {players[1].balance}")
print(f"Player 3: {players[2].balance}")