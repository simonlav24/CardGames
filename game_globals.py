

import pygame

font: pygame.Font | None = None
card_sprites: pygame.Surface | None = None

win_width: int = 1280
win_height: int = 720

KEY_D = 100
KEY_P = 112

def init_globals():
    global font, card_sprites
    pygame.font.init()

    font = pygame.font.Font(None, 36)
    card_sprites = pygame.image.load(r"assets/card_sprite.png")