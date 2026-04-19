import json

f = open("out.json", "r", encoding="utf-8")
data = json.load(f)
f.close()

orig = [
    d for d in data
    if d.get("uni") == "Bahria_University"
]

filtered_data = [
    d for d in data
    if not (
        d.get("uni") == "Bahria_University"
    )
]

new = [
    d for d in filtered_data
    if d.get("uni") == "Bahria_University"
]

print(f"Original count: {len(orig)}")
print(f"Filtered count: {len(new)}")

print(len(data))
print(len(filtered_data))


f2 = open("out.json", "w", encoding="utf-8")
json.dump(filtered_data, f2, indent=4)
f2.close()