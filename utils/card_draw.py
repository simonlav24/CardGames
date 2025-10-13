
from random import randint

import pygame

import game_globals
from core.card import Card, CARD_SIZE, Rank
from utils.utils import Rect, Vector2

DEBUG = False

back_index = 53 + randint(0, 21)
back_rect = pygame.Rect((back_index % 13) * CARD_SIZE[0], (back_index // 13) * CARD_SIZE[1], *CARD_SIZE)

def draw_card(surface: pygame.Surface, card: Card):
    card_rect = Rect(card.pos.x, card.pos.y, CARD_SIZE[0], CARD_SIZE[1])

    if card.rank == Rank.NONE:
        pygame.draw.rect(surface, (50, 50, 50), card_rect)
        pygame.draw.rect(surface, (0, 0, 0), card_rect, 2)
    else:
        if card.face_up and not card.is_hidden:
            surface.blit(game_globals.card_sprites, card_rect, get_card_sprite_rect(card))
        else:
            surface.blit(game_globals.card_sprites, card_rect, get_card_sprite_rect(None))
    
    if DEBUG and card.linked_down is not None:
        pygame.draw.line(surface, (255,0,0), card.pos + Vector2(-2, 0), card.linked_down.pos)


def get_card_sprite_rect(card: Card | None) -> pygame.Rect:
    if card is None:
        return back_rect  # Back of card
    x = (card.rank.value - 1) * CARD_SIZE[0]
    y = (card.suit.value - 1) * CARD_SIZE[1]
    return pygame.Rect(x, y, CARD_SIZE[0], CARD_SIZE[1])