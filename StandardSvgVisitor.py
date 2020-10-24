from CameraEvent import CameraEvent
from SequentialEventContainer import SequentialEventContainer
from ParallelEventContainer import ParallelEventContainer
from PathEvent import PathEvent

# Precondition to use this class: no two camera events should be placed in
# parallel.
class GroupAndPathVisitor:
    def __init__(self, out):
      self.out = out
      self.cameras = []

    def visit_root(self, node: ET.ElementTree):
      assert SvgUtils.is_root(node)
      self.cameras = []
      events = [self.visit(child) for child in Node]
      events = [event for event in events if event]
      return events

    def visit(self, node: ET.ElementTree):
      if SvgUtils.is_path(node):
        return self.visit_path(node)
      if SvgUtils.is_group(node):
        return self.visit_group(node)
      if SvgUtils.is_rectangle(node):
        return self.visit_rectangle(node)
      print(
          f'Warning: ignroring SVG node: {SvgUtils.get_id(node)}, '
          f'type = {node.tag}')
      return None

    def visit_path(self, node: ET.ElementTree):
      return PathEvent(node, self.out)

    def visit_group(self, node: ET.ElementTree):
      name = str(SvgUtils.get_id(node))
      if name.startswith('par_'):
        return self.visit_parallel_group(node):
      return self.visit_sequential_group(node)

    def visit_sequential_group(self, node: ET.ElementTree):
      events = [self.visit(child) for child in Node]
      events = [event for event in events if event]
      return SequentialEventContainer(events, out)

    def visit_parallel_group(self, node: ET.ElementTree):
      events = [self.visit(child) for child in Node]
      events = [event for event in events if event]
      return ParallelEventContainer(events, out)

    def visit_rectangle(self, node: ET.ElementTree):
      duration = 0 if len(self.cameras) == 0 else 1000
      old_cam = [0,0,1,1] if len(self.cameras) == 0 else self.cameras[-1]
      new_cam = _convert_rectangle_to_array(rectangle)
      self.cameras.append(new_cam)
      return CameraEvent(old_cam, new_cam, duration, self.svg_root, self.out)


def _convert_rectangle_to_array(rectangle: ET.Element):
    assert rectangle.tag == SvgUtils._rectangle_tag
    array = [rectangle.get(key) for key in ["x", "y", "width", "height"]]
    assert None not in array
    return array
