from blackjack_sim.base import (
    Action,
    Hand,
)

class Dealer:
    def __init__(self):
        self.hand: Hand | None = None
        self.strategy = DealerStrategy()
    
    def action(self) -> str:
        return self.strategy.action(self.hand)

class Player:
    def __init__(self, strategy):
        self.hands: list[Hand] = []
        self.strategy = strategy
        self.balance: float = 0

    def action(self, hand) -> Action:
        return self.strategy.action(hand)

    def bet(self, bet_size=None) -> int:
        # Bet for a round. This should not be re-called within a round because
        # strategy may change based on observed cards and all valid same-round bets
        # must be sized the same as the original.
        if bet_size is None:
            bet_size = self.strategy.bet_size()
        self.balance -= bet_size
        return bet_size

class DealerStrategy:
    def action(self, hand):
        if hand.value() >= 17 and not (len(hand.cards) == 2 and hand._soft_aces):
            return Action.STAY
        else:
            return Action.HIT