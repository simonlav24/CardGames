


from enum import Enum

from core import Card, Vacant, Rank, rank_translate_ace_high, Suit
from engine import post_event, DelayedSetPosEvent

from games.durak.player import PlayerBase
from games.durak.durak_pot import DurakPot

class GameStage(Enum):
    NONE = 0
    FIRST_ATTACK = 1
    FREE_PLAY = 2

class GameRoutine:
    def __init__(self):
        self.players: list[PlayerBase] = []
        self.current_attacker_index = 0

        self.deck: list[Card] = None
        self.pot: DurakPot = None
        self.burn_vacant: Vacant = None
        self.rank_translate = rank_translate_ace_high
        self.kozer: Suit
        self.game_mode = GameStage.FIRST_ATTACK

        self.event = None

    def initialize(self, deck: list[Card], pot: DurakPot, burn_vacant: Vacant, kozer: Suit) -> None:
        self.deck = deck
        self.pot = pot
        self.burn_vacant = burn_vacant
        self.kozer = kozer

    def add_player(self, player: PlayerBase) -> None:
        self.players.append(player)

    def start(self) -> None:
        self.players[self.current_attacker_index].attack()
        self.game_mode = GameStage.FIRST_ATTACK

    def end_turn(self) -> None:
        ...
        
    def reset_turn(self) -> None:
        ...
        # current_player = self.players[self.current_player_index]
        # self.event = {'time': 60, 'function': current_player.start_turn}         

    def card_belongs_to(self, card: Card, player: PlayerBase) -> bool:
        if card in player.hand_cards:
            return True
        return False

    def place_attack_card_on_battle(self, card: Card) -> None:
        self.pot.place_attack(card)
        self.get_attacker().hand_cards.remove(card)

    def place_defend_card_on_battle(self, attack_card: Card, defend_card: Card) -> None:
        self.pot.place_defend(attack_card, defend_card)
        self.get_defender().hand_cards.remove(defend_card)

    def get_defender(self) -> PlayerBase:
        return self.players[(self.current_attacker_index + 1) % len(self.players)]

    def get_attacker(self) -> PlayerBase:
        return self.players[self.current_attacker_index]

    def clicked_on_card(self, card: Card) -> None:
        if self.game_mode == GameStage.FIRST_ATTACK:
            if not self.card_belongs_to(card, self.get_attacker()):
                # card does not belong to attacker
                return
            self.place_attack_card_on_battle(card)
            self.game_mode = GameStage.FREE_PLAY
        
        elif self.game_mode == GameStage.FREE_PLAY:
            # if card is of defender
            defender = self.get_defender()
            if self.card_belongs_to(card, defender):
                defender.hand_cards.toggle_select(card)

            # if card is in pot
            if card in self.pot and self.pot.is_clear_for_defence(card):
                selected_card = defender.hand_cards.get_selected()
                if len(selected_card) == 0:
                    return
                defend_card = selected_card[0]
                if self.is_legal_defence(card, defend_card):
                    self.place_defend_card_on_battle(card, defend_card)

    def is_legal_defence(self, attack_card: Card, defence_card: Card) -> bool:
        if (attack_card.suit == defence_card.suit and
            self.rank_translate(attack_card.rank) < self.rank_translate(defence_card.rank)):
            return True
        elif (attack_card.suit != defence_card.suit and
            defence_card.suit == self.kozer):
            return True
        return False

    def burn_pile(self) -> None:
        last_card = self.burn_vacant.get_bottom_link()
        pos = last_card.get_pos()
        self.pile.vacant.break_lower_link()
        for i, card in enumerate(self.pile):
            last_card.link_card(card)
            post_event(DelayedSetPosEvent(card, pos + i * self.burn_vacant.link_offset, delay=30 + i))
            last_card = card
        
        self.pile.clear()

    def pick_up_pot(self) -> None:
        player = self.players[self.current_player_index]
        for card in self.pile:
            card.break_lower_link()
            card.break_upper_link()
            player.deal(card)
        self.pile.clear()
        
        self.end_turn()

    def step(self) -> None:
        for player in self.players:
            player.step()
        if self.event:
            self.event['time'] -= 1
            if self.event['time'] > 0:
                return

            is_done = self.event['function']()
            if is_done:
                self.event = None
            else:
                self.reset_turn()

