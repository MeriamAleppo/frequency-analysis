import random
import string
from collections import Counter
from typing import Dict, List, Tuple, Optional
from src.constants import FREQ_ENGLISH, FREQ_INDONESIAN


NGRAM_MODELS = {
    "EN": {
        "THE": 0.180, "AND": 0.150, "ING": 0.140, "TION": 0.110,
        "QUICK": 0.090, "BROWN": 0.080, "FOX": 0.070, "JUMPS": 0.065,
        "OVER": 0.073, "LAZY": 0.050, "DOG": 0.055,
        "TH": 0.170, "HE": 0.160, "IN": 0.110, "ER": 0.110,
        "AN": 0.100, "RE": 0.095, "ON": 0.095, "AT": 0.090,
    },
    "ID": {
        "DAN": 0.110, "YANG": 0.100, "KAND": 0.080, "KON": 0.070,
        "TAN": 0.080, "DI": 0.110, "ME": 0.090, "AN": 0.090,
        "PADA": 0.100, "KATA": 0.090, "KARAK": 0.060,
    },
}


def calculate_chi_squared(observed_counts: Counter, total_letters: int, target_freq: Dict[str, float]) -> float:
    """Menghitung statistik uji Chi-Square antara frekuensi teramati dan ekspektasi target."""
    if total_letters == 0:
        return float('inf')

    chi2 = 0.0
    for ch in string.ascii_uppercase:
        observed_pct = (observed_counts[ch] / total_letters) * 100
        expected_pct = target_freq.get(ch, 0.01)
        chi2 += ((observed_pct - expected_pct) ** 2) / expected_pct
    return chi2


def auto_solve_caesar(ciphertext: str, target_freq: Dict[str, float]) -> Tuple[int, float, Dict[str, str]]:
    """
    Mencari pergeseran Caesar terbaik (0-25) menggunakan minimasi skor Chi-Square.
    Mengembalikan: (best_shift, lowest_chi2, mapping)
    """
    best_shift = 0
    lowest_chi2 = float('inf')

    for shift in range(26):
        decrypted_letters = []
        for c in ciphertext:
            if c.isalpha():
                base = ord('A') if c.isupper() else ord('a')
                decrypted_letters.append(chr((ord(c) - base - shift) % 26 + ord('A')))

        total = len(decrypted_letters)
        if total == 0:
            continue

        counts = Counter(decrypted_letters)
        chi2 = calculate_chi_squared(counts, total, target_freq)

        if chi2 < lowest_chi2:
            lowest_chi2 = chi2
            best_shift = shift

    mapping = {
        c: chr((ord(c) - ord('A') - best_shift) % 26 + ord('A'))
        for c in string.ascii_uppercase
    }
    return best_shift, lowest_chi2, mapping


def auto_assign_by_frequency(observed_freq: Dict[str, float], target_freq: Dict[str, float]) -> Dict[str, str]:
    """Memetakan huruf secara 1:1 berdasarkan urutan frekuensi tertinggi teramati ke target."""
    sorted_cipher = sorted(
        string.ascii_uppercase,
        key=lambda x: observed_freq.get(x, 0.0),
        reverse=True
    )
    sorted_target = sorted(
        string.ascii_uppercase,
        key=lambda x: target_freq.get(x, 0.0),
        reverse=True
    )
    return {c: p for c, p in zip(sorted_cipher, sorted_target)}


def detect_mapping_conflicts(mapping: Dict[str, str]) -> Dict[str, List[str]]:
    """
    Mendeteksi konflik pemetaan (ketika lebih dari satu huruf cipher dipetakan ke huruf plain yang sama).
    Mengembalikan: {plain_char: [cipher_char_1, cipher_char_2, ...]}
    """
    reverse_map: Dict[str, List[str]] = {}
    for c, p in mapping.items():
        if p and p != '-':
            reverse_map.setdefault(p.upper(), []).append(c.upper())

    return {p: c_list for p, c_list in reverse_map.items() if len(c_list) > 1}


def decrypt_text(ciphertext: str, mapping: Dict[str, str], placeholder: str = '_') -> str:
    """Mendekripsi ciphertext menggunakan tabel pemetaan."""
    res = []
    for ch in ciphertext:
        if ch.isalpha():
            up = ch.upper()
            if up in mapping and mapping[up]:
                mapped = mapping[up]
                res.append(mapped if ch.isupper() else mapped.lower())
            else:
                res.append(placeholder)
        else:
            res.append(ch)
    return "".join(res)


def calculate_fitness(text: str, language: str = "EN") -> float:
    """Skor fitness n-gram untuk teks plaintext berdasarkan bahasa target."""
    normalized = text.upper()
    model = NGRAM_MODELS.get(language.upper(), NGRAM_MODELS["EN"])
    score = 0.0
    for pattern, weight in model.items():
        occurrences = normalized.count(pattern)
        score += occurrences * weight
    return score


def hill_climb_substitution(ciphertext: str, language: str = "EN", iterations: int = 500, seed: int = 0) -> Dict[str, str]:
    """Optimasi pemetaan monoalphabetik dengan hill climbing dan n-gram fitness."""
    rng = random.Random(seed)
    alphabet = list(string.ascii_uppercase)
    cipher_letters = [ch.upper() for ch in ciphertext if ch.isalpha()]
    if not cipher_letters:
        return {ch: ch for ch in alphabet}

    observed = Counter(cipher_letters)
    target = FREQ_ENGLISH if language.upper() == "EN" else FREQ_INDONESIAN
    sorted_cipher = sorted(alphabet, key=lambda ch: observed[ch], reverse=True)
    sorted_target = sorted(alphabet, key=lambda ch: target[ch], reverse=True)
    mapping = {cipher: plain for cipher, plain in zip(sorted_cipher, sorted_target)}

    current = decrypt_text(ciphertext, mapping)
    current_score = calculate_fitness(current, language)
    best_mapping = dict(mapping)
    best_score = current_score
    for _ in range(iterations):
        first, second = rng.sample(alphabet, 2)
        candidate = dict(mapping)
        candidate[first] = mapping[second]
        candidate[second] = mapping[first]
        candidate_text = decrypt_text(ciphertext, candidate)
        candidate_score = calculate_fitness(candidate_text, language)
        if candidate_score >= current_score or rng.random() < 0.03:
            mapping = candidate
            current_score = candidate_score
            if candidate_score > best_score:
                best_mapping = dict(candidate)
                best_score = candidate_score
    return best_mapping


def _ioc_for_key_length(text: str, key_length: int) -> float:
    """Menghitung rata-rata IoC untuk seluruh irisan berdasarkan key length."""
    values = []
    for offset in range(key_length):
        letters = [ch.upper() for ch in text if ch.isalpha()][offset::key_length]
        if len(letters) < 2:
            continue
        total = len(letters)
        counts = Counter(letters)
        values.append(sum(count * (count - 1) for count in counts.values()) / (total * (total - 1)))
    return sum(values) / len(values) if values else 0.0


def run_friedman_test(ciphertext: str, max_key_length: int = 10) -> Dict[int, Dict[str, float]]:
    """Menghitung IoC rata-rata untuk k = 1..max_key_length."""
    return {
        key_length: {
            "average_ioc": _ioc_for_key_length(ciphertext, key_length),
            "key_length": key_length,
        }
        for key_length in range(1, max_key_length + 1)
    }


def recover_vigenere_keyword(ciphertext: str, key_length: int, target_freq: Dict[str, float]) -> Dict[str, object]:
    """Mereksi setiap irisan Vigenere dan mengembalikan kunci yang paling cocok."""
    letters = [ch.upper() for ch in ciphertext if ch.isalpha()]
    keyword = []
    for offset in range(key_length):
        segment = letters[offset::key_length]
        best_shift = 0
        best_chi2 = float("inf")
        for shift in range(26):
            decrypted = [chr((ord(ch) - ord("A") - shift) % 26 + ord("A")) for ch in segment]
            chi2 = calculate_chi_squared(Counter(decrypted), len(decrypted), target_freq)
            if chi2 < best_chi2:
                best_chi2 = chi2
                best_shift = shift
        keyword.append(chr(ord("A") + best_shift))
    return {"keyword": "".join(keyword), "chi_squared": min(
        calculate_chi_squared(Counter(
            chr((ord(ch) - ord("A") - shift) % 26 + ord("A")) for ch in letters
        ), len(letters), target_freq)
        for shift in range(26)
    )}
