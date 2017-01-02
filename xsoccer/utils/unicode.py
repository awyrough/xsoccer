# Unicode Utilities
import unicodedata

def remove_accents(input_str):
    """Removes player accents"""
    encoding = "utf-8"
    byte_string = input_str 

    if whatisthis(byte_string) == "ordinary string":
    	unicode_string = byte_string.decode(encoding)
    else:
    	unicode_string = unicode(byte_string)
    nfkd_form = unicodedata.normalize('NFKD', unicode_string)
    only_ascii = nfkd_form.encode('ascii', 'ignore')
    return only_ascii

def whatisthis(s):
    """Helps decode what type of string you're working with"""
    if isinstance(s, str):
        return "ordinary string"
    elif isinstance(s, unicode):
       	return "unicode string"
    else:
       	raise Exception("not a string")
