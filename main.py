import sys
from pathlib import Path

# shortcut biar bisa dijalankan lewat "python main.py" atau "uv run main.py"
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pipeline import main

if __name__ == "__main__":
    main()
