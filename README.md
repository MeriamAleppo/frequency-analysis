# Toolkit Analisis Frekuensi & Kriptanalisis Klasik

Projek ini adalah perangkat bantu interaktif berbasis terminal (CLI) untuk menganalisis frekuensi kemunculan huruf pada teks tersandi (*ciphertext*) dan membantu proses kriptanalisis sandi monoalfabetik klasik seperti **Caesar Cipher** dan **Monoalphabetic Substitution Cipher**.

Projek ini disusun secara modular dan terstruktur untuk pelaporan aktivitas mingguan (*weekly activities*).

---

## Fitur Utama

1. **Dashboard Statistik Frekuensi & Visualisasi Terminal:**
   - Perhitungan persentase kemunculan huruf A–Z pada teks terenkripsi.
   - Grafik batang berbasis karakter ASCII untuk membandingkan frekuensi teramati dengan standar bahasa.
   - Opsi pengurutan data berdasarkan frekuensi tertinggi (`By %`) atau urutan alfabet (`A to Z`).
2. **Dukungan Dwi-Bahasa (Bilingual):**
   - Mendukung standar distribusi frekuensi Bahasa Inggris (EN) dan Bahasa Indonesia (ID).
3. **Index of Coincidence (IoC):**
   - Menghitung nilai IoC teks untuk membedakan apakah teks sandi bersifat monoalfabetik (bahasa alami) atau polialfabetik/acak.
4. **Pemecah Sandi Caesar Otomatis (Chi-Square Test):**
   - Mencari nilai pergeseran (*shift* 0–25) terbaik secara otomatis dengan meminimalkan statistik uji Chi-Square.
5. **Pemetaan Huruf Interaktif (Substitusi Manual & Otomatis):**
   - Pemetaan otomatis awal berdasarkan urutan kecocokan frekuensi.
   - Pemetaan manual per huruf (`K -> T`) maupun kata langsung (`KRG -> THE`).
   - Deteksi konflik pemetaan (*collision warning*) jika dua huruf cipher berbeda dipetakan ke huruf plain yang sama.
   - Fitur **Undo** untuk membatalkan langkah pemetaan sebelumnya.
6. **Live Preview & Manajemen Berkas (I/O):**
   - Preview real-time hasil dekripsi dengan placeholder (`_`) untuk huruf yang belum terpetakan.
   - Opsi memuat ciphertext dari berkas `.txt` serta mengekspor hasil dekripsi dan tabel kunci pemetaan ke berkas teks.

---

## Struktur Repositori

```text
frequency-analysis-cipher/
│
├── data/
│   └── samples/                  # Berkas sampel ciphertext untuk uji coba
│       ├── sample_caesar_en.txt
│       ├── sample_caesar_id.txt
│       └── sample_substitution.txt
│
├── src/                          # Modul kode sumber utama
│   ├── __init__.py
│   ├── constants.py              # Tabel frekuensi bahasa (EN, ID) & acuan IoC
│   ├── analyzer.py               # Logika perhitungan frekuensi & Index of Coincidence
│   ├── solvers.py                # Algoritma Chi-Square, solver Caesar, & deteksi konflik
│   ├── visualizer.py             # Rendering tabel, grafik ASCII, dan preview dekripsi
│   └── cli.py                    # Pengendali alur interaktif CLI dan riwayat (undo)
│
├── tests/                        # Pengujian unit otomatis (Unit Testing)
│   ├── __init__.py
│   ├── test_analyzer.py          # Pengujian akurasi frekuensi dan formula IoC
│   └── test_solvers.py           # Pengujian solver Caesar dan fungsi dekripsi
│
├── .gitignore                    # Mengabaikan cache python, venv, dan file sementara
├── requirements.txt              # Daftar dependensi pengembangan
├── main.py                       # Titik masuk utama eksekusi program
└── README.md                     # Dokumentasi komprehensif projek
```

---

## Panduan Penggunaan

### 1. Prasyarat
- Python versi 3.8 atau yang lebih baru.
- Aplikasi inti menggunakan pustaka standar Python (*built-in*), sehingga tidak memerlukan instalasi pustaka pihak ketiga.

### 2. Menjalankan Program
Jalankan perintah berikut di direktori `frequency-analysis-cipher`:

```bash
python main.py
```

Setelah dijalankan, Anda dapat memilih:
- Menggunakan teks sampel bawaan,
- Memasukkan teks secara manual di terminal, atau
- Memuat berkas `.txt` dari folder `data/samples/`.

### 3. Menjalankan Pengujian Unit (*Unit Tests*)
Untuk memverifikasi kebenaran fungsi kalkulasi frekuensi, rumus IoC, dan algoritma dekripsi:

```bash
python -m unittest discover -s tests
```

---

## Konsep Teori Kriptografi

### 1. Distribusi Frekuensi Huruf
Pada bahasa alami, huruf tidak muncul dengan probabilitas yang sama:
- **Bahasa Inggris:** Huruf **E** paling dominan (~12.02%), diikuti oleh **T**, **A**, dan **O**.
- **Bahasa Indonesia:** Huruf **A** sangat dominan (~18.25%), diikuti oleh **N** (~9.77%), **E**, dan **I**.

Pada sandi substitusi monoalfabetik, pola distribusi frekuensi tidak hancur; identitas huruf hanya bertukar peran.

### 2. Uji Chi-Square
Untuk memecahkan sandi Caesar secara otomatis, dilakukan pengujian untuk setiap kemungkinan pergeseran shift 0 sampai 25. Nilai Chi-Square terendah menunjukkan pergeseran yang paling mendekati distribusi bahasa alami.

### 3. Index of Coincidence (IoC)
Index of Coincidence mengukur probabilitas bahwa dua huruf yang dipilih secara acak dari suatu teks adalah identik:
- Teks bahasa Inggris monoalfabetik: IoC ~ 0.0667
- Teks bahasa Indonesia monoalfabetik: IoC ~ 0.0740
- Teks acak / Sandi Polialfabetik (seperti Vigenere): IoC ~ 0.0385

---

## Rencana Pengembangan (Roadmap)

- [ ] Analisis n-gram (Bigram dan Trigram) untuk mendeteksi kata-kata umum (misal: *THE*, *AND*, *DAN*, *YANG*).
- [ ] Implementasi algoritma heuristik *Hill Climbing* berbasis n-gram score untuk memecahkan sandi substitusi acak secara otomatis.
- [ ] Antarmuka web modern menggunakan Streamlit.
