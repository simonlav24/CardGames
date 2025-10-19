


from enum import Enum

from utils import Vector2
from core import Card, Vacant, sort_aces_high, Suit, move_cards_and_relink
from engine import RuleSet

from games.durak.player import PlayerBase, PlayerMode
from games.durak.durak_table import DurakTable, GameStage
from games.durak.durak_pot import DurakPot




class GameRoutine(RuleSet):
    def __init__(self):
        super().__init__()
        self.on_drop_return_to_previous_pos = True
        self.move_to_front_on_drag = False
        self.players: list[PlayerBase] = []
        self.current_attacker_index = 0

        self.table: DurakTable = None

        self.burn_vacant: Vacant = None
        self.event = None

    def initialize(self, table: DurakTable, burn_vacant: Vacant) -> None:
        self.table = table
        self.table.stage = GameStage.FIRST_ATTACK
        self.burn_vacant = burn_vacant

    def can_drop_card(self, upper, lower) -> bool:
        attack_card = upper
        defend_card = lower
        if (self.card_belongs_to(defend_card, self.get_defender()) and
            attack_card in self.table.pot and
            self.is_legal_defence(attack_card, defend_card)):
            return True
        return False

    def can_drag_card(self, card: Card) -> bool:
        if self.card_belongs_to(card, self.get_defender()):
            return True
        return False

    def add_player(self, player: PlayerBase) -> None:
        player.player_index = len(self.players)
        self.players.append(player)

    def start(self) -> None:
        self.table.stage = GameStage.FIRST_ATTACK

        main_attacker = self.get_main_attacker()
        main_attacker.toggle_turn()
        main_attacker.mode = PlayerMode.FIRST_ATTACKER
        self.get_defender().mode = PlayerMode.DEFEND
        self.reset_turn(self.get_main_attacker())

    def end_turn(self) -> None:
        # pick up card
        player_list = self.players[self.current_attacker_index:] + self.players[:self.current_attacker_index]
        player_list.remove(self.get_defender())
        player_list.append(self.get_defender())
        for player in player_list:
            card_needed = max(0, 6 - len(player.hand_cards))

            while len(self.table.deck) > 0 and card_needed > 0:
                card = self.table.deck.pop()
                if not card.is_face_up():
                    card.flip()
                player.hand_cards.append(card)
                card_needed -= 1
                if card_needed == 0:
                    break

        self.current_attacker_index = (self.current_attacker_index + 1) % len(self.players)
        self.table.stage = GameStage.FIRST_ATTACK
        self.get_main_attacker().toggle_turn()
        self.reset_turn(self.get_main_attacker())

    def end_turn_skip(self) -> None:
        self.current_attacker_index = (self.current_attacker_index + 1) % len(self.players)
        self.end_turn()
        
    def reset_turn(self, player: PlayerBase) -> None:
        self.event = {'time': 60, 'function': player.start_turn}

    def card_belongs_to(self, card: Card, player: PlayerBase) -> bool:
        if card in player.hand_cards:
            return True
        return False

    def place_attack_card_on_battle(self, card: Card, attacker: PlayerBase) -> None:
        self.table.pot.place_attack(card)
        attacker.hand_cards.remove(card)

    def place_defend_card_on_battle(self, attack_card: Card, defend_card: Card) -> None:
        self.table.pot.place_defend(attack_card, defend_card)
        self.get_defender().hand_cards.remove(defend_card)

    def get_defender(self) -> PlayerBase:
        return self.players[(self.current_attacker_index + 1) % len(self.players)]

    def get_main_attacker(self) -> PlayerBase:
        return self.players[self.current_attacker_index]
    
    def get_player_by_card(self, card: Card) -> PlayerBase:
        for player in self.players:
            if card in player.hand_cards:
                return player
        return None

    def on_placed_card_event(self, placed_Card: Card, placed_upon: Card, last_pos: Vector2, legal_drop: bool) -> None:
        defender = self.get_defender()
        if (not self.card_belongs_to(placed_Card, defender) or 
            placed_upon not in self.table.pot):
            # card does not belong to defender
            return
        if legal_drop:
            self.place_defend_card_on_battle(placed_upon, placed_Card)

    def clicked_on_card(self, card: Card) -> None:
        if self.table.stage == GameStage.FIRST_ATTACK:
            if not self.card_belongs_to(card, self.get_main_attacker()):
                # card does not belong to attacker
                return
            self.place_attack_card_on_battle(card, self.get_main_attacker())
            self.table.stage = GameStage.FREE_PLAY
            self.get_main_attacker().toggle_turn()
            self.reset_turn(self.get_defender())
        
        elif self.table.stage == GameStage.FREE_PLAY:
            current_player = self.get_player_by_card(card)
            if (current_player is not None and
                current_player is not self.get_defender() and
                card.rank in self.table.pot.get_ranks()):
                # any attacker
                attacker = self.get_player_by_card(card)
                self.place_attack_card_on_battle(card, attacker)
        

    def double_click_on_card(self, card: Card) -> None:
        if card.get_top_link() is self.burn_vacant:
            # see if burn is legal
            if self.table.pot.can_burn():
                self.burn_pot()

        if card in self.table.pot:
            self.pick_up_pot()
        
        if self.table.stage == GameStage.FREE_PLAY and self.card_belongs_to(card, self.get_defender()):
            # auto-defend if its obvious
            single_suit_card = self.table.pot.get_card_of_suit(card.suit)
            if single_suit_card is not None and self.is_legal_defence(single_suit_card, card):
                self.place_defend_card_on_battle(single_suit_card, card)
                return
            single_card = self.table.pot.get_if_one()
            if single_card is not None and self.is_legal_defence(single_card, card):
                self.place_defend_card_on_battle(single_card, card)
                return


    def is_legal_defence(self, attack_card: Card, defence_card: Card) -> bool:
        if (attack_card.suit == defence_card.suit and
            sort_aces_high(attack_card.rank) < sort_aces_high(defence_card.rank)):
            return True
        elif (attack_card.suit != defence_card.suit and
            defence_card.suit == self.table.kozer):
            return True
        return False

    def burn_pot(self) -> None:
        '''move all to burn vacant'''
        self.table.pot.clear_links()
        move_cards_and_relink(self.table.pot.get_all_cards(), self.burn_vacant.get_bottom_link())
        self.table.pot.clear_cards()
        self.end_turn()

    def pick_up_pot(self) -> None:
        defender = self.get_defender()
        for card in self.table.pot.get_all_cards(): 
            defender.hand_cards.append(card)
        self.table.pot.clear_links()
        self.table.pot.clear_cards()
        self.end_turn_skip ()

    def step(self) -> None:
        if self.event:
            self.event['time'] -= 1
            if self.event['time'] > 0:
                return

            self.event['function']()
            self.event = None

