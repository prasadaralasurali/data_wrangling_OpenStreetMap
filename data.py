#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET
import cerberus
import schema
from data_cleaning import clean_street_name, clean_postal_code, clean_phone_number, clean_house_number


OSM_PATH = "edmonton_canada.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


unexpected_postal_code = ['AB T5J', 'Alberta T6G', 'T5J', 'T6E', 'T6G', 
                          'AB T6E4S6']
unexpected_house_numbers = ['P.O. Box 21100', '1240, 5555', '10103;10360', '109 Street']
house_number_type = ["addr:housenumber", 
                     "addr:housenumber:first:left",
                     "addr:housenumber:last:left",
                     "addr:housenumber:last:right",
                     "addr:housenumber:first:right"]

def clean_data(value, k):
    if k == "addr:street":
        value = clean_street_name(value)
    elif k == "addr:postcode" or k == "postal_code":
        if value in unexpected_postal_code:
            return None
        else:
            value = clean_postal_code(value)
    elif k == "phone" or k == "contact:phone":
        value = clean_phone_number(value)
    elif k == "addr:city": 
        value = "Edmonton"
    elif k == 'addr:province' or k == "addr:state": 
        value = "AB"
    elif k == "addr:country": 
        value = "Canada"
    elif k in house_number_type:
        if value in unexpected_house_numbers:
            return None
        else:
            value = clean_house_number(value)
    return value
    

def tag_parser(child, element_id):
    tag_attribs = {}
    tag_attribs['id'] = element_id
    k = child.attrib['k']
    if PROBLEMCHARS.search(k):
        return None
    elif LOWER_COLON.search(k):
        k_split = k.split(':')
        k_split = [i.strip() for i in k_split]
        tag_attribs['key'] = ":".join(k_split[1:])
        tag_attribs['type'] = k_split[0]
        
    else:
        tag_attribs['key'] = k
        tag_attribs['type'] = 'regular'
    k_value = clean_data(child.attrib['v'], k)
    if k_value:
        tag_attribs['value'] = k_value
        return tag_attribs
    else:
        return None

def node_parser(element, node_attribs, tags):   
    for field in NODE_FIELDS:
        if field in element.keys():
            node_attribs[field] = element.attrib[field]
    for child in element:
        tag_attribs = tag_parser(child, element.attrib['id'])
        if tag_attribs:
            tags.append(tag_attribs)        
    return (node_attribs, tags)

def way_parser(element, way_attribs, way_nodes, tags):
    for field in WAY_FIELDS:
        way_attribs[field] = element.attrib[field]
    i = 0
    for child in element:
        way_node_attribs = {}
        if child.tag == "tag":            
            tag_attribs = tag_parser(child, element.attrib['id'])
            if tag_attribs:
                tags.append(tag_attribs)
        elif child.tag == "nd":
            way_node_attribs['id'] = element.attrib['id']
            way_node_attribs['node_id'] = child.attrib['ref']
            way_node_attribs['position'] = i
            way_nodes.append(way_node_attribs)
        i += 1            
    return (way_attribs, way_nodes, tags)
def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements
    to_skip_node_ids = ["4897962690", "4897985747", "4898033751"]
    #the above nodes do not belong to Edmonton city
    if element.tag == 'node' and element.attrib['id'] not in to_skip_node_ids:
        node_attribs, tags = node_parser(element, node_attribs, tags)
        return {'node': node_attribs, 'node_tags': tags}
            
   
    elif element.tag == 'way':
        way_attribs, way_nodes, tags = way_parser(element, way_attribs, way_nodes, tags)
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}

# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':

    process_map(OSM_PATH, validate=True)


