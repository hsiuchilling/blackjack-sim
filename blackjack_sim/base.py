from collections import Counter
from enum import Enum
import random

import numpy as np

class Action(Enum):
    SPLIT="split"
    HIT="hit"
    DHIT="dhit"
    STAY="stay"
    # TODO: implement surrender
    # TODO: implement so that ace splits can only be hit once

class Card:
    def __init__(self, rank: int, value: int):     
        self.rank: int = rank
        self.value: int = value
        
        if rank == 0:
            self.name = "A"
        elif rank >= 9:
            self.name = "T"
        else:
            self.name = f"{rank + 1}"
     
    def __str__(self):
        if self.rank == 0:
            return "A"
        elif self.rank == 10:
            return "J"
        elif self.rank == 11:
            return "Q"
        elif self.rank == 12:
            return "K"
        else:
            return str(self.rank + 1)
        

class Shoe:
    def __init__(self, n_decks: int = 6, idx: int = 0, pen: float = .9):
        self.n_decks = n_decks
        self.shoe_size = n_decks * 52
        self.cards = self._init_cards()
        self.idx = idx
        self.pen_idx = int(self.shoe_size * pen)
        self.backup_cards = self._init_cards()
        self.card_counts: np.array = self._init_card_counts()
    
    def _init_cards(self) -> list[Card]:
        cards = []
        for _ in range(self.n_decks):
            for _ in range(4):
                for i in range(13):
                    if i == 0:
                        # Aces are initialized as soft aces
                        cards.append(Card(rank=i, value=11))
                    elif i >= 9:
                        cards.append(Card(rank=i, value=10))
                    else:
                        cards.append(Card(rank=i, value=i+1))
        random.shuffle(cards)
        return cards

    def _init_card_counts(self) -> np.array:
        card_counts = np.zeros(13)
        if self.idx > 0:
            for rank, deals in Counter(self.cards[:self.idx]).items():
                card_counts[rank] += deals
        return card_counts
    
    def deal(self) -> Card:
        # temporary backstop for midround shoe depletion
        if self.idx >= len(self.cards):
            return self.backup_cards.pop()
        
        card = self.cards[self.idx]
        self.card_counts[card.rank] += 1
        self.idx += 1
        return card

    def is_active(self) -> bool:
        return self.idx < self.pen_idx

class Hand:
    def __init__(self, bet=None):
        self.cards: list[Card] = []
        self._soft_aces: list[Card] = []
        self.bet: float = bet
    
    def value(self) -> int:
        candidate_value = sum([c.value for c in self.cards])
        if candidate_value <= 21:
            return candidate_value
        elif candidate_value > 21 and not self._soft_aces:
            return -1
        else:
            while self._soft_aces:
                soft_ace = self._soft_aces.pop()
                soft_ace.value = 1
                candidate_value -= 10
                if candidate_value <= 21:
                    return candidate_value
            return -1
    
    def reset_aces(self):
        self._soft_aces = []
        for c in self.cards:
            if c.rank == 0:
                c.value = 11
                self._soft_aces.append(c)
    
    def name(self) -> str:
        if self.is_splittable():
            return f"{self.cards[0].name},{self.cards[0].name}"
        
        current_value = self.value()
        if self._soft_aces:
            if current_value < 12:
                print(self)
            second_term = str(current_value - 11) if current_value != 12 else "A"
            
            return f"A,{second_term}"
        
        return f"{current_value}"
    
    def is_splittable(self) -> bool:
        # TODO: implement so that aces can only be split once
        return len(self.cards) == 2 and self.cards[0].value == self.cards[1].value

    def is_blackjack(self) -> bool:
        return len(self.cards) == 2 and self.value() == 21

    def hit(self, card: Card):
        self.cards.append(card)
        if card.rank == 0:
            self._soft_aces.append(card)

    def __str__(self):
        return f"Cards: {[str(i) for i in self.cards]}\nValue: {self.value()}"