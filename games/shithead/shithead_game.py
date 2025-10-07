



from utils import Vector2, shuffle
from game_globals import win_width, win_height

from core import Card, Vacant, create_deck, CARD_SIZE, Pile
from engine import RuleSet, EventType, GameBase
 
from games.shithead.player import Player
from games.shithead.ai_player import AiPlayer
from games.shithead.game_routine import GameRoutine


class ShitheadRuleSet(RuleSet):
    def can_link_cards(self, upper: Card, lower: Card) -> bool:
        return False

    def can_drag_card(self, card: Card) -> bool:
        return False



class ShitheadGame(GameBase):
    def __init__(self):
        super().__init__()
        self.rules = ShitheadRuleSet()
        self.card_manipulator.set_rules(self.rules)

        self.deck: list[Card] = []
        self.pile = Pile()
        self.burn_vacant = Vacant()

        self.game_routine = GameRoutine()

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
        self.game_routine.step()

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
        player_positions = [
            {
                'lucky': Vector2(win_width // 2 - player_width // 2, win_height - margin - CARD_SIZE[1] - margin * 4),
                'hand': Vector2(win_width // 2, win_height - margin - CARD_SIZE[1] * 2 - margin * 5),
                'ai': False
            },
            {
                'lucky': Vector2(win_width // 2 - player_width // 2, margin),
                'hand': Vector2(win_width // 2, margin + CARD_SIZE[1] + margin * 5),
                'ai': True
            }
        ]
        
        for positions in player_positions:
            ai = None
            if positions['ai']:
                ai = AiPlayer()
            player = Player(ai=ai)
            if positions['ai']:
                ai.initialize(player.get_hand(), self.pile.vacant)

            self.game_routine.add_player(player)

            for i in range(3):
                pos = positions['lucky'] + Vector2(margin + CARD_SIZE[0], 0) * i
                # vacant for second lucky
                vacant = Vacant(pos)
                vacants.append(vacant)
                
                lucky_flipped = self.deck.pop(0)
                player.deal_second_lucky_card(lucky_flipped)
                lucky_flipped.set_pos(pos + vacant.link_offset)
                vacant.link_card(lucky_flipped)

                lucky_faced = self.deck.pop(0)
                player.deal_first_lucky_card(lucky_faced)
                lucky_faced.flip()
                lucky_faced.set_pos(pos + lucky_flipped.link_offset * 2)
                lucky_flipped.link_card(lucky_faced)

                # hand cards
                hand = player.get_hand()
                pos = positions['hand']
                hand.set_pos(pos)
                hand_card = self.deck.pop(0)
                hand_card.flip()
                hand.append(hand_card)

        self.game_routine.initialize(self.deck, self.pile, self.burn_vacant)

        self.cards = vacants + cards
        self.card_manipulator.set_cards(self.cards)

        self.game_routine.start()
        return self.cards
    

