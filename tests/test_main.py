""" Test functionality related to the packages entrypoint. """
import unittest

from paneldata_pipeline.__main__ import main


class TestMainModule(unittest.TestCase):  # pylint: disable=missing-docstring
    def test_main_method(self):
        """ Test entrypoint of the package. """
        self.assertIsInstance(main, object)
