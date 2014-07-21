from mock import MagicMock, patch

from jumpgate.common.exceptions import (Unauthorized, InvalidTokenError)
from jumpgate.identity.drivers.sl.tokens import (NoAuthDriver, SLAuthDriver,
                                                 TokensV2, FakeTokenIdDriver
                                                 )
import unittest


class TestNoAuthDriver(unittest.TestCase):

    def setUp(self):
        self.creds = MagicMock()
        self.instance = NoAuthDriver()

    @patch('SoftLayer.Client')
    def test_authenticate(self, mockSLClient):
        mockAccount = MagicMock()
        mockAccount.getCurrentUser.return_value = 'testuser'
        mockSLClient.return_value = {'Account': mockAccount}

        result = self.instance.authenticate(self.creds)
        self.assertEquals(result['user'], 'testuser')


class TestFakeTokenIdDriver(unittest.TestCase):

    def setUp(self):
        self.token_id = MagicMock()
        self.instance = FakeTokenIdDriver()

    @patch('jumpgate.identity.drivers.core')
    def test_invalid_auth_driver(self, mockIdentity):
        mockIdentity.auth_driver.return_value = SLAuthDriver()
        with self.assertRaises(InvalidTokenError):
            self.instance.token_from_id(self.token_id)

    @patch('jumpgate.identity.drivers.core')
    @patch('jumpgate.identity.drivers.sl.tokens.NoAuthDriver')
    def test_auth_failed(self, mockIdentity, mockNoAuthDriver):
        mockIdentity.auth_driver.return_value = mockNoAuthDriver
        mockNoAuthDriver.authenticate.return_value = None
        with self.assertRaises(Unauthorized):
            self.instance.token_from_id(self.token_id)
