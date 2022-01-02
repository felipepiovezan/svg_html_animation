from svganimator import SvgUtils
from svganimator.CameraEvent import CameraEvent
from svganimator.ParallelEventContainer import ParallelEventContainer
from svganimator.PathEvent import PathEvent
from svganimator.FadeEvent import FadeEvent
from svganimator.SequentialEventContainer import SequentialEventContainer
import xml.etree.ElementTree as ET
import re


class SimpleVisitor:
    """Converts and SVG graph into an Event graph.

    This class visits the SVG graph starting from the root in DFS order.
    For each node it visits:
      1. If it is a Path node, a PathEvent is created. Path nodes are assumed
      to be leaves.
      2. If it is a Rectangle node, a CameraEvent is created. The first such
      CameraEvent encountered has duration of 0ms and is assumed to have no
      previous camera associated with it. If the name of the camera contains a
      substring `d=<number>`, the camera event will have duration `number`
      miliseconds. Rectangle nodes are assumed to be leaves.
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
        """Creates the visitor and use `out` to instantiate each of the Events.

        A definition of the Event classes is added to `out`.
        """

        self.out = out
        self.cameras = []
        ParallelEventContainer.print_js_class(self.out)
        SequentialEventContainer.print_js_class(self.out)
        PathEvent.print_js_class(self.out)
        CameraEvent.print_js_class(self.out)
        FadeEvent.print_js_class(self.out)

    def visit_root(self, node: ET.ElementTree):
        """Create the Event graph, and return it as an array of Events."""

        assert SvgUtils.is_root(node)
        self.cameras = []
        self.svg_root = node
        events = [self._visit(child) for child in node]
        events = [event for event in events if event]
        return events

    def _visit(self, node: ET.ElementTree):
        if SvgUtils.is_circle(node):
            return self._visit_circle(node)
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

    def _visit_circle(self, node: ET.ElementTree):
        return FadeEvent(node, self.out)

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
        if len(events) < 2:
            print(
                f'Warning: parallel group {SvgUtils.get_id(node)} '
                f'has {len(events)} elements')
        return ParallelEventContainer(events, self.out)

    def _get_camera_duration(self, name):
        duration = 1000
        if len(self.cameras) == 0:
            duration = 0
        match = re.match(r'.*d=(\d+).*', name)
        if match:
            duration = int(match.group(1))
        return duration

    def _visit_rectangle(self, node: ET.ElementTree):
        name = str(SvgUtils.get_id(node))
        duration = self._get_camera_duration(name)
        new_cam = _convert_rectangle_to_array(node)
        old_cam = new_cam if len(self.cameras) == 0 else self.cameras[-1]
        self.cameras.append(new_cam)
        SvgUtils.hide_svg_obj(node, self.out)
        return CameraEvent(old_cam, new_cam, duration, self.svg_root, self.out)


def _convert_rectangle_to_array(rectangle: ET.Element):
    assert rectangle.tag == SvgUtils.rectangle_tag
    array = [float(rectangle.get(key))
             for key in ["x", "y", "width", "height"]]
    assert None not in array
    return array
