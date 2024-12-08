import csv
import folium
import math

m = folium.Map(location=[40, -100], zoom_start=4)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
        math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    return distance

def create_square(lat, lon, square_size, gap_size):
    lat_min = lat - (square_size / 2) / 6371000 * 180 / math.pi
    lon_min = lon - (square_size / 2) / 6371000 * 180 / math.pi / math.cos(math.radians(lat))
    lat_max = lat + (square_size / 2) / 6371000 * 180 / math.pi
    lon_max = lon + (square_size / 2) / 6371000 * 180 / math.pi / math.cos(math.radians(lat))
    return [[lat_min, lon_min], [lat_max, lon_max]]

with open('combined.csv', 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    areas = [{'category': row['Unnamed: 0'], 'latitude': float(row['latitude']), 'longitude': float(row['longitude']), 'total_population': row['total_population']} for row in reader]

new_squares = []
gap_size = -10
square_size = 180

offsets = []
for i, area in enumerate(areas):
    offset_lat = (i // int(math.sqrt(len(areas))) * (square_size + gap_size)) / 6371000 * 180 / math.pi
    offset_lon = (i % int(math.sqrt(len(areas))) * (square_size + gap_size)) / 6371000 * 180 / math.pi / math.cos(math.radians(area['latitude']))
    offsets.append([offset_lat, offset_lon])

for i, area in enumerate(areas):
    offset_lat, offset_lon = offsets[i]
    square = create_square(area['latitude'], area['longitude'], square_size, gap_size)
    gap_half = gap_size / 2 / 6371000 * 180 / math.pi
    square_bounds = [
        [square[0][0] - gap_half, square[0][1] - gap_half / math.cos(math.radians(area['latitude']))],
        [square[1][0] + gap_half, square[1][1] + gap_half / math.cos(math.radians(area['latitude']))]
    ]
    square_folium = folium.Rectangle(bounds=square_bounds, color='black', fill_color='white', fill_opacity=0.5, weight=2, tooltip=f"Total Population: {area['total_population']}")
    m.add_child(square_folium)
    new_squares.append({
        'category': area['category'],
        'latitude_min': square[0][0],
        'longitude_min': square[0][1],
        'latitude_max': square[1][0],
        'longitude_max': square[1][1],
        'total_population': area['total_population'],
        'square_size': square_size
    })

lat_mins = [area['latitude_min'] for area in new_squares]
lon_mins = [area['longitude_min'] for area in new_squares]
lat_maxes = [area['latitude_max'] for area in new_squares]
lon_maxes = [area['longitude_max'] for area in new_squares]

m.fit_bounds([[min(lat_mins), min(lon_mins)], [max(lat_maxes), max(lon_maxes)]])
m.save('map.html')

with open('new_squares.csv', 'w', newline='') as csvfile:
    fieldnames = ['category', 'latitude_min', 'longitude_min', 'latitude_max', 'longitude_max', 'total_population', 'square_size']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(new_squares)