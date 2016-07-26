#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json
from collections import defaultdict


lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]
ADDR = ["housenumber", "postcode", "street"]

OSMFILE = "test.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
zip_code_re = re.compile(r'^[0-9]{5}(?:-[0-9]{4})?$', re.IGNORECASE)

global expected_street
expected_street = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", "Trail", "Parkway", "Commons", "Way", "Circle"]
mapping = {" st": " Street", " St": " Street", " St.": " Street", " Rd.": " Road", " Rd": " Road", " ave": " Avenue", " Ave": " Avenue", 
    " Ave.": " Avenue", " Ln": " Lane", " Dr": " Drive", " Dr.": " Drive", " Blvd": " Boulevard", " Cir": " Circle", " Ct": " Court", " Pkwy": " Parkway"}

def audit_street_type(street_types, street_name):

    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected_street:
            street_types[street_type].add(street_name)

def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

def audit_street(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
            
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types

def update_name(name, mapping):

    for search_error in mapping:
        if search_error in name:
            name = name.replace(search_error, mapping[search_error])
            if name.find("Streetreet") != -1:
                name = name.replace("Streetreet", "Street")
            
    return name

def shape_element(element):
  node = {}
  node['created'] = {}
  address = {}
  node['pos'] = [0,0]

  if element.tag == "node" or element.tag == "way":
    st_types  = audit_street(OSMFILE)
    for st_type, ways in st_types.iteritems():
      for name in ways:
        update_name(name, mapping)

    node["type"] = element.tag
    for key, value in element.attrib.iteritems():
      if key in CREATED:
        node['created'][key] = value
      elif key == 'lat':
        node['pos'][0] = float(value)
      elif key == 'lon':
        node['pos'][1] = float(value)
      else:
        node[key] = value

    for subtag in element.iter('tag'):
      if re.search(problemchars, subtag.get('k')):
        pass
      elif re.search(r'\w+:\w+:\w+', subtag.get('k')):
        pass
      elif subtag.get('k').startswith('addr:'):
        address[subtag.get('k')[5:]] = subtag.get('v')
        node['address'] = address

    return node

  else:
    return None


def process_map(file_in, pretty = False):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data

def test():
    # NOTE: if you are running this code on your computer, with a larger dataset, 
    # call the process_map procedure with pretty=False. The pretty=True option adds 
    # additional spaces to the output, making it significantly larger.
    data = process_map('test.osm', False)
    pprint.pprint(data[0])
    
if __name__ == "__main__":
    test()