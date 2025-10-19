

from dataclasses import dataclass
from enum import Enum

from core import Card, Suit
from games.durak.durak_pot import DurakPot

class GameStage(Enum):
    NONE = 0
    FIRST_ATTACK = 1
    FREE_PLAY = 2

@dataclass
class DurakTable:
    deck: list[Card]
    pot: DurakPot
    kozer: Suit
    stage: GameStage = GameStage.NONE