

from utils import Vector2

from game_globals import win_width, win_height
from game_base import GameBase
from custom_random import shuffle
from card import Card, Vacant, Rank, Suit, create_deck, CARD_SIZE
from rules import RuleSet
from events import post_event, Event, EventType, AnimationEvent, MoveToTopEvent
from card_utilities import animate_and_relink
from hand_cards import HandCards
from pile import Pile


class ShitheadRuleSet(RuleSet):
    def can_link_cards(self, upper: Card, lower: Card) -> bool:
        return False

    def on_place_card(self, card: Card, previous_parent: Card | None):
        ...

    def can_drag_card(self, card: Card) -> bool:
        return False


class GameRoutine:
    def __init__(self):
        self.num_of_players = 2
        self.players_hands: list[HandCards] = []
        self.current_player_index = 0

        self.deck: list[Card] = None
        self.pile: Pile = None
        self.burn_vacant: Vacant = None

    def end_turn(self) -> None:
        self.current_player_index = (self.current_player_index + 1) % self.num_of_players

    def can_play_card(self, card: Card) -> bool:
        # can always play special cards
        if self.is_card_special(card):
            return True

        effective_rank = self.get_pile_top_effective_rank()

        match effective_rank:
            case Rank.NONE | Rank.TWO | Rank.THREE:
                return True
            
            case Rank.SEVEN:
                if card.rank.value <= Rank.SEVEN.value:
                    return True
                else:
                    return False

        if card.rank.value >= effective_rank.value:
            return True
        return False
            

    def is_card_special(self, card: Card) -> bool:
        return card.rank in [Rank.TWO, Rank.THREE, Rank.TEN]

    def clicked_on_card(self, card: Card) -> None:
        if not card in self.players_hands[self.current_player_index]:
            return
        
        if self.can_play_card(card):
            self.play_card(card)

    def get_pile_top_effective_rank(self) -> Rank:
        pile_top = self.pile.get_top()
        while pile_top.rank == Rank.THREE:
            pile_top = pile_top.get_prev()
        return pile_top.rank

    def play_card(self, card: Card) -> None:
        ''' play the card into the pile '''
        print(f'play card {card}')
        advance_turn = True
        pile_top = self.pile.get_top()
        hands = self.players_hands[self.current_player_index]

        # move card to pile
        hands.remove(card)
        self.pile.append(card)
        post_event(AnimationEvent(card, card.pos, pile_top.pos + pile_top.link_offset))

        # complete to hand
        while len(hands) < 3:
            drawn_card = self.deck.pop(0)
            drawn_card.flip()
            hands.append(drawn_card)

        # check for effects
        match card.rank:
            case Rank.TEN:
                self.burn_pile()
                advance_turn = False

            case Rank.THREE:
                effective_rank = self.get_pile_top_effective_rank()
                if effective_rank == Rank.EIGHT:
                    advance_turn = False

            case Rank.EIGHT:
                advance_turn = False

        # advance turn
        if advance_turn:
            self.end_turn()

        print(f'player {self.current_player_index + 1} turn')

    def burn_pile(self) -> None:
        last_card = self.burn_vacant.get_bottom_link()
        pos = last_card.get_pos()
        self.pile.vacant.break_lower_link()
        for i, card in enumerate(self.pile):
            last_card.link_card(card)
            post_event(AnimationEvent(card, card.pos, pos + i * self.burn_vacant.link_offset, delay=30 + i))
            last_card = card
        
        self.pile.clear()

    def pick_up_pile(self) -> None:
        hands = self.players_hands[self.current_player_index]
        for card in self.pile:
            card.break_lower_link()
            card.break_upper_link()
            hands.append(card)
        self.pile.clear()



class ShitheadGame(GameBase):
    def __init__(self):
        super().__init__()
        self.rules = ShitheadRuleSet()
        self.card_manipulator.set_rules(self.rules)

        self.deck: list[Card] = []
        self.pile = Pile()
        self.burn_vacant = Vacant()

        self.player_one_cards = HandCards()
        self.player_two_cards = HandCards()

        # TODO: refactor these
        self.game_routine = GameRoutine()
        self.game_routine.players_hands.append(self.player_one_cards)
        self.game_routine.players_hands.append(self.player_two_cards)
        self.game_routine.pile = self.pile
        self.game_routine.deck = self.deck
        self.game_routine.burn_vacant = self.burn_vacant

    def handle_event(self, event):
        super().handle_event(event)

        if event.type == EventType.CLICK_CARD:
            self.game_routine.clicked_on_card(event.card)

        if event.type == EventType.DOUBLE_CLICK_CARD:
            card = event.card
            if card in self.pile:
                self.game_routine.pick_up_pile()

    def step(self):
        super().step()
        self.player_one_cards.step()
        self.player_two_cards.step()

    def setup_game(self) -> list[Card]:
        cards = create_deck()
        shuffle(cards)
        self.deck += cards.copy()

        vacants: list[Vacant] = []
        margin = 10

        pile_pos = Vector2(win_width - CARD_SIZE[0], win_height - CARD_SIZE[1]) // 2
        self.pile.set_pos(pile_pos)
        self.pile.vacant.set_link_offset(Vector2(2,2))
        vacants.append(self.pile.vacant)
        deck_pos = pile_pos - Vector2(margin + CARD_SIZE[0], 0)

        burned_pos = pile_pos + Vector2(margin + CARD_SIZE[0], 0)
        self.burn_vacant.set_pos(burned_pos)
        self.burn_vacant.set_link_offset(Vector2(2,2))
        vacants.append(self.burn_vacant)

        for card in cards:
            card.set_pos(deck_pos.copy())
        
        # currently for two players
        player_width = CARD_SIZE[0] * 3 + margin * 2

        # player one
        player_pos = Vector2(win_width // 2 - player_width // 2, win_height - margin - CARD_SIZE[1] - margin * 4)
        for i in range(3):
            pos = player_pos + Vector2(margin + CARD_SIZE[0], 0) * i
            vacant = Vacant(pos)
            vacants.append(vacant)
            
            lucky_flipped = self.deck.pop(0)
            lucky_flipped.set_pos(pos + vacant.link_offset)
            vacant.link_card(lucky_flipped)

            lucky_faced = self.deck.pop(0)
            lucky_faced.flip()
            lucky_faced.set_pos(pos + lucky_flipped.link_offset * 2)
            lucky_flipped.link_card(lucky_faced)

            # hand cards
            pos = Vector2(win_width // 2, player_pos.y)
            self.player_one_cards.set_pos(pos)
            hand_card = self.deck.pop(0)
            hand_card.flip()
            self.player_one_cards.append(hand_card)

        # player two
        player_pos = Vector2(win_width // 2 - player_width // 2, margin)
        for i in range(3):
            pos = player_pos + Vector2(margin + CARD_SIZE[0], 0) * i
            vacant = Vacant(pos)
            vacants.append(vacant)
            
            lucky_flipped = self.deck.pop(0)
            lucky_flipped.set_pos(pos + vacant.link_offset)
            vacant.link_card(lucky_flipped)

            lucky_faced = self.deck.pop(0)
            lucky_faced.flip()
            lucky_faced.set_pos(pos + lucky_flipped.link_offset * 2)
            lucky_flipped.link_card(lucky_faced)

            # hand cards
            pos = Vector2(win_width // 2, player_pos.y + CARD_SIZE[1] * 2 + margin * 4)
            self.player_two_cards.set_pos(pos)
            hand_card = self.deck.pop(0)
            hand_card.flip()
            self.player_two_cards.append(hand_card)

        self.cards = vacants + cards
        self.card_manipulator.set_cards(self.cards)
        return self.cards
    

