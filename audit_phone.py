import xml.etree.cElementTree as ET
import re
import sys

OSMFILE = "edmonton_canada.osm"
phone_chr = re.compile(r'^[()\-\+\s\.0-9]*$')

def audit_phone(phone, unexpected_phones):
    #Are there at least 10 digits?
    i = 0
    for ch in phone:
        if ch in "0123456789":
            i +=1
    if i < 10:
        unexpected_phones.append(phone)
    #is area-code (780) in phone number? This code considers 780 anywhere in 
    # the number okay. This problem will be dealth with when cleaning phone
    #numbers in the 'clean_phone.py' file
    if '780' not in phone:
        unexpected_phones.append(phone)
        #is phone number have any special character
    m = phone_chr.search(phone)
    if not m:
        unexpected_phones.append(phone)
    
 
def is_phone(elem):
    return (elem.attrib['k'] == "phone" or elem.attrib['k'] == 
            "contact:phone")


def audit(osmfile):
    osm_file = open(osmfile, "r")
    unexpected_phones = []
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_phone(tag):
                    audit_phone(tag.attrib['v'], unexpected_phones)
    osm_file.close()
    return unexpected_phones

unexpected_phone_numbers = audit(OSMFILE)
print "Unexpected phone numbers"
print "-----------------------"
print unexpected_phone_numbers
