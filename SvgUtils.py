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


_svg_namespace = '{http://www.w3.org/2000/svg}'
_group_tag = _svg_namespace + 'g'
_path_tag = _svg_namespace + 'path'
_rectangle_tag = _svg_namespace + 'rect'
_svg_tag = _svg_namespace + 'svg'


def svg_groups(root: ET.Element):
    return _filter_tag(root, _group_tag)


def svg_paths(root: ET.Element):
    return _filter_tag(root, _path_tag)


def svg_rectangles(root: ET.Element):
    return _filter_tag(root, _rectangle_tag)
