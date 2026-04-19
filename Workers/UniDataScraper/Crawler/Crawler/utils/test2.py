from pathlib import Path

path = Path(__file__).parent.parent.parent.parent / "Crawler" / "cleaned_pages"

folders = [f for f in path.iterdir() if f.is_dir()]

print([str(f).split("\\")[-1] for f in folders])