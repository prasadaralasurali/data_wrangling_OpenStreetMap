import xml.etree.cElementTree as ET
import re
import sys

OSMFILE = "edmonton_canada.osm"
house_number_chr = re.compile(r'^[0-9]+\-?[0-9]*$')

def audit_house_number(house_number, unexpected_house_numbers):
    
    m = house_number_chr.search(house_number)
    if not m:
        unexpected_house_numbers.append(house_number)
    
 
def is_house_number(elem):
    house_number_type = ["addr:housenumber", 
                         "addr:housenumber:first:left",
                         "addr:housenumber:last:left",
                         "addr:housenumber:last:right",
                         "addr:housenumber:first:right"]
    return (elem.attrib['k'] in house_number_type)


def audit(osmfile):
    osm_file = open(osmfile, "r")
    unexpected_house_numbers = []
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_house_number(tag):
                    audit_house_number(tag.attrib['v'], unexpected_house_numbers)
    osm_file.close()
    return unexpected_house_numbers

unexpected_house_numbers = audit(OSMFILE)
print "Unexpected house numbers"
print "-----------------------"
print unexpected_house_numbers

