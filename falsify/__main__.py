"""Enable `python -m falsify` — the documented entry point after the package
restructure (root ``falsify.py`` was removed). Delegates to ``falsify.cli.main``
so the console-script entry point and ``-m`` form stay in sync.
"""
from falsify.cli import main

if __name__ == "__main__":
    main()
