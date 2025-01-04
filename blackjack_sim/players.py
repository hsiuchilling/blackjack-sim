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
        # Bet for a round.
        if bet_size is None:
            bet_size = self.strategy.bet_size()
        self.balance -= bet_size
        return bet_size
    
    def insurance(self) -> bool:
        if hasattr(self.strategy, "insurance"):
            return self.strategy.insurance()
        else:
            return False

class DealerStrategy:
    def action(self, hand) -> Action:
        if hand.value() >= 17 and not (len(hand.cards) == 2 and hand._soft_aces):
            return Action.STAY
        else:
            return Action.HIT