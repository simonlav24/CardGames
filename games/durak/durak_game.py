



from utils import Vector2, shuffle
from game_globals import win_width, win_height, KEY_D

from core import Card, Vacant, create_deck, CARD_SIZE, Suit, rank_translate_ace_high, Rank
from engine import EventType, GameBase, DroppedCardEvent
 
from games.durak.player import PlayerBase, Player
# from games.durak.ai_player import AiPlayer
from games.durak.game_routine import GameRoutine
from games.durak.durak_pot import DurakPot



class DurakGame(GameBase):
    def __init__(self):
        super().__init__()
        self.game_routine = GameRoutine()
        self.card_manipulator.set_rules(self.game_routine)

        self.deck: list[Card] = []
        self.pot: DurakPot = None
        self.burn_vacant = Vacant()
        self.kozer: Suit = None

    def on_key_press(self, key: int) -> None:
        if key == KEY_D:
            self.game_routine.burn_pot()

    def handle_event(self, event):
        super().handle_event(event)

        if event.type == EventType.CLICK_CARD:
            self.game_routine.clicked_on_card(event.card)

        if event.type == EventType.DOUBLE_CLICK_CARD:
            self.game_routine.pick_up_pot()

        if event.type == EventType.DROPPED_CARD:
            event: DroppedCardEvent = event
            self.game_routine.on_placed_card_event(event.placed_card, event.placed_upon, event.last_pos, event.legal_drop)
    
    def step(self):
        super().step()
        self.game_routine.step()

    def setup_game(self) -> list[Card]:
        deck = create_deck()
        cards: list[Card] = []
        for card in deck:
            if rank_translate_ace_high(card.rank) < rank_translate_ace_high(Rank.SIX):
                continue
            cards.append(card)
        
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

            # deal cards
            hand = player.get_hand()
            pos = positions['hand']
            hand.set_pos(pos)
            for i in range(6):
                drawn_card = self.deck.pop()
                drawn_card.flip()
                if positions['ai']:
                    drawn_card.is_hidden = True
                player.deal(drawn_card)

        self.game_routine.initialize(self.deck, self.pot, self.burn_vacant, self.kozer)

        self.cards = vacants + cards
        self.card_manipulator.set_cards(self.cards)

        self.game_routine.start()
        return self.cards
    

