import xml.etree.cElementTree as ET
import re

OSMFILE = "edmonton_canada.osm"
phone_chr = re.compile(r'^[()\-\+\s\.0-9]*$')

def audit_city(city, unexpected_city):
    city_names = ["Edmonton", "edmonton"]
    if city not in city_names: 
        unexpected_city.append(city)
        
def audit_province(province, unexpected_province):
    province_names = ["Alberta", "AB"]
    if province not in province_names: 
        unexpected_province.append(province)
def audit_country(country, unexpected_country):
    country_names = ["CANADA", "Canada", "CA"]
    if country not in country_names: 
        unexpected_country.append(country)
    
 

def audit(osmfile):
    osm_file = open(osmfile, "r")
    unexpected_city = []
    unexpected_province = []
    unexpected_country = []
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if tag.attrib['k'] == "addr:city":
                    audit_city(tag.attrib['v'], unexpected_city)
                elif tag.attrib['k'] == "addr:province" or tag.attrib['k'] == \
                "addr:state":
                    audit_province(tag.attrib['v'], unexpected_province)
                elif tag.attrib['k'] == "addr:country":
                    audit_country(tag.attrib['v'], unexpected_country)
    osm_file.close()
    return unexpected_city, unexpected_province, unexpected_country

unexpected_city, unexpected_province, unexpected_country = audit(OSMFILE)
print "Unexpected city names"
print "-----------------------"
print unexpected_city

print "Unexpected province names"
print "-----------------------"
print unexpected_province

print "Unexpected country names"
print "-----------------------"
print unexpected_country
