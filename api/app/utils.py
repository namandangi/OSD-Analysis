import numpy
import time
import numpy as np

# from colormath.color_objects import sRGBColor, LabColor
# from colormath.color_conversions import convert_color
# from colormath.color_diff import delta_e_cie2000
import math


def patch_asscalar(a):
    return a.item()


setattr(numpy, "asscalar", patch_asscalar)


R = 6371


def lab2rgb(lab):
    y = (lab[0] + 16) / 116
    x = lab[1] / 500 + y
    z = y - lab[2] / 200
    r, g, b = 0, 0, 0

    x = 0.95047 * (x**3 if x**3 > 0.008856 else (x - 16 / 116) / 7.787)
    y = 1.00000 * (y**3 if y**3 > 0.008856 else (y - 16 / 116) / 7.787)
    z = 1.08883 * (z**3 if z**3 > 0.008856 else (z - 16 / 116) / 7.787)

    r = x * 3.2406 + y * -1.5372 + z * -0.4986
    g = x * -0.9689 + y * 1.8758 + z * 0.0415
    b = x * 0.0557 + y * -0.2040 + z * 1.0570

    r = (1.055 * r ** (1 / 2.4) - 0.055) if r > 0.0031308 else 12.92 * r
    g = (1.055 * g ** (1 / 2.4) - 0.055) if g > 0.0031308 else 12.92 * g
    b = (1.055 * b ** (1 / 2.4) - 0.055) if b > 0.0031308 else 12.92 * b

    return [max(0, min(1, r)) * 255, max(0, min(1, g)) * 255, max(0, min(1, b)) * 255]


def rgb2lab(rgb):
    r = rgb[0] / 255
    g = rgb[1] / 255
    b = rgb[2] / 255
    x, y, z = 0, 0, 0

    r = r**2.4 if r > 0.04045 else r / 12.92
    g = g**2.4 if g > 0.04045 else g / 12.92
    b = b**2.4 if b > 0.04045 else b / 12.92

    x = (r * 0.4124 + g * 0.3576 + b * 0.1805) / 0.95047
    y = (r * 0.2126 + g * 0.7152 + b * 0.0722) / 1.00000
    z = (r * 0.0193 + g * 0.1192 + b * 0.9505) / 1.08883

    x = x ** (1 / 3) if x > 0.008856 else (7.787 * x) + 16 / 116
    y = y ** (1 / 3) if y > 0.008856 else (7.787 * y) + 16 / 116
    z = z ** (1 / 3) if z > 0.008856 else (7.787 * z) + 16 / 116

    return [(116 * y) - 16, 500 * (x - y), 200 * (y - z)]


def deltaE(labA, labB):
    deltaL = labA[0] - labB[0]
    deltaA = labA[1] - labB[1]
    deltaB = labA[2] - labB[2]
    c1 = math.sqrt(labA[1] * labA[1] + labA[2] * labA[2])
    c2 = math.sqrt(labB[1] * labB[1] + labB[2] * labB[2])
    deltaC = c1 - c2
    deltaH = deltaA * deltaA + deltaB * deltaB - deltaC * deltaC
    deltaH = 0 if deltaH < 0 else math.sqrt(deltaH)
    sc = 1.0 + 0.045 * c1
    sh = 1.0 + 0.015 * c1
    deltaLKlsl = deltaL / 1.0
    deltaCkcsc = deltaC / sc
    deltaHkhsh = deltaH / sh
    i = deltaLKlsl * deltaLKlsl + deltaCkcsc * deltaCkcsc + deltaHkhsh * deltaHkhsh
    return 0 if i < 0 else math.sqrt(i)


def build_adress(x):
    adress = x["adress"].lower() + " " + str(x["cp"]) + " " + x["city"].lower()
    adress = " ".join([e.capitalize() if len(e) >= 3 else e for e in adress.split(" ")]).replace(" l ", " l'")
    adress = "-".join([e[0].upper() + e[1:] if len(e) >= 3 else e for e in adress.split("-")])

    return pretify_address(adress)


def pretify_address(adress):
    adress = " ".join([e.capitalize() if len(e) >= 3 else e for e in adress.lower().split(" ")]).replace(" l ", " l'")

    adress = "-".join([e[0].upper() + e[1:] if len(e) >= 3 else e for e in adress.split("-")])

    return adress


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate the distance between two points (lat1,lon1) and (lat2, lon2) in km"""

    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    distance = R * c
    return distance


def extend_dict(x_, avg, clat, clon):
    new_address = build_adress(x_)
    delta_average = -float(np.round(float(x_["valeur"]) * 60 - avg * 60, 1))
    return {
        "address": new_address,
        "price_per_L": float(np.round(float(x_["valeur"]), 2)),
        "price_tank": round(float(x_["valeur"]) * 60),
        "delta_average": delta_average,
        "better_average": (delta_average > 0) * 1 + (delta_average < 0) * -1,
        "google_map_link": f"https://www.google.com/maps/search/?api=1&query={new_address.replace(' ','+')}",
        "distance": haversine_distance(x_["latitude"], x_["longitude"], clat, clon),
        "latitude": x_["latitude"],
        "longitude": x_["longitude"],
    }


def computeColorSimilarityForFeatureSet(featureSet, refFeatureVector, distanceThreshold):
    ### This expects a featureset, in mouseoverColor (i.e. feature) separately... this should then go through each individual
    ## feature and convert it to LAB space and use the colormath library to compute the delta_e score
    ## In the futurue I may want to look into cython or HIT
    """referenceColor: [Array]"""
    st = time.time()
    refColor_lab = rgb2lab(refFeatureVector)
    print(refColor_lab)
    tilesInRange = []
    for i in featureSet:
        tileColor_lab = rgb2lab(i.average)
        delta_e = deltaE(refColor_lab, tileColor_lab)
        if delta_e < distanceThreshold:
            tilesInRange.append((i.localTileId, delta_e))
    print(time.time() - st, "seconds to compute features")
    return tilesInRange
