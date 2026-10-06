#!/usr/bin/env python3
"""
Frequency Analysis & Classical Cipher Toolkit
Titik masuk utama untuk menjalankan aplikasi secara interaktif.
"""
import sys
from src.cli import run_interactive_app

if __name__ == "__main__":
    try:
        run_interactive_app()
    except KeyboardInterrupt:
        print("\n\nProgram dihentikan oleh pengguna.")
        sys.exit(0)
