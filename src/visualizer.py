from typing import Dict
from src.analyzer import FrequencyAnalyzer, extract_ngrams
from src.solvers import decrypt_text, detect_mapping_conflicts, run_friedman_test

CYAN = "\033[36m"
GREEN = "\033[32m"
MAGENTA = "\033[35m"
RESET = "\033[0m"


def _colorize(text: str, color: str) -> str:
    return f"{color}{text}{RESET}"


def render_dashboard(analyzer: FrequencyAnalyzer, mapping: Dict[str, str], sort_by: str = 'freq'):
    """Menampilkan dashboard, n-gram, Friedman, dan preview terminal berwarna."""
    lang_name = "Bahasa Inggris" if analyzer.language == 'EN' else "Bahasa Indonesia"
    ioc = analyzer.calculate_ioc()
    ioc_note = analyzer.get_ioc_assessment()

    print("\n" + "=" * 85)
    print(_colorize(f" DASHBOARD ANALISIS FREKUENSI (Standar: {lang_name})", CYAN))
    print(f" Total Huruf Teks : {analyzer.total_letters} karakter")
    print(f" Indeks Koinsidensi: {ioc:.4f} -> {ioc_note}")
    print(_colorize("=" * 85, CYAN))

    if sort_by == 'freq':
        sorted_chars = analyzer.get_sorted_letters(by='freq')
    else:
        sorted_chars = analyzer.get_sorted_letters(by='alphabet')

    print(f"{'Cipher':<7} | {'Frekuensi':<9} | {'Grafik Teramati':<18} | {'Pemetaan':<10} | {'Standar Bahasa':<18}")
    print("-" * 85)
    for c in sorted_chars:
        obs = analyzer.observed_freq.get(c, 0.0)
        exp = analyzer.target_freq.get(c, 0.0)
        mapped_to = mapping.get(c, "-")
        bar_obs = "#" * int(obs * 1.5)
        bar_exp = "*" * int(exp * 1.5)
        print(f"  [{c}]   | {obs:>6.2f}%  | {bar_obs:<18} | [{c}] -> [{mapped_to}]  | {c}:{exp:>5.2f}% {bar_exp}")

    print("\n" + "-" * 85)
    print(_colorize(" BARIS PEMETAAN KARAKTER (MAPPING BAR)", CYAN))
    row_orig = " Original (Cipher) : " + " ".join(f"[{c}]" for c in sorted_chars)
    row_maps = " Maps to  (Plain)  : " + " ".join(f"[{mapping.get(c, ' ')}]" for c in sorted_chars)
    print(row_orig)
    print(row_maps)

    conflicts = detect_mapping_conflicts(mapping)
    if conflicts:
        print("\n" + _colorize(" [PERINGATAN KONFLIK PEMETAAN]", MAGENTA))
        for plain, cipher_list in conflicts.items():
            print(f"  ! Karakter plain '{plain}' dipetakan dari beberapa cipher: {', '.join(cipher_list)}")

    bigrams = extract_ngrams(analyzer.ciphertext, 2)
    trigrams = extract_ngrams(analyzer.ciphertext, 3)
    print("\n" + _colorize(" ANALISIS N-GRAM", CYAN))
    print(" Bigram :", " ".join(f"{key}={value}" for key, value in sorted(bigrams.items(), key=lambda item: (-item[1], item[0]))[:12]))
    print(" Trigram :", " ".join(f"{key}={value}" for key, value in sorted(trigrams.items(), key=lambda item: (-item[1], item[0]))[:12]))

    print("\n" + _colorize(" TEST FRIEDMAN (VIGENERE)", CYAN))
    for key_length, result in run_friedman_test(analyzer.ciphertext, max_key_length=10).items():
        if key_length <= 10:
            print(f" k={key_length}: IoC rata-rata {result['average_ioc']:.4f}")

    decrypted_preview = decrypt_text(analyzer.ciphertext, mapping)
    print("\n" + "-" * 85)
    print(_colorize(" TEKS DEKRIPSI SAAT INI", GREEN))
    print(" Karakter belum dipetakan ditampilkan sebagai '_':")
    print(decrypted_preview)
    print("-" * 85)
