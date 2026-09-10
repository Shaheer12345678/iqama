"""PyInstaller's entry script.

Deliberately outside the iqama package and free of relative imports --
PyInstaller's static analysis handles a plain "import iqama.main" far
more reliably as the frozen app's __main__ than a script that itself
uses package-relative imports.
"""
import sys

from iqama.main import main

if __name__ == "__main__":
    sys.exit(main())
