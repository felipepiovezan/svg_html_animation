import xml.etree.ElementTree as ET


def get_id(root: ET.Element):
    """ Returns the id member of root. Asserts if not present."""

    id = root.get("id")
    assert id
    return id


def filter(root: ET.Element, predicate):
    """ Filter the direct children of root according to a predicate."""

    return [child for child in root if predicate(child)]


def filter_tag(root: ET.Element, tag):
    """ Filter the direct children of root according to their tag.

    For example, if tag == 'group', return all children of type
    <group></group>.
    """

    return filter(root, lambda x: x.tag == tag)


svg_namespace = '{http://www.w3.org/2000/svg}'
group_tag = svg_namespace + 'g'
path_tag = svg_namespace + 'path'
rectangle_tag = svg_namespace + 'rect'
svg_tag = svg_namespace + 'svg'


def svg_elements_named(name: str, root: ET.Element):
    """Returns direct children of `root` with a given id."""
    return filter(root, lambda x: get_id(x) == name)


def is_group(root: ET.Element):
    """Returns true if root is an SVG group."""

    return root.tag == group_tag


def is_path(root: ET.Element):
    """Returns true if root is an SVG path."""

    return root.tag == path_tag


def is_root(root: ET.Element):
    """Returns true if root is a top level SVG node."""

    return root.tag == svg_tag


def is_rectangle(root: ET.Element):
    """Returns true if root is an SVG rectangle."""

    return root.tag == rectangle_tag


def svg_groups(root: ET.Element):
    """Returns direct children of root that are SVG groups."""

    return filter_tag(root, group_tag)


def svg_paths(root: ET.Element):
    """Returns direct children of root that are SVG paths."""

    return filter_tag(root, path_tag)


def svg_rectangles(root: ET.Element):
    """Returns direct children of root that are SVG rectangles."""

    return filter_tag(root, rectangle_tag)


def hide_svg_obj(node, out):
    """Print the commands necessary to hide node from the screen.

    Note: not a member function because the rectangle is not part of the
    object.
    """

    def out_print(x): return print(x, file=out)
    node_id = get_id(node)
    out_print('{')
    out_print(f'let obj = document.getElementById("{node_id}");')
    out_print('obj.style.opacity = 0')
    out_print('}')
