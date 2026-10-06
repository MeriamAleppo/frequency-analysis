import unittest
from src.solvers import (
    auto_solve_caesar,
    decrypt_text,
    detect_mapping_conflicts
)
from src.constants import FREQ_ENGLISH


class TestSolvers(unittest.TestCase):
    def test_auto_solve_caesar(self):
        # Plaintext bahasa Inggris cukup panjang agar distribusi frekuensi jelas
        plaintext = (
            "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG AND RUNS THROUGH THE FOREST "
            "WHERE MANY ANIMALS RESIDE PEACEFULLY IN NATURE AND HARMONY"
        )
        shift = 4
        # Enkripsi dengan shift 4
        encrypted = []
        for c in plaintext:
            if c.isalpha():
                encrypted.append(chr((ord(c) - ord('A') + shift) % 26 + ord('A')))
            else:
                encrypted.append(c)
        ciphertext = "".join(encrypted)

        best_shift, chi2, mapping = auto_solve_caesar(ciphertext, FREQ_ENGLISH)
        self.assertEqual(best_shift, shift)

    def test_decrypt_text(self):
        ciphertext = "KHOOR ZRUOG"
        # KHOOR -> HELLO, ZRUOG -> _O_L_
        mapping = {'K': 'H', 'H': 'E', 'O': 'L', 'R': 'O'}
        decrypted = decrypt_text(ciphertext, mapping, placeholder='_')
        self.assertEqual(decrypted, "HELLO _O_L_")

    def test_detect_mapping_conflicts(self):
        # Misal 'K' dan 'M' keduanya dipetakan ke 'E'
        mapping = {'K': 'E', 'M': 'E', 'T': 'A'}
        conflicts = detect_mapping_conflicts(mapping)
        self.assertIn('E', conflicts)
        self.assertEqual(set(conflicts['E']), {'K', 'M'})
        self.assertNotIn('A', conflicts)


if __name__ == '__main__':
    unittest.main()
