import math

def calculate_distance_str(lat1, lon1, lat2, lon2):
    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    kpdl = 111.1

    kpdlo1 = 111.3 * math.cos(math.radians(lat1))
    kpdlo2 = 111.3 * math.cos(math.radians(lat2))

    ab = delta_lat * kpdl

    bc = delta_lon * kpdlo2
    ad = delta_lon * kpdlo1

    hdb = abs(ad - bc) / 2
    hp = ab
    height = math.sqrt(hp ** 2 - hdb ** 2)

    hd = abs(ad - hdb)
    distance = math.sqrt(height ** 2 + hd ** 2)

    return distance

def calculate_distance_tuple(coords, coords1):
    lat1,lon1 = coords
    lat2,lon2 = coords1
    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    kpdl = 111.1

    kpdlo1 = 111.3 * math.cos(math.radians(lat1))
    kpdlo2 = 111.3 * math.cos(math.radians(lat2))

    ab = delta_lat * kpdl

    bc = delta_lon * kpdlo2
    ad = delta_lon * kpdlo1

    hdb = abs(ad - bc) / 2
    hp = ab
    height = math.sqrt(hp ** 2 - hdb ** 2)

    hd = abs(ad - hdb)
    distance = math.sqrt(height ** 2 + hd ** 2)

    return distance