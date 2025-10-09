

from utils import randint
from core import Card, Vacant, Rank, rank_translate_ace_high, HandCards
from engine import post_event, ClickedCard, DoubleClickedCard
from games.shithead.player import PlayerBase, GameStage

special_ranks = [Rank.TWO, Rank.THREE, Rank.TEN]
under_seven_ranks = [Rank.FOUR, Rank.FIVE, Rank.SIX, Rank.SEVEN]

DEBUG = True

def debug_print(text: str) -> None:
    if DEBUG:
        print(f'> Ai Player: {text}')


class AiPlayer(PlayerBase):
    def start_ai_turn(self) -> bool:
        ''' start thinking round for ai, return True if turn is ended '''
        pile_rank = self.get_pile_top_effective_rank()
        debug_print(f'I see rank {pile_rank}')

        if self.get_game_stage() == GameStage.SECOND_LEVEL_LUCKY:
            # pick lucky and then play normally
            self.pick_lucky(self.second_level_lucky)
            return False

        # try to play lowest
        potential_card = self.get_lowest_non_special(pile_rank)
        if potential_card is not None:
            debug_print(f'I played lowest: {potential_card}')
            select_cards = self.gather_same(potential_card)
            self._play(select_cards)
            return True
        
        # play special card
        potential_card = self.get_special()
        if potential_card is not None:
            debug_print(f'I played special: {potential_card}')
            self._play([potential_card])
            return True

        # cant do anything -> pick up pile
        debug_print('cant do, picking up')
        self.pick_up_pile()
        return True


    def _play(self, selected_cards: list[Card]) -> None:
        ''' place selected cards on the deck '''
        for card in selected_cards:
            post_event(ClickedCard(card=card))
            if self.get_game_stage() in [GameStage.FIRST_LEVEL_LUCKY, GameStage.SECOND_LEVEL_LUCKY]:
                # click again to select
                post_event(ClickedCard(card=card))
        post_event(ClickedCard(self.pile_vacant))

    def gather_same(self, card: Card) -> list[Card]:
        if self.get_game_stage() in [GameStage.FIRST_LEVEL_LUCKY, GameStage.SECOND_LEVEL_LUCKY]:
            return [card]
        if card.rank == Rank.ACE:
            # ace not worth to multi place
            return [card]
        selected = [c for c in self.hand_cards if c.rank == card.rank]
        return selected

    def is_legal_move(self, rank: Rank, pile_rank: Rank) -> bool:
        if rank in special_ranks:
            return True
        if pile_rank == Rank.SEVEN:
            if rank in under_seven_ranks:
                return True
            else:
                return False
        if rank_translate_ace_high(rank) >= rank_translate_ace_high(pile_rank):
            return True
        return False

    def get_lowest_non_special(self, pile_rank: Rank) -> Card:
        cards = self.get_playable_cards()
        cards.sort(key=lambda x: rank_translate_ace_high(x.rank))
        cards = [card for card in cards if (
            card.rank not in special_ranks and
            self.is_legal_move(card.rank, pile_rank)
              )]
        if len(cards) == 0:
            return None
        return cards[0]
    
    def get_special(self) -> Card:
        cards = self.get_playable_cards()
        cards.sort(key=lambda x: rank_translate_ace_high(x.rank))
        cards = [card for card in cards if (
            card.rank in special_ranks
              )]
        if len(cards) == 0:
            return None
        return cards[0]
    
    def get_playable_cards(self) -> list[Card]:
        match self.get_game_stage():
            case GameStage.CARD_IN_HAND:
                cards = self.hand_cards.cards.copy()
            case GameStage.FIRST_LEVEL_LUCKY:
                cards = self.first_level_lucky.copy()
        return cards

    def pick_up_pile(self) -> None:
        ''' pick up pile, return True if ended turn '''
        if self.get_game_stage() == GameStage.FIRST_LEVEL_LUCKY:
            # pick anyone
            picked = self.pick_lucky(self.first_level_lucky)
            picked.is_hidden = True
        for card in self.hand_cards:
            card.is_hidden = True
        post_event(DoubleClickedCard(self.pile_vacant))

    def start_turn(self) -> bool:
        return self.start_ai_turn()

    def get_pile_top_effective_rank(self) -> Rank:
        pile_top = self.pile_vacant.get_bottom_link()
        while pile_top.rank == Rank.THREE:
            pile_top = pile_top.get_prev()
        return pile_top.rank
    
    def pick_lucky(self, group: list[Card]) -> Card:
        ''' at the stage of picking from lucky pile, pick random card '''
        rand_choice = randint(0, len(group) - 1)
        card = group[rand_choice]
        post_event(ClickedCard(card))
        return card

    def deal(self, card: Card) -> None:
        self.hand_cards.append(card)
        card.is_hidden = True



