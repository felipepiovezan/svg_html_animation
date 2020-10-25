from CameraEvent import CameraEvent
from SequentialEventContainer import SequentialEventContainer
from ParallelEventContainer import ParallelEventContainer
from PathEvent import PathEvent
import SvgUtils
import xml.etree.ElementTree as ET


class SimpleVisitor:
    """Converts and SVG graph into an Event graph.

    This class visits the SVG graph starting from the root in DFS order.
    For each node it visits:
      1. If it is a Path node, a PathEvent is created. Path nodes are assumed
      to be leaves.
      2. If it is a Rectangle node, a CameraEvent is created. The first such
      CameraEvent encountered has duration of 0ms and is assumed to have no
      previous camera associated with it. Rectangle nodes are assumed to be
      leaves.
      3. If it is a Group node:
        - If its name starts with "par_", a ParallelEventContainer is created.
        - Otherwise, a SequentialEventContainer is created.
        In both cases, the contents of the containers are the events returned
        by visiting the children of the Group node.

    Within a single node, its children are visited in the order specified by
    the SVG container, i.e., the order in which they would appear in the
    original xml description.
    """

    def __init__(self, out):
        """Creates the visitor and use `out` to instantiate each of the Events."""

        self.out = out
        self.cameras = []

    def visit_root(self, node: ET.ElementTree):
        """Create the Event graph, and return it as an array of Events."""

        assert SvgUtils.is_root(node)
        self.cameras = []
        self.svg_root = node
        events = [self._visit(child) for child in node]
        events = [event for event in events if event]
        return events

    def _visit(self, node: ET.ElementTree):
        if SvgUtils.is_path(node):
            return self._visit_path(node)
        if SvgUtils.is_group(node):
            return self._visit_group(node)
        if SvgUtils.is_rectangle(node):
            return self._visit_rectangle(node)
        print(
            f'Warning: ignroring SVG node: {SvgUtils.get_id(node)}, '
            f'type = {node.tag}')
        return None

    def _visit_path(self, node: ET.ElementTree):
        return PathEvent(node, self.out)

    def _visit_group(self, node: ET.ElementTree):
        name = str(SvgUtils.get_id(node))
        if name.startswith('par_'):
            return self._visit_parallel_group(node)
        return self._visit_sequential_group(node)

    def _visit_sequential_group(self, node: ET.ElementTree):
        events = [self._visit(child) for child in node]
        events = [event for event in events if event]
        return SequentialEventContainer(events, self.out)

    def _visit_parallel_group(self, node: ET.ElementTree):
        events = [self._visit(child) for child in node]
        events = [event for event in events if event]
        return ParallelEventContainer(events, self.out)

    def _visit_rectangle(self, node: ET.ElementTree):
        duration = 0 if len(self.cameras) == 0 else 1000
        old_cam = None if len(self.cameras) == 0 else self.cameras[-1]
        new_cam = _convert_rectangle_to_array(node)
        self.cameras.append(new_cam)
        return CameraEvent(old_cam, new_cam, duration, self.svg_root, self.out)


def _convert_rectangle_to_array(rectangle: ET.Element):
    assert rectangle.tag == SvgUtils.rectangle_tag
    array = [float(rectangle.get(key))
             for key in ["x", "y", "width", "height"]]
    assert None not in array
    return array
