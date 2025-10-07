

from core import Card, Vacant, Rank, rank_translate_ace_high, HandCards
from engine import post_event, ClickedCard, DoubleClickedCard

special_ranks = [Rank.TWO, Rank.THREE, Rank.TEN]
under_seven_ranks = [Rank.FOUR, Rank.FIVE, Rank.SIX, Rank.SEVEN]

DEBUG = True

def debug_print(text: str) -> None:
    if DEBUG:
        print(f'> Ai Player: {text}')


class AiPlayer:
    def __init__(self):
        self.hand: HandCards = None
        self.pile_vacant: Vacant

    def initialize(self, hand: HandCards, pile_vacant: Vacant) -> None:
        self.hand = hand
        self.pile_vacant = pile_vacant

    def start_turn(self, pile_rank: Rank) -> Card:
        ''' start thinking round for ai '''

        # try to play lowest
        potential_card = self.get_lowest_non_special(pile_rank)
        if potential_card is not None:
            debug_print(f'played lowest: {potential_card}')
            select_cards = self.gather_same(potential_card)
            self._play(select_cards)
            return
        
        # play special card
        potential_card = self.get_special()
        if potential_card is not None:
            debug_print(f'played special: {potential_card}')
            self._play([potential_card])
            return

        # cant do anything -> pick up pile
        self.pick_up_pile()

        debug_print('Ai stuck')

    def _play(self, selected_cards: list[Card]) -> None:
        ''' place selected cards on the deck '''
        # time.sleep(1)
        for card in selected_cards:
            post_event(ClickedCard(card=card))
            # time.sleep(1)
        post_event(ClickedCard(self.pile_vacant))

    def get_cards_in_hand(self) -> list[Card]:
        return self.hand.cards.copy()

    def gather_same(self, card: Card) -> list[Card]:
        cards = self.get_cards_in_hand()
        if card.rank == Rank.ACE:
            # ace not worth to multi place
            return [card]
        selected = [c for c in cards if c.rank == card.rank]
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
        cards = self.get_cards_in_hand()
        cards.sort(key=lambda x: rank_translate_ace_high(x.rank))
        cards = [card for card in cards if (
            card.rank not in special_ranks and
            self.is_legal_move(card.rank, pile_rank)
              )]
        if len(cards) == 0:
            return None
        return cards[0]
    
    def get_special(self) -> Card:
        cards = self.get_cards_in_hand()
        cards.sort(key=lambda x: rank_translate_ace_high(x.rank))
        cards = [card for card in cards if (
            card.rank in special_ranks
              )]
        if len(cards) == 0:
            return None
        return cards[0]
    
    def pick_up_pile(self) -> None:
        post_event(DoubleClickedCard(self.pile_vacant))



