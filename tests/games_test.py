


import unittest

from core import Card, Rank, Suit, HandCards
import engine.events

from games.durak.durak_table import DurakTable, GameStage
from games.durak.ai_player import hand_score



class TestDurak(unittest.TestCase):
    def test_attack_card_score(self):

        hand_cards = [
            Card(Rank.SIX, Suit.HEARTS),
            Card(Rank.EIGHT, Suit.HEARTS),
            Card(Rank.TEN, Suit.DIAMONDS),
            Card(Rank.KING, Suit.CLUBS),
            Card(Rank.SIX, Suit.SPADES),
            Card(Rank.JACK, Suit.SPADES),
        ]
        kozer = Suit.SPADES
        card_set = set(hand_cards)

        option_scores = [
            hand_score(card_set - set([hand_cards[0]]), kozer),
            hand_score(card_set - set([hand_cards[1]]), kozer),
            hand_score(card_set - set([hand_cards[2]]), kozer),
            hand_score(card_set - set([hand_cards[3]]), kozer),
            hand_score(card_set - set([hand_cards[4]]), kozer),
            hand_score(card_set - set([hand_cards[5]]), kozer),
        ]
        
        self.assertEqual(option_scores[0], 78)
        self.assertEqual(option_scores[-1], 58)
        self.assertEqual(max(option_scores), option_scores[0])
        self.assertEqual(min(option_scores), option_scores[5])
        self.assertEqual(max(option_scores), 78)

    def test_attack_card_pairs(self):
        hand_cards = [
            Card(Rank.SIX, Suit.HEARTS),
            Card(Rank.SIX, Suit.DIAMONDS),
            Card(Rank.EIGHT, Suit.HEARTS),
            Card(Rank.TEN, Suit.DIAMONDS),
            Card(Rank.KING, Suit.CLUBS),
            Card(Rank.JACK, Suit.SPADES),
        ]
        kozer = Suit.SPADES
        card_set = set(hand_cards)

        score = hand_score(card_set, kozer)

        self.assertEqual(score, 74)




