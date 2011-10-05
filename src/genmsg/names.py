PRN_SEPARATOR = '/'

import re
#ascii char followed by (alphanumeric, _, /)
RESOURCE_NAME_LEGAL_CHARS_P = re.compile('^[A-Za-z][\w_\/]*$') 
def is_legal_resource_name(name):
    """
    Check if name is a legal ROS name for filesystem resources
    (alphabetical character followed by alphanumeric, underscore, or
    forward slashes). This constraint is currently not being enforced,
    but may start getting enforced in later versions of ROS.

    @param name: Name
    @type  name: str
    """
    # resource names can be unicode due to filesystem
    if name is None:
        return False
    m = RESOURCE_NAME_LEGAL_CHARS_P.match(name)
    # '//' check makes sure there isn't double-slashes
    return m is not None and m.group(0) == name and not '//' in name

BASE_RESOURCE_NAME_LEGAL_CHARS_P = re.compile('^[A-Za-z][\w_]*$') #ascii char followed by (alphanumeric, _)
def is_legal_resource_base_name(name):
    """
    Validates that name is a legal resource base name. A base name has
    no package context, e.g. "String".
    """
    # resource names can be unicode due to filesystem
    if name is None:
        return False
    m = BASE_NAME_LEGAL_CHARS_P.match(name)
    return m is not None and m.group(0) == name

def package_resource_name(name):
    """
    Split a name into its package and resource name parts, e.g. 'std_msgs/String -> std_msgs, String'

    :param name: package resource name, e.g. 'std_msgs/String', ``str``
    :returns: package name, resource name, ``(str, str)``
    :raises: :exc:`ValueError` If name is invalid
    """    
    if PRN_SEPARATOR in name:
        val = tuple(name.split(PRN_SEPARATOR))
        if len(val) != 2:
            raise ValueError("invalid name [%s]"%name)
        else:
            return val
    else:
        return '', name

def resource_name(res_pkg_name, name, my_pkg=None):
    """
    Convert package name + resource into a fully qualified resource name

    :param res_pkg_name: name of package resource is located in, ``str``
    :param name: resource base name, ``str``
    :param my_pkg: name of package resource is being referred to
        in. If specified, name will be returned in local form if 
        res_pkg_name is my_pkg, ``str``
    :returns: name for resource , ``str``
    """    
    if res_pkg_name != my_pkg:
        return res_pkg_name+PRN_SEPARATOR+name
    return name
