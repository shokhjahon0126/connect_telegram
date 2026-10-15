"""Direct entry point to run connect-telegram using standard Python venv."""
import sys
from pathlib import Path

# Add src/ to sys.path so connect_telegram is importable directly
src_dir = Path(__file__).resolve().parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from connect_telegram.main import main

if __name__ == "__main__":
    main()
