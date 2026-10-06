import os
import copy
from typing import Dict, List
from src.analyzer import FrequencyAnalyzer
from src.solvers import (
    auto_solve_caesar,
    auto_assign_by_frequency,
    decrypt_text,
    hill_climb_substitution,
    recover_vigenere_keyword,
    run_friedman_test,
)
from src.visualizer import render_dashboard

DEFAULT_SAMPLE = (
    "Npd ulk vy krg lycrpdkgj epctopkgda un krg lynparvuypebg gyj un krg ogakgdy "
    "aqvdpb pds un krg Mpbpfi bvga p aspbb lydgmpdjgj igbbuo aly..."
)


class CLISession:
    """Mengelola sesi interaktif CLI analisis frekuensi."""
    def __init__(self, ciphertext: str, language: str = 'EN'):
        self.analyzer = FrequencyAnalyzer(ciphertext, language=language)
        self.mapping: Dict[str, str] = {}
        self.history: List[Dict[str, str]] = []

    def save_state(self):
        """Menyimpan snapshot pemetaan untuk fungsi undo."""
        self.history.append(copy.deepcopy(self.mapping))
        if len(self.history) > 20:
            self.history.pop(0)

    def undo(self) -> bool:
        """Mengembalikan pemetaan ke state sebelumnya."""
        if not self.history:
            return False
        self.mapping = self.history.pop()
        return True

    def set_manual_mapping(self, cipher_str: str, plain_str: str):
        self.save_state()
        c_clean = [ch.upper() for ch in cipher_str if ch.isalpha()]
        p_clean = [ch.upper() for ch in plain_str if ch.isalpha()]
        for c, p in zip(c_clean, p_clean):
            self.mapping[c] = p

    def reset_mapping(self):
        self.save_state()
        self.mapping = {}


def run_interactive_app():
    print("=" * 70)
    print(" TOOLKIT ANALISIS FREKUENSI & KRIPTANALISIS KLASIK")
    print("=" * 70)

    print("Pilihan sumber ciphertext:")
    print(" 1. Gunakan sampel bawaan (Substitusi)")
    print(" 2. Masukkan teks langsung via terminal")
    print(" 3. Muat teks dari berkas (.txt)")
    pilih_sumber = input("Pilih [1-3] (default 1): ").strip()

    ciphertext = DEFAULT_SAMPLE
    if pilih_sumber == '2':
        inp = input("Masukkan Ciphertext: ").strip()
        if inp:
            ciphertext = inp
    elif pilih_sumber == '3':
        filepath = input("Masukkan path berkas .txt (cth: data/samples/sample_caesar.txt): ").strip()
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                ciphertext = f.read().strip()
            print(f"[INFO] Berkas berhasil dimuat ({len(ciphertext)} karakter).")
        else:
            print(f"[PERINGATAN] Berkas '{filepath}' tidak ditemukan. Menggunakan sampel bawaan.")

    lang = input("Pilih bahasa acuan ([EN] English / [ID] Indonesia, default EN): ").strip().upper()
    if lang not in ['EN', 'ID']:
        lang = 'EN'

    session = CLISession(ciphertext, language=lang)
    render_dashboard(session.analyzer, session.mapping, sort_by='freq')

    while True:
        print("\nMENU KONTROL:")
        print(" 1. Tampilkan Dashboard (Urut Frekuensi - 'By %')")
        print(" 2. Tampilkan Dashboard (Urut Alfabet - 'A to Z')")
        print(" 3. Mode Caesar Cipher (Otomatis uji Chi-Square)")
        print(" 4. Mode Substitusi Acak (Auto-assign urutan frekuensi)")
        print(" 5. Pemetaan Huruf Manual (Assign cipher -> plain)")
        print(" 6. Batalkan Pemetaan Terakhir (Undo)")
        print(" 7. Reset Semua Pemetaan")
        print(" 8. Ganti Bahasa Acuan (EN/ID)")
        print(" 9. Simpan Hasil Dekripsi ke Berkas (.txt)")
        print("10. Hill Climbing Substitusi Acak")
        print("11. Analisis Vigenere + Friedman")
        print(" 0. Keluar")

        pilihan = input("\nPilih menu [0-9]: ").strip()

        if pilihan == '1':
            render_dashboard(session.analyzer, session.mapping, sort_by='freq')
        elif pilihan == '2':
            render_dashboard(session.analyzer, session.mapping, sort_by='alphabet')
        elif pilihan == '3':
            session.save_state()
            best_shift, chi2, mapping = auto_solve_caesar(session.analyzer.ciphertext, session.analyzer.target_freq)
            session.mapping = mapping
            print(f"\n[SUKSES] Caesar Shift Terdeteksi: {best_shift} (Skor Chi-Square: {chi2:.2f})")
            render_dashboard(session.analyzer, session.mapping, sort_by='freq')
        elif pilihan == '4':
            session.save_state()
            session.mapping = auto_assign_by_frequency(session.analyzer.observed_freq, session.analyzer.target_freq)
            print("\n[SUKSES] Pemetaan awal berdasarkan urutan frekuensi diterapkan.")
            render_dashboard(session.analyzer, session.mapping, sort_by='freq')
        elif pilihan == '5':
            print("\nContoh input satu huruf: Cipher: K | Plain: T")
            print("Contoh input kata sekaligus: Cipher: KRG | Plain: THE")
            c_input = input("Masukkan huruf Cipher : ").strip()
            p_input = input("Dipetakan ke Plaintext: ").strip()
            if c_input and p_input:
                session.set_manual_mapping(c_input, p_input)
                print("[SUKSES] Pemetaan diperbarui!")
            else:
                print("[PERINGATAN] Input tidak boleh kosong.")
            render_dashboard(session.analyzer, session.mapping, sort_by='freq')
        elif pilihan == '6':
            if session.undo():
                print("\n[SUKSES] Langkah pemetaan sebelumnya berhasil dibatalkan (Undo).")
            else:
                print("\n[INFO] Tidak ada riwayat pemetaan sebelumnya.")
            render_dashboard(session.analyzer, session.mapping, sort_by='freq')
        elif pilihan == '7':
            session.reset_mapping()
            print("\n[SUKSES] Seluruh pemetaan berhasil direset.")
            render_dashboard(session.analyzer, session.mapping, sort_by='freq')
        elif pilihan == '8':
            curr = session.analyzer.language
            new_lang = 'ID' if curr == 'EN' else 'EN'
            session.analyzer.set_language(new_lang)
            print(f"\n[SUKSES] Bahasa acuan diubah ke {'Bahasa Indonesia' if new_lang == 'ID' else 'Bahasa Inggris'}.")
            render_dashboard(session.analyzer, session.mapping, sort_by='freq')
        elif pilihan == '9':
            out_path = input("Masukkan nama berkas simpan (default: hasil_dekripsi.txt): ").strip()
            if not out_path:
                out_path = "hasil_dekripsi.txt"
            decrypted = decrypt_text(session.analyzer.ciphertext, session.mapping)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write("=== HASIL DEKRIPSI ===\n")
                f.write(decrypted + "\n\n")
                f.write("=== TABEL PEMETAAN ===\n")
                for c in sorted(session.mapping.keys()):
                    f.write(f"{c} -> {session.mapping[c]}\n")
            print(f"\n[SUKSES] Hasil dekripsi dan pemetaan berhasil disimpan ke '{out_path}'.")
        elif pilihan == '10':
            session.save_state()
            session.mapping = hill_climb_substitution(session.analyzer.ciphertext, session.analyzer.language)
            print("\n[SUKSES] Optimasi pemetaan Hill Climbing berbasis n-gram selesai.")
            render_dashboard(session.analyzer, session.mapping, sort_by='freq')
        elif pilihan == '11':
            friedman = run_friedman_test(session.analyzer.ciphertext, max_key_length=10)
            print("\nANALISIS FRIEDMAN VIGENERE")
            for key_length, result in friedman.items():
                print(f" k={key_length}: IoC rata-rata {result['average_ioc']:.4f}")
            key_length = max(friedman, key=lambda k: friedman[k]["average_ioc"])
            recovered = recover_vigenere_keyword(session.analyzer.ciphertext, key_length, session.analyzer.target_freq)
            print(f"[SUKSES] Kandidat kunci statistik: {recovered['keyword']} (Chi-Square: {recovered['chi_squared']:.2f})")
            render_dashboard(session.analyzer, session.mapping, sort_by='freq')
        elif pilihan == '0':
            print("Selesai. Selamat belajar kriptografi!")
            break
        else:
            print("Pilihan tidak valid, silakan masukkan angka 0 - 9.")
