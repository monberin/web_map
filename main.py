import folium
import pandas
import geopy
import random
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from geopy.extra.rate_limiter import RateLimiter

geolocator = Nominatim(user_agent="specify_your_app_name_here", timeout=100)
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=0.1, max_retries=1)


def read_file(inp_year):
    data = pandas.read_csv(
        "locations.csv", error_bad_lines=False, warn_bad_lines=False)
    movie = data['movie']
    year = data['year']
    location = data['location']
    loc_dict = {}
    counter = 0
    for m, y, l in zip(movie, year, location):
        try:
            if int(y) == int(inp_year):
                counter += 1
                if l not in loc_dict:
                    loc_dict[l] = []
                loc_dict[l].append(m.strip())
                if counter == 600:
                    break
        except ValueError:
            continue
    return loc_dict


def distance_sorted(locations_d, entered_lat, entered_long):

    points = []
    for loc in locations_d:
        location = geolocator.geocode(loc)
        if location is not None:
            points.append(
                (loc, locations_d[loc], location.latitude, location.longitude))

    def geodistance(loc_tupl):
        return geodesic((entered_lat, entered_long),
                        (loc_tupl[2], loc_tupl[3]))

    points.sort(key=geodistance)
    return points[:10]


def marking_locations(location_list):

    fg_film = folium.FeatureGroup(name="Films")

    for loc in location_list:
        fg_film.add_child(folium.Marker(location=[loc[2], loc[3]],
                                        popup=loc[1][random.randint(0, len(loc[1])-1)]+' was filmed here',
                                        icon=folium.Icon(icon='film')))
    return fg_film


def population_layer():
    fg_pp = folium.FeatureGroup(name="Population",)

    fg_pp.add_child(folium.GeoJson(data=open('world.json', 'r',
                                             encoding='utf-8-sig').read(),
                                   style_function=lambda x: {'color': '#330033', 'fillOpacity': 0.5, 'fillColor': '#4393C3'
                                                             if x['properties']['POP2005'] < 10000000
                                                             else '#FDDBC7' if 10000000 <= x['properties']['POP2005'] < 25000000
                                                             else '#F4A582' if 25000000 <= x['properties']['POP2005'] < 50000000
                                                             else '#D6604D' if 50000000 <= x['properties']['POP2005'] < 100000000
                                                             else '#B2182B'}))
    return fg_pp


if __name__ == "__main__":
    while True:
        try:
            year = input(
                'Please enter a year you would like to have a map for: ')
            year = int(year)
            coordinates = input(
                'Please enter your location (format: lat, long): ')
            coord_list = coordinates.split(',')
            lat, lon = float(coord_list[0].strip()), float(
                coord_list[1].strip())
            break
        except (ValueError, IndexError):
            print('wrong value was entered.')
            continue
    print('generating map...')
    map = folium.Map(location=[lat, lon], zoom_start=10)
    dict_locations = read_file(year)
    distance_list = distance_sorted(dict_locations, lat, lon)
    print('adding marks...')
    marking = marking_locations(distance_list)
    map.add_child(marking)
    print('adding population...')
    map.add_child(population_layer())
    map.add_child(folium.LayerControl())
    map.save('Map.html')
    print('map generated. please take a look at "Map.html"')
