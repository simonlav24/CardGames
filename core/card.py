
from enum import Enum

from utils.utils import Vector2, Rect

import game_globals

DEBUG = False

CARD_SIZE = Vector2(0, 0)
DEFAULT_LINK_OFFSET = Vector2(0, 17)

class Rank(Enum):
    NONE = 0
    ACE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    JOKER = 14


class Suit(Enum):
    NONE = 0
    SPADES = 1
    HEARTS = 2
    CLUBS = 3
    DIAMONDS = 4
    JOKER = 5

suit_text = {
    Suit.HEARTS: "Hearts",
    Suit.DIAMONDS: "Diamonds",
    Suit.CLUBS: "Clubs",
    Suit.SPADES: "Spades"
}

suit_color = {
    Suit.HEARTS: (255, 0, 0),
    Suit.DIAMONDS: (255, 0, 0),
    Suit.CLUBS: (0, 0, 0),
    Suit.SPADES: (0, 0, 0)
}

rank_text = {
    Rank.ACE: "Ace",
    Rank.TWO: "2",
    Rank.THREE: "3",
    Rank.FOUR: "4",
    Rank.FIVE: "5",
    Rank.SIX: "6",
    Rank.SEVEN: "7",
    Rank.EIGHT: "8",
    Rank.NINE: "9",
    Rank.TEN: "10",
    Rank.JACK: "Jack",
    Rank.QUEEN: "Queen",
    Rank.KING: "King"
}

def initialize(card_size: tuple[int, int]) -> None:
    global CARD_SIZE
    CARD_SIZE.x = card_size[0]
    CARD_SIZE.y = card_size[1]

def sort_aces_low(rank: Rank) -> int:
    return rank.value

def sort_aces_high(rank: Rank) -> int:
    if rank == Rank.ACE:
        return 14
    return rank.value


class Card:
    def __init__(self, rank: Rank, suit: Suit):
        self.rank = rank
        self.suit = suit
        self.face_up = True
        
        self.pos = Vector2()
        self.target_pos = Vector2()

        self.is_hidden = False
        self.parent = None

    def set_pos(self, pos: Vector2) -> None:
        self.target_pos = pos.copy()

    def set_abs_pos(self, pos: Vector2) -> None:
        self.target_pos = pos.copy()
        self.pos = pos.copy()

    def get_pos(self) -> Vector2:
        return self.target_pos.copy()

    def __repr__(self):
        return f"{rank_text[self.rank]} of {suit_text[self.suit]}"
    
    def is_face_up(self) -> bool:
        return self.face_up

    def flip(self) -> None:
        self.face_up = not self.face_up

    def step(self) -> None:
        self.pos = self.pos + (self.target_pos - self.pos) * 0.2
        if self.pos.distance_squared_to(self.target_pos) < 1:
            self.pos = self.target_pos
    

class Vacant(Card):
    def __init__(self, pos: Vector2 = Vector2(0,0)):
        super().__init__(Rank.NONE, Suit.NONE)
        self.target_pos = pos

    def __repr__(self):
        return "Vacant"



def create_deck(joker_allowed: bool=False) -> list[Card]:
    deck = []
    for suit in Suit:
        if suit in [Suit.NONE, Suit.JOKER]:
            continue
        for rank in Rank:
            if rank in [Rank.NONE, Rank.JOKER]:
                continue
            card = Card(rank, suit)
            card.face_up = False
            deck.append(card)
    
    if joker_allowed:
        joker1 = Card(Rank.JOKER, Suit.JOKER)
        joker1.face_up = False
        deck.append(joker1)
        joker2 = Card(Rank.JOKER, Suit.JOKER)
        joker2.face_up = False
        deck.append(joker2)

    return deck

def create_single_suit_deck(suit: Suit) -> list[Card]:
    deck = []
    for rank in Rank:
        if rank in [Rank.NONE, Rank.JOKER]:
            continue
        card = Card(rank, suit)
        card.face_up = False
        deck.append(card)

    return deck
