edmonton_post_codes = [] #need to obtain this list with authentic source

#prepare a list of post_codes in the data

import xml.etree.cElementTree as ET
from data_cleaning import clean_postal_code

OSMFILE = "edmonton_canada.osm"

#list of unexpected postal codes in the data that needs to be ignored
unexpected_postal_code = ['AB T5J', 'Alberta T6G', 'T5J', 'T6E', 'T6G', 
                          'AB T6E4S6']        


def is_postalcode(elem):
    return (elem.attrib['k'] == "postal_code" or elem.attrib['k'] == 
            "addr:postcode")


def postcode_list(osmfile):
    code_list = []
    osm_file = open(osmfile, "r")
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_postalcode(tag):
                    code = tag.attrib['v'].strip()
                    if code not in unexpected_postal_code:
                        code_list.append(clean_postal_code(code))
    return code_list


postcodes_in_data = postcode_list(OSMFILE)

#check if each of the postcode in the data is a valid Edmonton postal code
invalid_post_code = []
for code in postcodes_in_data:
    code = code.replace(" ", "")
    
    if code  in edmonton_post_codes:
        continue
    else:
        invalid_post_code.append(code)
print "Invalid post codes"
print "------------------"
print invalid_post_code

