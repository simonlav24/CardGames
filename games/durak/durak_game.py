



from utils import Vector2, shuffle
from game_globals import win_width, win_height

from core import Card, Vacant, create_deck, CARD_SIZE, Suit
from engine import RuleSet, EventType, GameBase
 
from games.durak.player import PlayerBase, Player
# from games.durak.ai_player import AiPlayer
from games.durak.game_routine import GameRoutine
from games.durak.durak_pot import DurakPot


class ShitheadRuleSet(RuleSet):
    def can_link_cards(self, upper: Card, lower: Card) -> bool:
        return False

    def can_drag_card(self, card: Card) -> bool:
        return False



class DurakGame(GameBase):
    def __init__(self):
        super().__init__()
        self.rules = ShitheadRuleSet()
        self.card_manipulator.set_rules(self.rules)

        self.deck: list[Card] = []
        self.pot: DurakPot = None
        self.burn_vacant = Vacant()
        self.kozer: Suit = None

        self.game_routine = GameRoutine()

    def handle_event(self, event):
        super().handle_event(event)

        if event.type == EventType.CLICK_CARD:
            self.game_routine.clicked_on_card(event.card)

        if event.type == EventType.DOUBLE_CLICK_CARD:
            ...
    
    def step(self):
        super().step()
        self.game_routine.step()

    def setup_game(self) -> list[Card]:
        cards = create_deck()
        shuffle(cards)
        self.deck += cards.copy()

        vacants: list[Vacant] = []
        margin = 10

        # pot
        pos = Vector2(win_width, win_height) // 2 - Vector2(CARD_SIZE) // 2
        self.pot = DurakPot(pos)
        
        deck_pos = Vector2(win_width // 2 - 5 * (margin + CARD_SIZE[0]), win_height // 2 - CARD_SIZE[1] // 2)
        burned_pos = Vector2(win_width // 2 + 4 * (margin + CARD_SIZE[0]), win_height // 2 - CARD_SIZE[1] // 2)

        self.burn_vacant.set_pos(burned_pos)
        self.burn_vacant.set_link_offset(Vector2(2,2))
        vacants.append(self.burn_vacant)

        pos = Vector2(0, 0)
        for i, card in enumerate(cards):
            if i == 0:
                card.set_pos(deck_pos.copy() + Vector2(-20, -20))
                card.flip()
                self.kozer = card.suit
                continue
            pos += Vector2(0.6,0.6)
            card.set_pos(deck_pos.copy() + pos)
        
        # currently for two players
        player_positions = [
            {
                'hand': Vector2(win_width // 2, win_height - CARD_SIZE[1] - margin),
                'ai': False
            },
            {
                'hand': Vector2(win_width // 2, margin),
                'ai': False
            },
        ]
        
        for positions in player_positions:
            if positions['ai']:
                player = Player()
            else:
                player = Player()
            
            player.initialize(self.pot, self.kozer)

            self.game_routine.add_player(player)

            for i in range(6):
                # hand cards
                hand = player.get_hand()
                pos = positions['hand']
                hand.set_pos(pos)
                hand_card = self.deck.pop()
                hand_card.flip()
                if positions['ai']:
                    hand_card.is_hidden = True
                hand.append(hand_card)

        self.game_routine.initialize(self.deck, self.pot, self.burn_vacant, self.kozer)

        self.cards = vacants + cards
        self.card_manipulator.set_cards(self.cards)

        self.game_routine.start()
        return self.cards
    

