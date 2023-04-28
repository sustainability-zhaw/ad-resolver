import unittest
from utils import build_full_name_variations

class TestBuildFullNameVariations(unittest.TestCase):

    def test_build_full_name_variations(self):
        full_names_and_expectations = [
            ('Stohner, Jürgen', [('Stohner', 'Jürgen')]),
            ('Pothier, Joël F.', [('Pothier', 'Joël F.'), ('Pothier', 'Joël')]),
            ('Pothier, Joël (F.)', [('Pothier', 'Joël (F.)'), ('Pothier', 'Joël')]),
            ('Pehlke-Milde, Jessica', [('Pehlke-Milde', 'Jessica'), ('Pehlke', 'Jessica'), ('Milde', 'Jessica')]),
            ('von Wyl, Agnes', [('von Wyl', 'Agnes'), ('von-Wyl', 'Agnes'), ('von', 'Agnes'), ('Wyl', 'Agnes')]),
            ('Föhn, Martina', [('Föhn', 'Martina')])
        ]

        for fullname_and_expectation in full_names_and_expectations:
            full_name, expectation = fullname_and_expectation
            with self.subTest(full_name=full_name, expectation=expectation):
                self.assertEqual(build_full_name_variations(full_name), expectation, f"Expectation for {full_name} not matched.")


if __name__ == '__main__':
    unittest.main()