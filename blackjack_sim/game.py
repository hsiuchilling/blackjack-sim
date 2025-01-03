import numpy as np

from blackjack_sim.base import (
    Action,
    Hand,
    Shoe,
)
from blackjack_sim.players import (
    Dealer,
    Player
)
from blackjack_sim.utils import estimate_rounds

class Game:
    def __init__(self, dealer: Dealer, shoe: Shoe, players: list[Player]):
        self.dealer: Dealer = dealer
        self.players: list[Player] = players
        self.n_players: int = len(players)
        self.shoe: Shoe = shoe
        self.round: int = 0
        
        # 2.7 is average number of cards per blackjack hand
        round_estimate: int = estimate_rounds(shoe=shoe, n_players=self.n_players)
        self.player_balances = np.empty((self.n_players, round_estimate))
        self.player_balances[:] = np.nan
    
    def play(self):
        # TODO: confirm simulation end condition
        while self.shoe.is_active():
            self.player_balances[:,self.round] = [p.balance for p in self.players]
            self.play_round()
            self.round += 1
        self.player_balances[:,self.round] = [p.balance for p in self.players]

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
        if self.dealer.hand.value() == 21:
            for player in self.players:
                if player.hands[0].value() == 21:
                    player.balance += player.hands[0].bet
            return
        
        # update player hands
        for player in self.players:
            handle_player(player, self.shoe)
        
        # resolve game
        handle_dealer(self.dealer, self.shoe)
        if self.dealer.hand.value() == -1:
            for player in self.players:
                for hand in player.hands:
                    if hand.is_blackjack():
                        player.balance += 2.5 * hand.bet
                    elif hand.value() != -1:
                        player.balance += 2 * hand.bet
        else:
            for player in self.players:
                for hand in player.hands:
                    if hand.value() > self.dealer.hand.value():
                        if hand.is_blackjack():
                            player.balance += 2.5 * hand.bet
                        else:
                            player.balance += 2 * hand.bet
                    elif hand.value() == self.dealer.hand.value():
                        player.balance += hand.bet

def handle_dealer(dealer: Dealer, shoe: Shoe):
    while dealer.hand.value() != -1:
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
        while hand.value() != -1:
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
                new_hand.hit(shoe.deal())
                new_hand.reset_aces()
                hand.hit(shoe.deal())
                hand.reset_aces()
                player.hands.append(new_hand)
                hands_to_handle.append(new_hand)
            else:
                raise RuntimeError(f"Invalid player action: {str(action)}")