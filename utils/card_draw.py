
import pygame

import game_globals
from core.card import Card, CARD_SIZE, Rank
from utils.utils import Rect, Vector2

DEBUG = True

def draw_card(surface: pygame.Surface, card: Card):
    card_rect = Rect(card.pos.x, card.pos.y, CARD_SIZE[0], CARD_SIZE[1])

    if card.rank == Rank.NONE:
        pygame.draw.rect(surface, (50, 50, 50), card_rect)
        pygame.draw.rect(surface, (0, 0, 0), card_rect, 2)
    else:
        if card.face_up:
            surface.blit(game_globals.card_sprites, card_rect, get_card_sprite_rect(card))
        else:
            surface.blit(game_globals.card_sprites, card_rect, get_card_sprite_rect(None))
    
    if card.linked_down is not None:
        if DEBUG:
            pygame.draw.line(surface, (255,0,0), card.pos + Vector2(-2, 0), card.linked_down.pos)


def get_card_sprite_rect(card: Card | None) -> pygame.Rect:
    if card is None:
        return pygame.Rect(142, 384, *CARD_SIZE)  # Back of card
    x = (card.rank.value - 1) * CARD_SIZE[0]
    y = (card.suit.value - 1) * CARD_SIZE[1]
    return pygame.Rect(x, y, CARD_SIZE[0], CARD_SIZE[1])