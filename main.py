import json
from src.measurements import area, bbox
from src.booleans import is_valid

with open("./test-geojson/example-mp.json") as file:
    obj = json.load(file)

    print(f"\nCALLING AREA WITH MULTIPOLYGON")
    print(area(obj))

with open("./test-geojson/maine-poly.json") as file:
    obj = json.load(file)

    print(f"\nCALLING AREA WITH POLYGON")
    print(area(obj))

print("\n")
print(f"calling bbox {bbox()}")
print(f"calling is_valid {is_valid()}")
