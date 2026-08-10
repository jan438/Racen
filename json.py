import json
line_items=[]
for q in selectedcoords:
    longtitude = q[0]
    latitude= q[1]

    myjson3 = {
                'longtitude': longtitude,
                'latitude': latitude
            }
    line_items.append(myjson3)
print(json.dumps(line_items))