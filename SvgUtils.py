import xml.etree.ElementTree as ET

def get_id(root: ET.Element):
    """ Returns the id member of root. Asserts if not present."""
    id = root.get("id")
    assert(id)
    return id

def _filter(root: ET.Element, predicate):
    """ Filter the direct children of root according to a predicate."""
    return [child for child in root if predicate(child)]


def _filter_tag(root: ET.Element, tag):
    """ Filter the direct children of root according to their tag.

    For example, if tag == 'group', return all children of type
    <group></group>.
    """

    return _filter(root, lambda x: x.tag == tag)
