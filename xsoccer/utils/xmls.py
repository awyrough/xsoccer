# XML Utilities
import xml.etree.cElementTree as etree

def get_root_from_file(data_filename):
    """Returns the root of an XML tree in data_filename"""
    data_file = open(data_filename, "rU")
    xml_data_tree = etree.parse(data_file)
    return xml_data_tree.getroot()

def get_children(xml_obj):
    """Return the XML elements one level down"""
    return [x for x in xml_obj]

def pull_attrib(xml_obj, attrib):
    """Pull the XML attr value"""
    return xml_obj.attrib[attrib]

def get_tag(xml_obj, tag_name):
    """Returns the matching tag attr:value"""
    children = get_children(xml_obj)
    for child in children:
        if child.tag == tag_name:
            return child
    return None
