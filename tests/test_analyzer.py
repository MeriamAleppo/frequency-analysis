import unittest
from src.analyzer import FrequencyAnalyzer


class TestFrequencyAnalyzer(unittest.TestCase):
    def test_frequency_calculation(self):
        # Teks dengan 4 huruf: 2 'A', 1 'B', 1 'C'
        text = "A A B C"
        analyzer = FrequencyAnalyzer(text, language='EN')
        self.assertEqual(analyzer.total_letters, 4)
        self.assertAlmostEqual(analyzer.observed_freq['A'], 50.0)
        self.assertAlmostEqual(analyzer.observed_freq['B'], 25.0)
        self.assertAlmostEqual(analyzer.observed_freq['C'], 25.0)
        self.assertAlmostEqual(analyzer.observed_freq['D'], 0.0)

    def test_ioc_calculation(self):
        # Tes teks identik (semua 'A') -> IoC harus 1.0
        text = "AAAAA"
        analyzer = FrequencyAnalyzer(text, language='EN')
        self.assertAlmostEqual(analyzer.calculate_ioc(), 1.0)

        # Tes teks kosong atau 1 huruf -> IoC 0.0
        empty_analyzer = FrequencyAnalyzer("", language='EN')
        self.assertEqual(empty_analyzer.calculate_ioc(), 0.0)

    def test_language_switch(self):
        analyzer = FrequencyAnalyzer("Halo", language='EN')
        self.assertEqual(analyzer.language, 'EN')
        analyzer.set_language('ID')
        self.assertEqual(analyzer.language, 'ID')


if __name__ == '__main__':
    unittest.main()
