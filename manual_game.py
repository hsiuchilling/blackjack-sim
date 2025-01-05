from blackjack_sim import (
    DumbassStrategy,
    Dealer,
    Game,
    ManualStrategy,
    Player,
    Shoe,
)

dealer = Dealer()
shoe = Shoe(n_decks=6)
dumbass_strategy = DumbassStrategy(dealer=dealer, shoe=shoe)
manual_strategy = ManualStrategy(dealer=dealer, shoe=shoe)
players = [
    Player(strategy=manual_strategy),
]
game = Game(
    dealer=dealer,
    shoe=shoe,
    players=players,
    interactive=True
)
game.play()