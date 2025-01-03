from pathlib import Path

import pandas as pd

from blackjack_sim.base import (
    Action,
    Hand,
)

class DumbassStrategy:
    def __init__(self, dealer, shoe):
        # Strategies are given access to both dealer and shoe
        # Strategies should access only the first card of the dealer's hand
        # Strategies should access only cards in shoe.cards[0:shoe.idx]
        self.dealer = dealer
        self.shoe = shoe

    def action(self, hand: Hand):
        if hand.is_splittable():
            return Action.SPLIT
        elif hand.value() == 11 and len(hand.cards) == 2:
            return Action.DHIT
        elif hand.value() < 17:
            return Action.HIT
        else:
            return Action.STAY

    def bet_size(self) -> int:
        return 1

class StandardStrategy:
    def __init__(self, dealer, shoe):
        self.dealer = dealer
        self.shoe = shoe
        self.strategy_mapping = self._init_strategy()

    def action(self, hand: Hand):
        if self.dealer.hand.cards[0].rank == 0:
            dealer_card_name = "A"
        elif self.dealer.hand.cards[0].rank >= 9:
            dealer_card_name = "10"
        else:
            dealer_card_name = str(self.dealer.hand.cards[0].value)
        
        if hand.is_splittable():
            if action := self.strategy_mapping.get((hand.name(), dealer_card_name)):
                return action
            else:
                hand_name = str(hand.value())
        else:
            hand_name = hand.name()
        return self.strategy_mapping[(hand_name, dealer_card_name)]

    def bet_size(self) -> int:
        return 1

    def _init_strategy(self):
        file = Path(__file__).resolve().parent / "assets" / "standard_strategy.csv"
        strat_df = pd.read_csv(file)
        dealer_card_names = [str(i) for i in range(2, 11)] + ["A"]
        strategy_mapping = {}
        for _, row in strat_df.iterrows():
            for dcn in dealer_card_names:
                if row[dcn] == "H":
                    strategy_mapping[(row.Hand, dcn)] = Action.HIT
                elif row[dcn] == "S":
                    strategy_mapping[(row.Hand, dcn)] = Action.STAY
                elif row[dcn] in ("D", "Ds"):
                    strategy_mapping[(row.Hand, dcn)] = Action.DHIT
                elif row[dcn] == "Y":
                    strategy_mapping[(row.Hand, dcn)] = Action.SPLIT
        return strategy_mapping

        
