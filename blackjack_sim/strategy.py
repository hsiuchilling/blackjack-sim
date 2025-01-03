from pathlib import Path

import numpy as np
import pandas as pd

from blackjack_sim.base import (
    Action,
    Hand,
    Shoe
)

class DumbassStrategy:
    def __init__(self, dealer, shoe):
        # Strategies are given access to both dealer and shoe
        # Strategies should access only the first card of the dealer's hand
        # Strategies should access only cards in shoe.cards[0:shoe.idx]
        self.dealer = dealer
        self.shoe = shoe

    def action(self, hand: Hand) -> Action:
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

    def action(self, hand: Hand) -> Action:
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

    def _init_strategy(self) -> dict:
        # TODO: standardize strategy mapping hand nomenclature
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


class I18Strategy:
    def __init__(self, dealer, shoe):
        self.dealer = dealer
        self.shoe: Shoe = shoe
        self.standard_strategy = self._init_standard_strategy()
        self.count_values = np.array([-1, 1, 1, 1, 1, 1, 0, 0, 0, -1, -1, -1, -1])
        self.i18_indices = self._init_i18_indices()

    def action(self, hand: Hand) -> Action:
        if action := self.check_i18(hand):
            return action
        
        if self.dealer.hand.cards[0].rank == 0:
            dealer_card_name = "A"
        elif self.dealer.hand.cards[0].rank >= 9:
            dealer_card_name = "10"
        else:
            dealer_card_name = str(self.dealer.hand.cards[0].value)
        
        if hand.is_splittable():
            if action := self.standard_strategy.get((hand.name(), dealer_card_name)):
                return action
            else:
                hand_name = str(hand.value())
        else:
            hand_name = hand.name()
        return self.standard_strategy[(hand_name, dealer_card_name)]

    def bet_size(self) -> int:
        return 1

    def get_true_count(self) -> int:
        cards_left_approx = self.shoe.shoe_size - self.shoe.idx + 1 if self.shoe.shoe_size - self.shoe.idx + 1 > 0 else 1
        return np.dot(self.shoe.card_counts, self.count_values) / cards_left_approx * 52

    def check_i18(self, hand: Hand) -> Action:
        true_count = self.get_true_count()
        if hand.value == 20 and hand.is_splittable():
            if self.dealer.hand.cards[0].value == 5 and true_count >= 5:
                return Action.SPLIT
            if self.dealer.hand.cards[0].value == 6 and true_count >= 4:
                return Action.SPLIT
        dealer_key = self.dealer.hand.cards[0].value if self.dealer.hand.cards[0].rank != 0 else 1
        key = (str(hand.value()), str(dealer_key))
        if benchmark_idx := self.i18_indices.get(key):
            if true_count < benchmark_idx:
                return Action.HIT
            # if hand.is_splittable():
            #     return Action.SPLIT
            # # TODO: is this right?
            # if len(hand.cards) == 2:
            #     return Action.DHIT
            return Action.STAY
            
    def _init_i18_indices(self) -> dict:
        file = Path(__file__).resolve().parent / "assets" / "i18_strategy.csv"
        strat_df = pd.read_csv(file)
        indices = {}
        for _, row in strat_df.iterrows():
            indices[(str(row.hand_value), str(row.dealer))] = row["index"]
        return indices

    def _init_standard_strategy(self) -> dict:
        # TODO: standardize strategy mapping hand nomenclature
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

        
