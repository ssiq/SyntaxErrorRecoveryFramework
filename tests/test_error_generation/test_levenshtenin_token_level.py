import Levenshtein
import unittest

from error_generation.levenshtenin_token_level import levenshtenin_distance

class TestLevenshteninTokenLevel(unittest.TestCase):

    def test_levenshtenin_distance(self):
        a = 'asd'
        b = 'abasd'

        target_distance = Levenshtein.distance(a, b)
        edit_pos = Levenshtein.editops(a, b)
        print('target_distance: {}, edit_pos: {}'.format(target_distance, edit_pos))
        distance, _ = levenshtenin_distance(list(a), list(b))
        self.assertEqual(distance, target_distance)
