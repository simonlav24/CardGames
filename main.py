
import sys

import pygame

import custom_random
import game_globals
from card import draw_card

from spider_game import SpiderGame
from klondike_game import KlondikeGame
from shithead_game import ShitheadGame


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

    game = ShitheadGame()
    cards = game.setup_game()

    # Main loop
    last_click_time = 0

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
                    if current_time - last_click_time < DOUBLE_CLICK_INTERVAL:
                        game.on_mouse_double_click(event.pos)
                    game.on_mouse_press(event.pos)
                    last_click_time = current_time
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