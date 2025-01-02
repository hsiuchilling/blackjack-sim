from enum import Enum
from pydantic import BaseModel
import random

class Action(Enum):
    SPLIT="split"
    HIT="hit"
    DHIT="dhit"
    STAY="stay"
    # TODO: implement surrender
    # TODO: implement so that ace splits can only be hit once

class Card(BaseModel):
    rank: int
    value: int

class Shoe:
    def __init__(self, n_decks: int = 6, idx: int = 0, pen: float = .9):
        self.n_decks = n_decks
        self.shoe_size = n_decks * 52
        self._init_cards()
        self.idx = idx
        self.pen_idx = int(self.shoe_size * pen)
    
    def _init_cards(self):
        self.cards = []
        for _ in range(self.n_decks):
            for _ in range(4):
                for i in range(13):
                    if i == 0:
                        self.cards.append(Card(rank=i, value=11))
                    elif i >= 9:
                        self.cards.append(Card(rank=i, value=10))
                    else:
                        self.cards.append(Card(rank=i, value=i+1))
        random.shuffle(self.cards)
    
    def deal(self) -> Card:
        card = self.cards[self.idx]
        self.idx += 1
        return card

    def is_active(self) -> bool:
        return self.idx < self.pen_idx

class Hand:
    def __init__(self, bet=None):
        self.cards = []
        self._soft_aces = []
        self.bet = bet
    
    @property
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
    
    def is_splittable(self) -> bool:
        # TODO: implement so that aces can only be split once
        return len(self.cards) == 2 and self.cards[0].value == self.cards[1].value

    def is_blackjack(self) -> bool:
        return len(self.cards) == 2 and self.value == 21

    def hit(self, card: Card):
        self.cards.append(card)
        if card.rank == 1:
            self._soft_aces.append(card)

    def __str__(self):
        return f"Cards: {str(self.cards)}\nValue: {self.value}"

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

    def bet(self) -> int:
        bet_size = self.strategy.bet_size()
        self.balance -= bet_size
        return bet_size

class Game:
    def __init__(self, dealer: Dealer, shoe: Shoe, players: list[Player]):
        self.dealer: Dealer = dealer
        self.players: list[Player] = players
        self.shoe: Shoe = shoe
    
    def play(self):
        # TODO: confirm simulation end condition
        while self.shoe.is_active():
            self.play_round()

    def play_round(self):
        # initial deal
        self.dealer.hand = Hand()
        self.dealer.hand.hit(self.shoe.deal())
        self.dealer.hand.hit(self.shoe.deal())
        
        for player in self.players:
            player.hands = [Hand(bet=player.bet())]
            player.hands[0].hit(self.shoe.deal())
            player.hands[0].hit(self.shoe.deal())
        
        # TODO: implement insurance
        
        # anyone home?
        if self.dealer.hand.value == 21:
            for player in self.players:
                if player.hands[0].value == 21:
                    player.balance += player.hands[0].bet
        
        # update player hands
        for player in self.players:
            handle_player(player, self.shoe)
        
        # resolve game
        handle_dealer(self.dealer, self.shoe)
        if self.dealer.hand.value == -1:
            for player in self.players:
                for hand in player.hands:
                    if hand.is_blackjack():
                        player.balance += 2.5 * hand.bet
                    elif hand.value != -1:
                        player.balance += 2 * hand.bet
        else:
            for player in self.players:
                for hand in player.hands:
                    if hand.value > self.dealer.hand.value:
                        if hand.is_blackjack():
                            player.balance += 2.5 * hand.bet
                        else:
                            player.balance += 2 * hand.bet
                    elif hand.value == self.dealer.hand.value:
                        player.balance += hand.bet
        


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
        elif hand.value == 11 and len(hand.cards) == 2:
            return Action.DHIT
        elif hand.value < 17:
            return Action.HIT
        else:
            return Action.STAY

    def bet_size(self) -> int:
        return 1
        

class DealerStrategy:
    def action(self, hand):
        if hand.value >= 17 and not (len(hand.cards) == 2 and hand._soft_aces):
            return Action.STAY
        else:
            return Action.HIT

def handle_dealer(dealer: Dealer, shoe: Shoe):
    while dealer.hand.value != -1:
        action = dealer.action()
        if action == Action.HIT:
            dealer.hand.hit(shoe.deal())
        elif action == Action.STAY:
            break
        else:
            raise RuntimeError(f"Invalid dealer action: {str(action)}")

def handle_player(player: Player, shoe: Shoe):
    hands_to_handle = [player.hands[0]]
    while hands_to_handle:
        hand = hands_to_handle.pop()
        while hand.value != -1:
            action = player.action(hand)
            if action == Action.HIT:
                hand.hit(shoe.deal())
            elif action == Action.STAY:
                break
            elif action == Action.DHIT:
                player.balance -= hand.bet
                hand.bet *= 2
                hand.hit(shoe.deal())
                break
            elif action == Action.SPLIT:
                player.balance -= hand.bet
                new_hand = Hand(bet=hand.bet)
                new_hand.hit(hand.cards.pop())
                player.hands.append(new_hand)
                hands_to_handle.append(new_hand)
            else:
                raise RuntimeError(f"Invalid player action: {str(action)}")