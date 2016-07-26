"""

- audit the OSMFILE and change the variable 'mapping' to reflect the changes needed to fix 
    the unexpected street types to the appropriate ones in the expected list.
    You have to add mappings only for the actual problems you find in this OSMFILE,
    not a generalized solution, since that may and will depend on the particular area you are auditing.
- write the update_name function, to actually fix the street name.
    The function takes a string with street name as an argument and should return the fixed name
    We have provided a simple test so that you see what exactly is expected
"""
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = "test.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
zip_code_re = re.compile(r'^[0-9]{5}(?:-[0-9]{4})?$', re.IGNORECASE)

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


def audit():
    st_types  = audit_street(OSMFILE)
    for st_type, ways in st_types.iteritems():
        for name in ways:
            better_name = update_name(name, mapping)
            print name, "=>", better_name

if __name__ == '__main__':
    audit()