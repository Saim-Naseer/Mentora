import subprocess
from pathlib import Path

base_dir = Path(__file__).parent

subprocess.run(["python", "UniLister.py"], check=True, cwd=base_dir / "Crawler" / "UniList")

subprocess.run(
    ["scrapy", "crawl", "spider", "-o", "data.json"], 
    check=True, 
    cwd=base_dir / "Crawler"
)

subprocess.run(
    ["python", "csvGenerator.py"], 
    check=True, 
    cwd=base_dir / "csvGenerator"
)

print("Pipeline completed!")