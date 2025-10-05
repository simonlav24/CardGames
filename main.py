
import sys

import pygame

import custom_random
import globals
from card import draw_card

from spider_game import SpiderGame
from klondike_game import KlondikeGame


def main():
    # Initialize Pygame
    pygame.init()

    # Screen settings
    WIDTH, HEIGHT = 1280, 720
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Card Games")

    globals.init_globals()
    custom_random.initialize()

    # Clock for controlling FPS
    clock = pygame.time.Clock()
    FPS = 60

    game = KlondikeGame()
    cards = game.setup_game()

    # Main loop
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    done = True
                elif event.key == pygame.K_d:
                    game.deal_from_deck()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    game.on_mouse_press(event.pos)
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