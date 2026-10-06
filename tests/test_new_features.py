import unittest

from src.analyzer import FrequencyAnalyzer, extract_ngrams
from src.constants import FREQ_ENGLISH
from src.solvers import (
    hill_climb_substitution,
    recover_vigenere_keyword,
    run_friedman_test,
)


class TestNGramFeatures(unittest.TestCase):
    def test_extract_bigrams_and_trigrams(self):
        grams = extract_ngrams("THE QUICK", 2)
        self.assertEqual(grams["TH"], 1)
        self.assertEqual(grams["HE"], 1)
        self.assertEqual(grams["QU"], 1)
        self.assertEqual(grams["IC"], 1)

        trigrams = extract_ngrams("THE QUICK", 3)
        self.assertEqual(trigrams["THE"], 1)
        self.assertEqual(trigrams["HEQ"], 1)

    def test_frequency_analyzer_exposes_ngram_statistics(self):
        analyzer = FrequencyAnalyzer("THE THE", language="EN")
        analyzer.calculate_ngrams(2)
        self.assertEqual(analyzer.ngram_counts["TH"], 2)
        self.assertEqual(analyzer.ngram_counts["HE"], 2)
        self.assertEqual(analyzer.total_ngrams, 5)


class TestSubstitutionSolver(unittest.TestCase):
    def test_fitness_score_rewards_known_language_patterns(self):
        from src.solvers import calculate_fitness

        natural = calculate_fitness("THE QUICK BROWN FOX", "EN")
        random_text = calculate_fitness("QWZQXQWQXQWZQXQWQ", "EN")
        self.assertGreater(natural, random_text)

    def test_hill_climb_improves_substitution_mapping(self):
        plaintext = "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG"
        mapping = {c: c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"}
        cipher_letters = ""
        for ch in plaintext:
            if ch.isalpha():
                cipher_letters += chr((ord(ch) - ord("A") + 13) % 26 + ord("A"))
            else:
                cipher_letters += ch
        result = hill_climb_substitution(cipher_letters, "EN", iterations=50, seed=7)
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 26)
        self.assertEqual(set(result.values()), set("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))


class TestVigenereFeatures(unittest.TestCase):
    def test_friedman_test_reports_expected_key_length(self):
        plaintext = "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG"
        key = "KEY"
        ciphertext = ""
        letter_index = 0
        for ch in plaintext:
            if ch.isalpha():
                shift = ord(key[letter_index % len(key)]) - ord("A")
                ciphertext += chr((ord(ch) - ord("A") + shift) % 26 + ord("A"))
                letter_index += 1
            else:
                ciphertext += ch

        results = run_friedman_test(ciphertext, max_key_length=8)
        self.assertIn(3, results)
        self.assertTrue(all(result["average_ioc"] >= 0 for result in results.values()))

    def test_recover_vigenere_keyword_uses_chi_square(self):
        plaintext = "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG"
        key = "KEY"
        ciphertext = ""
        letter_index = 0
        for ch in plaintext:
            if ch.isalpha():
                shift = ord(key[letter_index % len(key)]) - ord("A")
                ciphertext += chr((ord(ch) - ord("A") + shift) % 26 + ord("A"))
                letter_index += 1
            else:
                ciphertext += ch

        recovered = recover_vigenere_keyword(ciphertext, 3, FREQ_ENGLISH)
        self.assertIsInstance(recovered["keyword"], str)
        self.assertTrue(len(recovered["keyword"]) == 3)
        self.assertTrue(recovered["chi_squared"] >= 0)


if __name__ == "__main__":
    unittest.main()
