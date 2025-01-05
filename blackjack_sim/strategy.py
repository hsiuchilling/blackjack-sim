from pathlib import Path

import numpy as np
import pandas as pd

from blackjack_sim.base import (
    ACTION_MAPPING,
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
        self.count_values = np.array([-1, 1, 1, 1, 1, 1, 0, 0, 0, -1, -1, -1, -1])

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
        if self.shoe.is_active():
            true_count_bet_index = int(self.get_true_count())
            if true_count_bet_index < 1:
                return 1
            elif true_count_bet_index >= 6:
                return 6
            else:
                return true_count_bet_index
        else:
            return 1
    
    def get_true_count(self) -> int:
        cards_left_approx = self.shoe.shoe_size - self.shoe.idx + 1 if self.shoe.shoe_size - self.shoe.idx + 1 > 0 else 1
        return np.dot(self.shoe.card_counts, self.count_values) / cards_left_approx * 52

    # def bet_size(self) -> int:
    #     return 1

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
        if self.shoe.is_active() and (action := self.check_i18(hand)):
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
        if self.shoe.is_active():
            true_count_bet_index = int(self.get_true_count())
            if true_count_bet_index < 1:
                return 1
            elif true_count_bet_index >= 6:
                return 6
            else:
                return true_count_bet_index
        else:
            return 1

    def get_true_count(self) -> int:
        cards_left_approx = self.shoe.shoe_size - self.shoe.idx + 1 if self.shoe.shoe_size - self.shoe.idx + 1 > 0 else 1
        return np.dot(self.shoe.card_counts, self.count_values) / cards_left_approx * 52

    def check_i18(self, hand: Hand) -> Action:
        true_count = self.get_true_count()
        if hand.value() == 20 and hand.is_splittable():
            if self.dealer.hand.cards[0].value == 5 and true_count >= 5:
                return Action.SPLIT
            if self.dealer.hand.cards[0].value == 6 and true_count >= 5:
                return Action.SPLIT
        dealer_key = self.dealer.hand.cards[0].value if self.dealer.hand.cards[0].rank != 0 else 1
        key = (str(hand.value()), str(dealer_key))
        if benchmark_entry := self.i18_indices.get(key):
            if true_count < benchmark_entry["index"]:
                return benchmark_entry["under"]
            else:
                return benchmark_entry["over"]
            
    def _init_i18_indices(self) -> dict:
        file = Path(__file__).resolve().parent / "assets" / "i18_strategy.csv"
        strat_df = pd.read_csv(file)
        indices = {}
        for _, row in strat_df.iterrows():
            indices[(str(row.hand_value), str(row.dealer))] = {
                "index": row["index"],
                "over": ACTION_MAPPING[row["decision_over"]],
                "under": ACTION_MAPPING[row["decision_under"]]
            }
        return indices
    
    def insurance(self) -> bool:
        true_count = self.get_true_count()
        return true_count >= 3

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

class ManualStrategy(I18Strategy):
    def __init__(self, dealer, shoe):
        # Strategies are given access to both dealer and shoe
        # Strategies should access only the first card of the dealer's hand
        # Strategies should access only cards in shoe.cards[0:shoe.idx]
        super().__init__(dealer, shoe)
        
        self.dealer = dealer
        self.shoe = shoe
        self.i18_strat = super().action

    def action(self, hand: Hand) -> Action:
        if hand.value == 21:
            return Action.STAY
        
        print("(h)it/(s)tay/(sp)lit/(d)ouble: ", end='')
        action = None
        while True:
            x = input()
            if x == "sp" and hand.is_splittable():
                action = Action.SPLIT
            elif x == "d" and len(hand.cards) == 2:
                action = Action.DHIT
            elif x == "h":
                action = Action.HIT
            elif x == "s":
                action = Action.STAY
            else:
                print("Invalid input.\nHit: h\nStay: s\nDouble: d\nSplit: sp")
            
            if action is not None:
                i18_action = self.i18_strat(hand)
                if i18_action != action:
                    print(f"Book said {i18_action.value}")
                return action

    
    def insurance(self) -> bool:
        while True:
            print("Insurance? (y/n): ", end="")
            x = input()
            if x == "y":
                return True
            elif x == "n":
                return False

    def bet_size(self) -> int:
        while True:
            try:
                print("Bet: ", end='')
                x = input()
                bet = float(x)
                if bet >= 100:
                    print("What a degen 👀...")
                return bet
            except Exception as e:
                print("Numeric bet please...")
            
