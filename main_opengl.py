from random import randint, uniform

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

from core import Card, CARD_SIZE, Rank

from utils import Vector2
import utils.custom_random as custom_random
import game_globals

from games.spider.spider_game import SpiderGame
from games.klondike.klondike_game import KlondikeGame
from games.shithead.shithead_game import ShitheadGame
from games.durak.durak_game import DurakGame

class Texture:
    def __init__(self, path: str):
        self.width = 0
        self.height = 0
        self.id = 0
        self._load(path)
    
    def _load(self, path: str) -> None:
        surface = pygame.image.load(path)
        surface = pygame.transform.flip(surface, False, True)
        image_data = pygame.image.tobytes(surface, "RGBA", 1)
        self.width, self.height = surface.get_size()

        self.id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.id)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.width, self.height, 0,
                    GL_RGBA, GL_UNSIGNED_BYTE, image_data)


WINDOW_SIZE = (1280, 720)
WINDOW_WIDTH, WINDOW_HEIGHT = WINDOW_SIZE
FPS = 60

def init():
    ortho = True

    pygame.init()
    pygame.display.set_mode(WINDOW_SIZE, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("CardsEngine")

    # Set up orthographic projection (2D)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    if ortho:
        # gluOrtho2D(0, WINDOW_WIDTH, WINDOW_HEIGHT, 0)  # top-left origin like Pygame
        glOrtho(0, WINDOW_WIDTH, WINDOW_HEIGHT, 0, -1000, 1000)
    else:
        gluPerspective(45, (WINDOW_WIDTH / WINDOW_HEIGHT), 0.1, 2000.0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if not ortho:
        gluLookAt(0, 0, 0, 0, 0, -1, 0, 1, 0)  # camera at origin looking toward -Z
        glTranslatef(-WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2, -1000)  # push backward
        glScalef(1, -1, 1)  # make y go downwards (like Pygame)
        glEnable(GL_DEPTH_TEST)

    # General GL settings
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glClearColor(0.1, 0.1, 0.1, 1.0)



card_assets_texture: Texture = None

def draw_card(card: Card):
    glEnable(GL_TEXTURE_2D)
    glColor4f(1.0, 1.0, 1.0, 1.0)
    glBindTexture(GL_TEXTURE_2D, card_assets_texture.id)
    glPushMatrix()

    x, y = card.pos
    w, h = CARD_SIZE

    if card.animation.is_selected:
        mouse = Vector2(pygame.mouse.get_pos())
        center = card.pos + CARD_SIZE / 2
        mouse_to_pos = center - mouse
        axis_of_rotation = Vector2(-mouse_to_pos[1], mouse_to_pos[0])
        dist = mouse.distance_to(center)

        glTranslatef(x + w/2, y + h/2, 0)
        angle = min(dist, 25)
        glRotatef(angle, axis_of_rotation.x, axis_of_rotation.y, 0)
        glTranslatef(-x - w/2, -y - h/2, 0)

    if card.rank == Rank.NONE:
        glDisable(GL_TEXTURE_2D)
        glColor3f(1.0, 0.3, 0.3)
        glBegin(GL_LINE_LOOP)
        glVertex3f(x,     y, 0)
        glVertex3f(x + w, y, 0)
        glVertex3f(x + w, y + h, 0)
        glVertex3f(x,     y + h, 0)
        glEnd()
        glPopMatrix()
        return

    glBegin(GL_QUADS)
    
    card_rect = get_card_sprite_rect(card)
    if not card.is_face_up():
        card_rect = get_card_sprite_rect(None)
    
    sx = card_rect.topleft[0] / card_assets_texture.width
    sy = card_rect.topleft[1] / card_assets_texture.height
    tx = card_rect.bottomright[0] / card_assets_texture.width
    ty = card_rect.bottomright[1] / card_assets_texture.height

    size_adding = card.animation.size_factor * 5.0
    y -= size_adding / 2
    x -= size_adding / 2
    w += size_adding
    h += size_adding

    glTexCoord2f(sx, sy); glVertex3f(x,     y, 0)
    glTexCoord2f(tx, sy); glVertex3f(x + w, y, 0)
    glTexCoord2f(tx, ty); glVertex3f(x + w, y + h, 0)
    glTexCoord2f(sx, ty); glVertex3f(x,     y + h, 0)
    glEnd()

    glPopMatrix()

back_index = 53 + randint(0, 21)
back_rect = pygame.Rect((back_index % 13) * CARD_SIZE[0], (back_index // 13) * CARD_SIZE[1], *CARD_SIZE)

class CardAnim:
    def __init__(self, card: Card):
        self.is_selected = False

        self.size_factor = 1.0
        self.size_factor_vel = 0.0
        self.size_factor_acc = 0.0
        self.card = card

        self.target_size_factor = 0.0

    def step(self) -> None:
        dt = 0.7
        force = - 1 * (self.size_factor - self.target_size_factor)
        self.size_factor_acc = force
        self.size_factor_vel += self.size_factor_acc * dt
        self.size_factor_vel *= 0.65
        self.size_factor += self.size_factor_vel * dt

    def reset(self) -> None:
        self.target_size_factor = 0.0
        self.is_selected = False
        



def get_card_sprite_rect(card: Card | None) -> pygame.Rect:
    if card is None:
        return back_rect  # Back of card
    x = (card.rank.value - 1) * CARD_SIZE[0]
    y = (card.suit.value - 1) * CARD_SIZE[1]
    return pygame.Rect(x, y, CARD_SIZE[0], CARD_SIZE[1])

DOUBLE_CLICK_INTERVAL = 400
DOUBLE_CLICK_OFFSET_SQUARED = 25



def main():
    global card_assets_texture
    init()
    
    game = SpiderGame()
    cards = game.setup_game()
    cards_animation: list[CardAnim] = []
    for card in cards:
        anim = CardAnim(card)
        card.animation = anim
        cards_animation.append(anim)

    clock = pygame.time.Clock()

    card_assets_texture = Texture("assets/card_sprite.png")

    last_click_time = 0
    last_click_pos = (0,0)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
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

        game.step()


        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        for card_anim in cards_animation:
            card_anim.reset()
            if card_anim.card is game.get_selected_card():
                card_anim.target_size_factor = 2.0
            card_anim.step()
            if game.get_selected_card() is card_anim.card:
                card_anim.is_selected = True

        for card in cards:
            draw_card(card)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()