from time import sleep

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
    def __init__(self, dealer: Dealer, shoe: Shoe, players: list[Player], interactive: bool=False):
        self.dealer: Dealer = dealer
        self.players: list[Player] = players
        self.n_players: int = len(players)
        self.shoe: Shoe = shoe
        self.round: int = 0
        self.interactive: bool = interactive
        
        # 2.7 is average number of cards per blackjack hand
        round_estimate: int = estimate_rounds(shoe=shoe, n_players=self.n_players)
        self.player_balances = np.empty((self.n_players, round_estimate))
        self.player_balances[:] = np.nan
    
    def play(self):
        # TODO: confirm simulation end condition
        while self.shoe.is_active():
            self.player_balances[:,self.round] = [p.balance for p in self.players]
            if self.interactive:
                print("====================")
                print(f"Round: {self.round} | PNL: {self.players[0].balance}")
                print("====================")
            self.play_round()
            self.round += 1
        self.player_balances[:,self.round] = [p.balance for p in self.players]

    def play_round(self):
        # initial deal
        self.dealer.hand = Hand()
        self.dealer.hand.hit(self.shoe.deal())
        self.dealer.hand.hit(self.shoe.deal(reserve_count=True))
        
        for player in self.players:
            player.hands = [Hand(bet=player.bet())]
            player.hands[0].hit(self.shoe.deal())
            player.hands[0].hit(self.shoe.deal())
        
        if self.interactive:
            print(f"Dealer: {str(self.dealer.hand.cards[0])}")

        if self.dealer.hand.cards[0].rank == 0:
            for player in self.players:
                if self.interactive:
                    print(self.players[0].hands[0])
                if player.insurance():
                    if self.dealer.hand.is_blackjack():
                        player.balance += player.hands[0].bet / 2
                    else:
                        player.balance -= player.hands[0].bet / 2

        # anyone home?
        if self.dealer.hand.value() == 21:
            if self.interactive:
                print("Sorry! Someone's home")
                print(f"Dealer: {self.dealer.hand.format()}")
                print(f"Hand: {self.players[0].hands[0].format()}")
            
            for player in self.players:
                if player.hands[0].value() == 21:
                    player.balance += player.hands[0].bet
            self.shoe.reveal_reserved_card()
            return
        
        # update player hands
        for idx, player in enumerate(self.players):
            handle_player(player, self.shoe, interactive=self.interactive and idx == 0)
        
        # resolve game
        handle_dealer(self.dealer, self.shoe)
        if self.interactive:
            print(f"Dealer: {', '.join([str(c) for c in self.dealer.hand.cards])}")
        
        first_player_results = []
        if self.dealer.hand.value() == -1:
            for idx, player in enumerate(self.players):
                for hand in player.hands:
                    if hand.is_blackjack():
                        player.balance += 2.5 * hand.bet
                        if idx == 0:
                            first_player_results.append("Win!")
                    elif hand.value() != -1:
                        player.balance += 2 * hand.bet
                        if idx == 0:
                            first_player_results.append("Win!")
                    else:
                        if idx == 0:
                            first_player_results.append("Loss")
        else:
            for idx, player in enumerate(self.players):
                for hand in player.hands:
                    if hand.value() > self.dealer.hand.value():
                        if hand.is_blackjack():
                            player.balance += 2.5 * hand.bet
                            if idx == 0:
                                first_player_results.append("Win")
                        else:
                            player.balance += 2 * hand.bet
                            if idx == 0:
                                first_player_results.append("Win")
                    elif hand.value() == self.dealer.hand.value():
                        player.balance += hand.bet
                        if idx == 0:
                            first_player_results.append("Push")
                    else:
                        if idx == 0:
                            first_player_results.append("Loss")
        
        if self.interactive:
            print(first_player_results)
            sleep(1)

def handle_dealer(dealer: Dealer, shoe: Shoe):
    shoe.reveal_reserved_card()
    while dealer.hand.value() != -1:
        action = dealer.action()
        if action == Action.HIT:
            dealer.hand.hit(shoe.deal())
        elif action == Action.STAY:
            break
        else:
            raise RuntimeError(f"Invalid dealer action: {str(action)}")

def handle_player(player: Player, shoe: Shoe, interactive=False):
    hands_to_handle = [player.hands[0]]
    while hands_to_handle:
        hand = hands_to_handle.pop()
        while hand.value() not in (-1, 21):
            if interactive:
                print(f"Hand: {hand.format()}")
            action = player.action(hand)
            if action == Action.HIT:
                hand.hit(shoe.deal())
            elif action == Action.STAY:
                break
            elif action == Action.DHIT:
                player.balance -= hand.bet
                hand.bet *= 2
                hand.hit(shoe.deal())
                if interactive:
                    print(f"Hand: {hand.format()}")
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
        
        if interactive and hand.value() == -1:
            print("Bust!")
            print(f"Hand: {hand.format()}")
        if interactive and hand.value() == 21:
            print(f"Hand: {hand.format()}")
            print("Blackjack!")
        