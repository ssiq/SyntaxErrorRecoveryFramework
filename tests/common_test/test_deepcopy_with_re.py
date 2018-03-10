from common.deepcopy_with_re import deepcopy

import unittest
import re


class B(object):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __eq__(self, other):
        if isinstance(other, B):
            return other.a == self.a and other.b == self.b
        else:
            return False


class Test(unittest.TestCase):
    def test_deepcopy(self):
        a = ['stre', B(re.compile(r'fdas',), 1243), re.compile(r'fdsafdsgs'), [12, 34, 56]]
        b = deepcopy(a)
        self.assertEquals(a, b, "They do not contain the same message")
        self.assertNotEqual(id(a), id(b), "They are the same object")