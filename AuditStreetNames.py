import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint
import sys

OSMFILE = "edmonton_canada.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
#Add some of the common street names in Edmonton to the list 
#(Crescent, Hill, Point, Way)
expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", 
            "Square", "Lane", "Road", "Trail", "Parkway", "Commons", 
            "Crescent", "Hill", "Point", "Way"]

def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'].strip())
    osm_file.close()
    return street_types


st_types = audit(OSMFILE)

#print unexpected street types
print "Unexpected street types"
print "-----------------------"
for i in st_types:
    print i

#print st_types to a file
orig_stdout = sys.stdout
f = open('street_type.txt', 'w')
sys.stdout = f
pprint.pprint(dict(st_types))
sys.stdout = orig_stdout
f.close()

# further audit street names when there are prefixes like NW, North-West etc.
prefixes = ['North-west', 'North-West', 'Northwest', 'W', 'NW']
for prefix in prefixes:    
    street_types_1 = defaultdict(set)
    for value in st_types[prefix]:
                audit_street_type(street_types_1,value[:-(len(prefix) + 1)].strip())
    print prefix
    print "-----------"
    pprint.pprint(dict(street_types_1))






    
        
        

