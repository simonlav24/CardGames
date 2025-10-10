
import sys

import pygame
from pygame.math import Vector2

import utils.custom_random as custom_random
import game_globals
from utils.card_draw import draw_card

from games.spider.spider_game import SpiderGame
from games.klondike.klondike_game import KlondikeGame
from games.shithead.shithead_game import ShitheadGame
from games.durak.durak_game import DurakGame


def main():
    # Initialize Pygame
    pygame.init()

    # Screen settings
    screen = pygame.display.set_mode((game_globals.win_width, game_globals.win_height))
    pygame.display.set_caption("Card Games")

    game_globals.init_globals()
    custom_random.initialize()

    # Clock for controlling FPS
    clock = pygame.time.Clock()
    FPS = 60
    DOUBLE_CLICK_INTERVAL = 400
    DOUBLE_CLICK_OFFSET_SQUARED = 25
 
    game = DurakGame()
    cards = game.setup_game()

    # Main loop
    last_click_time = 0
    last_click_pos = (0,0)

    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    done = True
                elif event.key:
                    game.on_key_press(event.key)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    current_time = pygame.time.get_ticks()
                    current_pos = event.pos
                    if (
                        current_time - last_click_time < DOUBLE_CLICK_INTERVAL and
                        Vector2(current_pos).distance_squared_to(last_click_pos) < DOUBLE_CLICK_OFFSET_SQUARED
                    ):
                        game.on_mouse_double_click(event.pos)
                    else:
                        game.on_mouse_press(event.pos)
                    last_click_time = current_time
                    last_click_pos = event.pos
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left click
                    game.on_mouse_release(event.pos)
            elif event.type == pygame.MOUSEMOTION:
                game.on_mouse_move(event.pos)

            elif event.type == pygame.USEREVENT:
                game.handle_event(event.dict.get('event'))

        # step
        game.step()

        # draw
        screen.fill((30, 30, 30))

        for card in cards:
            draw_card(screen, card)
        

        # display
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()