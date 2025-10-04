
from enum import Enum

import pygame
from pygame.math import Vector2

import globals

DEBUG = True

CARD_SIZE = Vector2(71, 96)
LINK_OFFSET = Vector2(0, 17)

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


class Suit(Enum):
    NONE = 0
    SPADES = 1
    HEARTS = 2
    CLUBS = 3
    DIAMONDS = 4

suit_text = {
    Suit.HEARTS: "H",
    Suit.DIAMONDS: "D",
    Suit.CLUBS: "C",
    Suit.SPADES: "S"
}

suit_color = {
    Suit.HEARTS: (255, 0, 0),
    Suit.DIAMONDS: (255, 0, 0),
    Suit.CLUBS: (0, 0, 0),
    Suit.SPADES: (0, 0, 0)
}

rank_text = {
    Rank.ACE: "A",
    Rank.TWO: "2",
    Rank.THREE: "3",
    Rank.FOUR: "4",
    Rank.FIVE: "5",
    Rank.SIX: "6",
    Rank.SEVEN: "7",
    Rank.EIGHT: "8",
    Rank.NINE: "9",
    Rank.TEN: "10",
    Rank.JACK: "J",
    Rank.QUEEN: "Q",
    Rank.KING: "K"
}


class Card:
    def __init__(self, rank: Rank, suit: Suit):
        self.rank = rank
        self.suit = suit
        self.face_up = True
        self.pos = Vector2(0, 0)
        self.linked_up: Card | None = None
        self.linked_down: Card | None = None

    def set_pos(self, pos: Vector2):
        self.pos = pos
        # if self.linked_down is not None:
        #     self.linked_down.set_pos(pos + LINK_OFFSET)

    def get_bottom_link(self) -> 'Card':
        # return bottom most linked card
        card = self
        while card.linked_down is not None:
            card = card.linked_down
        return card

    def is_linked(self) -> bool:
        # check if linked from above
        return self.linked_up is not None
    
    def get_next(self) -> 'Card | None':
        return self.linked_down
    
    def get_prev(self) -> 'Card | None':
        return self.linked_up
    
    def break_upper_link(self):
        # break link to upper card
        if self.linked_up is not None:
            self.linked_up.linked_down = None
            self.linked_up = None

    def link_card(self, card: 'Card') -> bool:
        # link a card below this card

        for uplink in self.iterate_up():
            if uplink is self:
                continue
            if uplink is card:
                return False  # already linked
        for downlink in self.iterate_down():
            if downlink is self:
                continue
            if downlink is card:
                return False  # already linked

        if card.linked_up is not None:
            card.break_upper_link()    
        
        self.linked_down = card
        card.linked_up = self
        return True

    def __repr__(self):
        return f"{rank_text[self.rank]}{suit_text[self.suit]}"
    
    def iterate_up(self):
        card = self
        while card is not None:
            yield card
            card = card.linked_up

    def iterate_down(self):
        card = self
        while card is not None:
            yield card
            card = card.linked_down

    def is_face_up(self) -> bool:
        return self.face_up

    def flip(self):
        self.face_up = not self.face_up
    

class Vacant(Card):
    def __init__(self, pos: Vector2 = Vector2(0,0)):
        super().__init__(Rank.NONE, Suit.NONE)
        self.pos = pos

    def __repr__(self):
        return "Vacant"


def draw_card(surface: pygame.Surface, card: Card):
    card_rect = pygame.Rect(card.pos.x, card.pos.y, CARD_SIZE[0], CARD_SIZE[1])

    if card.rank == Rank.NONE:
        pygame.draw.rect(surface, (50, 50, 50), card_rect)
        pygame.draw.rect(surface, (0, 0, 0), card_rect, 2)
    else:
        if card.face_up:
            surface.blit(globals.card_sprites, card_rect, get_card_sprite_rect(card))
        else:
            surface.blit(globals.card_sprites, card_rect, get_card_sprite_rect(None))
    
    if card.linked_down is not None:
        if DEBUG:
            pygame.draw.line(surface, (255,0,0), card.pos + Vector2(-2, 0), card.linked_down.pos)


def get_card_sprite_rect(card: Card | None) -> pygame.Rect:
    if card is None:
        return pygame.Rect(142, 384, *CARD_SIZE)  # Back of card
    x = (card.rank.value - 1) * CARD_SIZE[0]
    y = (card.suit.value - 1) * CARD_SIZE[1]
    return pygame.Rect(x, y, CARD_SIZE[0], CARD_SIZE[1])


def create_deck() -> list[Card]:
    deck = []
    for suit in Suit:
        if suit == Suit.NONE:
            continue
        for rank in Rank:
            if rank == Rank.NONE:
                continue
            card = Card(rank, suit)
            card.face_up = False
            deck.append(card)

    return deck

def create_single_suit_deck(suit: Suit) -> list[Card]:
    deck = []
    for rank in Rank:
        if rank == Rank.NONE:
            continue
        card = Card(rank, suit)
        card.face_up = False
        deck.append(card)

    return deck
