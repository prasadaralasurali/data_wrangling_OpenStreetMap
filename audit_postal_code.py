import xml.etree.cElementTree as ET
import re

OSMFILE = "edmonton_canada.osm"
po_code = re.compile(r'^[A-Z][0-9][A-Z][\s-]?[0-9][A-Z][0-9]$', re.IGNORECASE)

def audit_postalcode(po_code_types, code):
    
    m = po_code.search(code)
    if not m:
        po_code_types.add(code)
        


def is_postalcode(elem):
    return (elem.attrib['k'] == "postal_code" or elem.attrib['k'] == 
            "addr:postcode")


def audit(osmfile):
    osm_file = open(osmfile, "r")
    po_code_types = set([])
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_postalcode(tag):
                    audit_postalcode(po_code_types, tag.attrib['v'].strip())
    osm_file.close()
    return po_code_types


unexpected_postal_code = audit(OSMFILE)
print "Unexpected postal codes"
print "-----------------------"
print unexpected_postal_code
