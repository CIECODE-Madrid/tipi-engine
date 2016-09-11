import unittest




class TestConfig(unittest.TestCase):


    def test_numbers_3_4(self):
        self.assertEqual(3*4, 12)

    def test_strings_a_3(self):
        self.assertEqual(1*2, 2)


if __name__ == '__main__':
    unittest.main()