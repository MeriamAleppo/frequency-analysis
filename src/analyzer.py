import string
from collections import Counter
from typing import Dict, List, Optional
from src.constants import FREQ_ENGLISH, FREQ_INDONESIAN, EXPECTED_IOC


def extract_ngrams(text: str, n: int) -> Dict[str, int]:
    """Ekstrak n-gram, mengabaikan karakter non-huruf, dan menghitung kemunculan."""
    if n < 1:
        raise ValueError("n harus lebih besar atau sama dengan 1")
    letters = [ch.upper() for ch in text if ch.isalpha()]
    return Counter("".join(letters[index:index + n]) for index in range(len(letters) - n + 1))


class FrequencyAnalyzer:
    """
    Menganalisis frekuensi kemunculan huruf dan metrik statistik pada teks sandi.
    """
    def __init__(self, ciphertext: str, language: str = 'EN'):
        self.ciphertext = ciphertext
        self.language = language.upper() if language.upper() in ('EN', 'ID') else 'EN'
        self.target_freq = FREQ_ENGLISH if self.language == 'EN' else FREQ_INDONESIAN
        self.counts: Counter = Counter()
        self.total_letters: int = 0
        self.observed_freq: Dict[str, float] = {}
        self.ngram_counts: Dict[str, int] = {}
        self.ngram_size: int = 0
        self.total_ngrams: int = 0
        self.calculate_frequencies()

    def set_language(self, language: str):
        """Mengubah bahasa acuan analisis ('EN' atau 'ID')."""
        self.language = language.upper() if language.upper() in ('EN', 'ID') else 'EN'
        self.target_freq = FREQ_ENGLISH if self.language == 'EN' else FREQ_INDONESIAN

    def set_ciphertext(self, ciphertext: str):
        """Memperbarui ciphertext yang sedang dianalisis."""
        self.ciphertext = ciphertext
        self.calculate_frequencies()

    def calculate_ngrams(self, size: int):
        """Menghitung kemunculan bigram/trigram dari ciphertext saat ini."""
        self.ngram_size = size
        self.ngram_counts = dict(extract_ngrams(self.ciphertext, size))
        self.total_ngrams = sum(self.ngram_counts.values())
        return self.ngram_counts

    def calculate_frequencies(self):
        """Menghitung frekuensi kemunculan setiap huruf A-Z."""
        letters_only = [c.upper() for c in self.ciphertext if c.isalpha()]
        self.total_letters = len(letters_only)
        self.counts = Counter(letters_only)

        if self.total_letters > 0:
            self.observed_freq = {
                c: (self.counts[c] / self.total_letters) * 100 for c in string.ascii_uppercase
            }
        else:
            self.observed_freq = {c: 0.0 for c in string.ascii_uppercase}

    def calculate_ioc(self) -> float:
        """
        Menghitung Index of Coincidence (IoC).
        IoC = sum(f_i * (f_i - 1)) / (N * (N - 1))
        Nilai ~0.065-0.074 mengindikasikan monoalfabetik (bhs alami).
        Nilai ~0.038 mengindikasikan polialfabetik (acak).
        """
        n = self.total_letters
        if n <= 1:
            return 0.0
        numerator = sum(count * (count - 1) for count in self.counts.values())
        return numerator / (n * (n - 1))

    def get_ioc_assessment(self) -> str:
        """Memberikan taksiran tipe cipher berdasarkan nilai IoC."""
        ioc = self.calculate_ioc()
        expected = EXPECTED_IOC.get(self.language, 0.0667)
        if ioc >= 0.055:
            return f"Monoalfabetik (Teks alami terdeteksi, IoC: {ioc:.4f}, Acuan: {expected:.4f})"
        else:
            return f"Polialfabetik atau Teks Terlalu Pendek (IoC: {ioc:.4f}, Acik/Poly: ~0.0385)"

    def get_sorted_letters(self, by: str = 'freq', reverse: bool = True) -> List[str]:
        """Mengembalikan daftar huruf terurut berdasarkan frekuensi atau alfabet."""
        if by == 'freq':
            return sorted(
                string.ascii_uppercase,
                key=lambda x: self.observed_freq[x],
                reverse=reverse
            )
        return list(string.ascii_uppercase)
