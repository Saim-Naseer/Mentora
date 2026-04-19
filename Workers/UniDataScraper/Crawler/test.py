# import json
# from pathlib import Path

# filepath = Path("pdf_urls.json")
# f = open(filepath, "r", encoding="utf-8")
# data = json.load(f)


# urls = [
#     "https://www.iub.edu.pk/uploads/2340/admission-fall-2025/fee-fall-2025/1752586420-revised-fee-structure-fall-2025-for-new-intake-only.pdf",
#     "https://www.iub.edu.pk/uploads/2319/fee-structure-old-fall-2024/1752040572-1726209281-proposal-for-fee-reduction-in-under-performing-programs-sub-campuses-bahawalnagar-and-rahimyar-khan.pdf",
#     "https://www.iub.edu.pk/uploads/2340/iub-adm/new-updated-fall-2024/1726209281-revised-fee-structure-of-various-programsdepartments.pdf",
#     "https://www.iub.edu.pk/uploads/2340/iub-adm/new-updated-fall-2024/1726211211-10-fee-concession-on-full-fee-for-students-of-affiliated-colleges-and-25-concession-of-alumni-students-1.pdf",
#     "https://www.iub.edu.pk/uploads/2340/academic-calendar-2025-26/1744722120-academic-calendar-2025-2026.pdf"
# ]

# for u in urls:
#     uni="Unknown"
#     u=u.replace(" ","")
#     count=0
#     for s in u:
#         if count==2:
#             continue
#         if count==1 and s!='/':
#             continue
#         if s=="/":
#             count+=1
#         u=u[1:]
        
#     for d in data:

#         temp = d["link"].replace(" ","")
#         if u in temp:
#             uni = d["uni"]

#     print(uni)
from Crawler.utils.UniLinkMap import UniLinkMap as UniLinkmap


print(len(UniLinkmap.values()))