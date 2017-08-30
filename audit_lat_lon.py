import xml.etree.cElementTree as ET

OSMFILE = "edmonton_canada.osm"

def audit(osmfile):
    osm_file = open(osmfile, "r")
    unexpected_lon = []
    unexpected_lat = []
    
    lat_min = 53.4251
    lat_max = 53.6593
    lon_min = -113.7085
    lon_max = -113.3446
    
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node":
            if float(elem.attrib['lat']) < lat_min or float(elem.attrib['lat']) >lat_max:
                unexpected_lat.append(elem.attrib['lat'])
            if float(elem.attrib['lon']) < lon_min or float(elem.attrib['lon']) >lon_max:
                unexpected_lon.append(elem.attrib['lon'])
                    
    osm_file.close()
    return unexpected_lon, unexpected_lat

unexpected_lon, unexpected_lat = audit(OSMFILE)
print "Unexpected longitudes"
print "-----------------------"
print unexpected_lon

print "Unexpected latitudes"
print "-----------------------"
print unexpected_lat

