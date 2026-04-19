import subprocess
from pathlib import Path
import time


base_dir = Path(__file__).parent

start = time.time()
# subprocess.run(
#     ["scrapy", "crawl", "spider", "-o", "out.json"], 
#     check=True, 
#     cwd=base_dir / "Crawler"
# )

# print("First crawl completed")
# time.sleep(5)

# subprocess.run(
#     ["python","Extractor.py"],
#     check=True,
#     cwd=base_dir / "Extractor"
# )

# print("First extraction completed")
# time.sleep(5)

# subprocess.run(
#     ["scrapy", "crawl", "spider2", "-o", "out2.json"], 
#     check=True, 
#     cwd=base_dir / "Crawler"
# )

# print("Second crawl completed")
# # time.sleep(5)

# subprocess.run(
#     ["python","Extractor2.py"],
#     check=True,
#     cwd=base_dir / "Extractor"
# )

# print("Second extraction completed")
# time.sleep(5)

# subprocess.run(
#     ["scrapy", "crawl", "spider3", "-o", "out3.json"], 
#     check=True, 
#     cwd=base_dir / "Crawler"
# )

# print("Third crawl completed")
# time.sleep(5)

subprocess.run(
    ["python","Extractor3.py"],
    check=True,
    cwd=base_dir / "Extractor"
)



print("Third extraction completed")

end = time.time()
print(f"Pipeline completed in {end - start:.2f} seconds")

