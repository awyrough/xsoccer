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

def get_attrib(xml_obj, attrib):
    """Get an arbitrary XML attribute"""
    return xml_obj.attrib[attrib]

def get_tag(xml_obj, tag_name):
    """Returns the matching tag attribute from among the children"""
    children = get_children(xml_obj)
    for child in children:
        if child.tag == tag_name:
            return child
    return None

def get_tag_and_type(xml_obj, tag_name, type_name):
    """Returns the matching tag / type attribute from among the children"""
    children = get_children(xml_obj)
    for child in children:
        if child.tag == tag_name:
            if type_name == "":
                return child
            elif get_attrib(child, "Type") == type_name:
                return child
    return None

def pull_text_if_exists(xml_obj, tag_name, type_name=""):
    """Returns the text value of the matching tag / type attribute from among the children

        This is created because get_tag_and_type().text could return a none_type if the tag didn't exist
    """
    obj_of_interest = get_tag_and_type(xml_obj, tag_name, type_name)
    text = None
    if obj_of_interest is not None:
        text = obj_of_interest.text
        if text == "Unknown": #rather use a Null value rather than an "unknown" string
            text = None
    return text