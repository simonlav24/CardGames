

import pygame

font: pygame.Font | None = None
card_sprites: pygame.Surface | None = None

def init_globals():
    global font, card_sprites
    pygame.font.init()

    font = pygame.font.Font(None, 36)
    card_sprites = pygame.image.load(r"assets/card_sprite.png")