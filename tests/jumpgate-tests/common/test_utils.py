import unittest

from jumpgate.common.utils import lookup


class TestLookup(unittest.TestCase):
    def test_lookup(self):
        self.assertEquals(lookup({}, 'key'), None)

        self.assertEquals(lookup({'key': 'value'}, 'key'), 'value')
        self.assertEquals(
            lookup({'key': {'key': 'value'}}, 'key', 'key'), 'value')
