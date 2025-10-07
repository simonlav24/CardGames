



from core import Card, Vacant, Rank, rank_translate_ace_high, Pile
from engine import post_event, DelayedSetPosEvent

from games.shithead.player import Player, GameStage


class GameRoutine:
    def __init__(self):
        self.num_of_players = 2
        self.players: list[Player] = []
        self.current_player_index = 0

        self.deck: list[Card] = None
        self.pile: Pile = None
        self.burn_vacant: Vacant = None
        self.rank_translate = rank_translate_ace_high

        self.event = None

    def initialize(self, deck: list[Card], pile: Pile, burn_vacant: Vacant) -> None:
        self.deck = deck
        self.pile = pile
        self.burn_vacant = burn_vacant

    def add_player(self, player: Player) -> None:
        self.players.append(player)

    def start(self) -> None:
        self.players[self.current_player_index].toggle_turn()

    def end_turn(self) -> None:
        self.players[self.current_player_index].toggle_turn()
        self.current_player_index = (self.current_player_index + 1) % self.num_of_players
        current_player = self.players[self.current_player_index]
        current_player.toggle_turn()
        self.reset_turn()
        
    def reset_turn(self) -> None:
        current_player = self.players[self.current_player_index]
        if current_player.is_ai():
            self.event = {'time': 60, 'function': current_player.ai_play, 'arg': self.get_pile_top_effective_rank()}

    def can_play_card(self, card: Card) -> bool:
        # can always play special cards
        if self.is_card_special(card):
            return True

        effective_rank = self.get_pile_top_effective_rank()

        match effective_rank:
            case Rank.NONE | Rank.TWO | Rank.THREE:
                return True
            
            case Rank.SEVEN:
                if self.rank_translate(card.rank) <= self.rank_translate(Rank.SEVEN):
                    return True
                else:
                    return False

        if self.rank_translate(card.rank) >= self.rank_translate(effective_rank):
            return True
        return False
            

    def is_card_special(self, card: Card) -> bool:
        return card.rank in [Rank.TWO, Rank.THREE, Rank.TEN]

    def clicked_on_card(self, card: Card) -> None:
        current_player = self.players[self.current_player_index]
        current_hand = current_player.get_hand()

        # click on pile -> play
        if card in self.pile:
            cards_to_play = current_hand.get_selected()
            if len(cards_to_play) == 0:
                return
            if self.can_play_card(cards_to_play[0]):
                self.play_cards(cards_to_play)
            return

        # click on card -> select
        if card in current_hand:
            current_hand.toggle_select(card)
            return
        
        # late game, choose from first pile
        if current_player.get_game_stage() == GameStage.FIRST_LEVEL_LUCKY:
            if card in current_player.first_level_lucky:
                # move card to hand
                card.break_upper_link()
                current_player.first_level_lucky.remove(card)
                current_player.get_hand().append(card)
        
        elif current_player.get_game_stage() == GameStage.SECOND_LEVEL_LUCKY:
            if card in current_player.second_level_lucky:
                # move card to hand
                card.break_upper_link()
                card.flip()
                current_player.second_level_lucky.remove(card)
                current_player.get_hand().append(card)
        
        

    def get_pile_top_effective_rank(self) -> Rank:
        pile_top = self.pile.get_top()
        while pile_top.rank == Rank.THREE:
            pile_top = pile_top.get_prev()
        return pile_top.rank

    def play_cards(self, cards: list[Card]) -> None:
        ''' play the card into the pile '''
        print(f'play card {cards[0]}')
        advance_turn = True
        hands = self.players[self.current_player_index].get_hand()
        pile_top = self.pile.get_top()

        # move card to pile
        for i, card in enumerate(cards):
            hands.remove(card)
            self.pile.append(card)
            card.set_pos(pile_top.pos + pile_top.link_offset * (i + 1))

        # complete to hand
        if len(self.deck) > 0:
            while len(hands) < 3:
                drawn_card = self.deck.pop(0)
                drawn_card.flip()
                hands.append(drawn_card)

        # check for effects
        match cards[0].rank:
            case Rank.TEN:
                self.burn_pile()
                advance_turn = False

            case Rank.THREE:
                effective_rank = self.get_pile_top_effective_rank()
                if effective_rank == Rank.EIGHT:
                    advance_turn = False

            case Rank.EIGHT:
                advance_turn = False

        # check if four of a kind
        pile_top = self.pile.get_top()
        rank = pile_top.rank
        rank_count = 0
        try_count = 0
        current_card = pile_top
        while current_card is not None:
            if current_card.rank == rank:
                rank_count += 1
            try_count += 1
            if try_count >= 4:
                break
            current_card = current_card.get_prev()
        if rank_count == 4:
            self.burn_pile()
            advance_turn = False

        # advance turn
        if advance_turn:
            self.end_turn()
        else:
            self.reset_turn()

        print(f'player {self.current_player_index + 1} turn')

    def burn_pile(self) -> None:
        last_card = self.burn_vacant.get_bottom_link()
        pos = last_card.get_pos()
        self.pile.vacant.break_lower_link()
        for i, card in enumerate(self.pile):
            last_card.link_card(card)
            post_event(DelayedSetPosEvent(card, pos + i * self.burn_vacant.link_offset, delay=30 + i))
            last_card = card
        
        self.pile.clear()

    def pick_up_pile(self) -> None:
        hands = self.players[self.current_player_index].get_hand()
        for card in self.pile:
            card.break_lower_link()
            card.break_upper_link()
            hands.append(card)
        self.pile.clear()
        
        self.end_turn()

    def step(self) -> None:
        for player in self.players:
            player.step()
        if self.event:
            self.event['time'] -= 1
            if self.event['time'] <= 0:
                self.event['function'](self.event['arg'])
                self.event = None
