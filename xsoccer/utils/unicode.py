# Unicode Utilities
import unicodedata

def remove_accents(input_str):
    """Removes player accents"""
    encoding = "utf-8"
    byte_string = input_str 
    unicode_string = byte_string.decode(encoding)
    
    nfkd_form = unicodedata.normalize('NFKD', unicode_string)
    only_ascii = nfkd_form.encode('ASCII', 'ignore')
    
    return only_ascii