
import sys

import pygame
from pygame.math import Vector2

import custom_random
import globals
from card import Suit, create_deck, create_single_suit_deck, draw_card, Card, Vacant, CARD_SIZE
from card_event_handler import CardEventHandler, LINK_OFFSET
from animation import Animation
from spider_game import SpiderGame
from events import EventSystem, AnimationEvent


# def klondike() -> tuple[list[Card], list[Vacant]]:
#     deck = create_deck()
#     shuffle(deck)
#     for card in deck:
#         card.set_pos(Vector2(600, 400))
#     vacants: list[Vacant] = []
    
#     margin = 10
#     for i in range(7):

#         col = 100 + (CARD_SIZE[0] + margin) * i
#         # create vacant
#         vacants.insert(0, Vacant(Vector2(col, margin)))

#         # place i face down cards
#         for j in range(i):
#             card = deck.pop(0)
#             card.face_up = False
#             card.set_pos(Vector2(col, margin + (LINK_OFFSET.y * (j + 1))))
#             deck.append(card)
 
#         # place 1 face up card
#         card = deck.pop(0)
#         card.face_up = True
#         card.set_pos(Vector2(col, margin + (LINK_OFFSET.y * (i + 1))))
#         deck.append(card)

#     return deck, vacants


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

    game = SpiderGame()
    event_system = EventSystem()

    cards = game.setup_game()

    card_event_handler = CardEventHandler(game.rules, event_system)
    card_event_handler.set_cards(cards)

    animations = []
    is_animating = False


    # Main loop
    done = False
    while not done:
        for event in pygame.event.get():
            card_event_handler.handle_event(event)
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    done = True
                elif event.key == pygame.K_d:
                    game.deal_from_deck()

            elif event.type == pygame.USEREVENT:
                if event.dict.get("key") == "animation":
                    card = event.dict.get("card")
                    start_pos = event.dict.get("start_pos")
                    end_pos = event.dict.get("end_pos")
                    anim = Animation(card, start_pos, end_pos)
                    animations.append(anim)
                
                if event.dict.get("key") == 'move_to_top':
                    card = event.dict.get("card")
                    cards.remove(card)
                    cards.append(card)  # move to top

        is_animating = False
        animations = [anim for anim in animations if not anim.finished]
        if len(animations) > 0:
            is_animating = True
        for anim in animations:
            anim.step()

        # Fill screen with a color
        screen.fill((30, 30, 30))

        for card in cards:
            draw_card(screen, card)
        

        # Update display
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()