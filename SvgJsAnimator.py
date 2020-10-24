import xml.etree.ElementTree as ET
import SvgUtils


class SvgJsPath:
    """Maps an Svg path to a JavaScript variable.

    This class manipulates aspects of an Svg path through a JS format,
    defined as a struct `{{path, length}}`, where `path` is the HTML object
    itself and length is the pre-computed length (equivalent to
    `path.getTotalLength()`).

    It assumes the parent Svg container has been included in an HTML document
    and can be fetched through `document.getElementById`.
    """

    gid = -1

    def gen_unique_name():
        SvgJsPath.gid += 1
        return 'p' + str(SvgJsPath.gid)

    def __init__(self, node: ET.Element, out):
        """ Declares `node` as a JS variable inside `out`.

        `node` must have the Svg xml path tag.
        `node` must have an id key.
        The resulting JS variable will have name `self.js_name`.
        `out` must be anything accepted by the `file` argument of standard
        `print`.
        """

        assert node.tag == SvgUtils._path_tag, "SvgJsPath must be created with an Svg path"
        self.print = lambda msg: print(msg, file=out)
        self.node = node
        self.js_name = SvgJsPath.gen_unique_name()
        self.html_id = node.get("id")
        assert self.html_id is not None, "Path should have an id value"
        self.__declare()

    def __declare(self):
        js_query = f'document.getElementById("{self.html_id}")'
        self.print(
            f'let {self.js_name} = {{'
            f'path: {js_query}, length: {js_query}.getTotalLength()}}')


class SvgJsGroup:
    """Maps an Svg Group to a JavaScript variable.

    This class manipulates aspects of an Svg group through a JS format.

    It assumes the parent Svg container has been included in an HTML document.
    """

    gid = -1

    def gen_unique_name():
        SvgJsGroup.gid += 1
        return 'group' + str(SvgJsGroup.gid)

    def __init__(self, node: ET.Element, out):
        """ Declares `node` as a JS variable inside `out`.

        This causes an instantiation of SvgJsPath for each Svg path that is a
        direct child of `node`. The group JS variable will be an array of all
        such children.
        `node` must have the Svg xml group tag.
        The resulting JS variable will have name `self.js_name`.
        `out` must be anything accepted by the `file` argument of standard
        `print`.
        """
        assert node.tag == SvgUtils._group_tag, "SvgJsGroup must be created with an Svg group"
        self.print = lambda msg: print(msg, file=out)
        self.node = node
        self.js_name = SvgJsGroup.gen_unique_name()
        self.paths = [SvgJsPath(path, out)
                      for path in SvgUtils.svg_paths(node)]
        self.__declare()

    def __declare(self):
        list_str = ', '.join([f'{path.js_name}' for path in self.paths])
        self.print(f'let {self.js_name} = [{list_str}]')


class SvgJsAnimator:
    """Manipulates HTML properties of SvgPaths using JS.

    Through the manipulation of `style.strokeDasharray` and
    `style.strokeDashoffset`, this class is able to hide or display [pieces of]
    paths. By interacting with the `window.requestAnimationFrame` interface, it
    creates the effect that paths are being drawn.

    No more than one such object should be created for the same file, as it
    relies on global state for some of its functions.
    """

    def __init__(self, out, svg_root: ET.Element):
        """Prints the boilerplate JS code to `out`.

        Initializes the camera to be the bounding box of the entire svg.
        Sets the svg height and width to 100%, effectively fitting the entire
        file to the space allocated for the svg container.
        """

        assert svg_root.tag == SvgUtils._svg_tag, "svg_root must have svg tag"
        root_id = svg_root.get("id")
        assert root_id is not None, "Top svg node should have an id value"

        # Helper function to print to `out`.
        self.out = out
        self.print = lambda msg: print(msg, file=out)

        # Paths in animation must be unique, since they manipulate
        # properties of unique svg objects
        self.paths_in_animation = set()

        # Camera events in animation may contain repeated elements,
        # since they don't change any objects in the screen.
        self.cameras = []

        # Speed in which paths are drawn.
        self.length_per_ms = 1.0

        # Helper variables to write JS code ('js_' prefix)
        # JS function names are prefixed with 'js_foo_'
        # JS animation events are prefixed with 'js_kind_'
        self.js_animation_queue = 'animation_queue'
        self.js_drawing_idx = 'drawing_idx'
        self.js_event_obj = 'obj'
        self.js_foo_clear_path = 'clear_path'
        self.js_foo_event_camera = 'process_camera'
        self.js_foo_event_camera = 'set_camera'
        self.js_foo_event_path = 'process_path'
        self.js_foo_event_stop_animation = 'stop_animation'
        self.js_foo_next_frame = 'next_frame'
        self.js_kind = 'type'
        self.js_kind_camera = '0'
        self.js_kind_path = '1'
        self.js_kind_stop_animation = '2'
        self.js_listen_to_kb = 'listen_to_kb'
        self.js_svg_root = 'svg_root'

        self.print(f'let {self.js_animation_queue} = []')
        self.print(f'let {self.js_drawing_idx} = 0')
        self.print(f'let {self.js_listen_to_kb} = false')
        self.print(
            f'{self.js_svg_root} = document.getElementById("{root_id}")')

        # Print all JS functions.
        self._print_clear_path_foo()
        self._print_keyboard_event_foo()
        self._print_next_frame_foo()
        self._print_process_path_event_foo()
        self._print_process_stop_animation_event_foo()
        self._print_process_camera_event_foo()
        self._print_set_camera_foo()

        # Reset root dimensions to 100% so that BBox setting works properly.
        self.set_dimensions_to_100pc()

    def _print_clear_path_foo(self):
        self.print(f'''
function {self.js_foo_clear_path}(event) {{
    if (event.{self.js_kind} != {self.js_kind_path})
      return;
    path_event = event.{self.js_event_obj};
  path_event.forEach(function(path_and_length) {{
    const length = path_and_length.length;
    path = path_and_length.path;
    path.style.strokeDasharray = length + " " + length;
    path.style.strokeDashoffset = length;
  }});
}}''')

    def _print_process_path_event_foo(self):
        self.print(f'''
// Draws paths on the screen based on time elapsed and draw speed.
// Returns true if all paths in the event have been drawn.
function {self.js_foo_event_path}'''
                   f'''(elapsed, speed_in_ms, path_event, next_frame_cb) {{
  completed_all = true;

  path_event.forEach(function(path_and_length) {{
    const length = path_and_length.length;
    path = path_and_length.path;
    const total_time = length / speed_in_ms;
    const percentage = elapsed/total_time;
    const progress = Math.min(1, percentage);
    path.style.strokeDashoffset = Math.floor(length * (1 - progress));
    completed_all &&= (progress === 1);
  }});

  handle = window.requestAnimationFrame(next_frame_cb);
  return completed_all;
}}
''')

    def _print_process_stop_animation_event_foo(self):
        self.print(f'''
// Stops the animation frame callback loop.
// Always returns true.
function {self.js_foo_event_stop_animation}(handle) {{
  window.cancelAnimationFrame(handle);
  {self.js_listen_to_kb} = true;
  return true
}}
''')

    def _print_process_camera_event_foo(self):
        """Function to create a camera animation.

        Advances each (x, y, width, heigh) component of the camera into the
        direction of the new camera.
        """

        self.print(
            f'function {self.js_foo_event_camera} '
            f'(elapsed, camera_event, next_frame_cb) {{')
        self.print(f'''
const old_cam = camera_event.old_cam;
const new_cam = camera_event.new_cam;
const duration = camera_event.duration;
const progress = Math.min(1, elapsed/duration);
const total_delta = new_cam.map((n, idx) => n - old_cam[idx]);
const cam = old_cam.map((n, idx) => n + progress * total_delta[idx])
{self.js_svg_root}.setAttribute("viewBox", cam.join(" "));
handle = window.requestAnimationFrame(next_frame_cb);
return progress >= 1;
        ''')
        self.print(f'}}')

    def _print_next_frame_foo(self):
        js_current_event = f'{self.js_animation_queue}[{self.js_drawing_idx}]'
        self.print(
            f'''
let start;
let handle = 0;
function {self.js_foo_next_frame}(timestamp) {{
  if ({self.js_drawing_idx} == {self.js_animation_queue}.length) {{
    window.cancelAnimationFrame(handle);
    return
  }}

  if (start === undefined)
    start = timestamp;
  const elapsed = timestamp - start;
  const event_kind = {js_current_event}.{self.js_kind};
  let finished = false;
  if (event_kind === {self.js_kind_stop_animation})
    finished = {self.js_foo_event_stop_animation}(handle);
  else if (event_kind === {self.js_kind_path})
    finished = {self.js_foo_event_path}(elapsed, {self.length_per_ms}, '''
            f'''{js_current_event}.{self.js_event_obj}, {self.js_foo_next_frame})
  else if (event_kind === {self.js_kind_camera})
    finished = {self.js_foo_event_camera}(elapsed, '''
            f'''{js_current_event}.{self.js_event_obj}, {self.js_foo_next_frame})
  else
    console.error("Unhandled event kind");

  if (finished === true) {{
    start = undefined;
    {self.js_drawing_idx}++;
  }}
}}''')

    def _print_keyboard_event_foo(self):
        self.print(f'''
document.addEventListener('keydown', (event) => {{
  if ({self.js_listen_to_kb} == false)
    return;
  switch (event.key) {{
    case "Down": // IE/Edge
    case "ArrowDown":
    case "Right": // IE/Edge
    case "ArrowRight":
    case "Enter":
    case " ":
      {self.js_listen_to_kb} = false
      handle = window.requestAnimationFrame({self.js_foo_next_frame});
    default:
      return;
  }}
}}, false);
''')

    def _print_set_camera_foo(self):
        self.print(f'''
function {self.js_foo_event_camera}(new_rectangle) {{
  {self.js_svg_root}.setAttribute("viewBox", new_rectangle.join(" "));
  return true;
}}
''')

    def set_dimensions_to_100pc(self):
        """Remove the `width` and `height` attributes from the SVG node.

        If these attributes are empty, they instead become 100%, and the svg
        container will take all the space available on the top level container,
        scaling accordingly.

        This allows further manipulation of the viewbox, setting its dimensions
        to be those of a rectangle, effectively manipulating the "camera".
        """

        self.print(f'{self.js_svg_root}.setAttribute("width" , "100%")')
        self.print(f'{self.js_svg_root}.setAttribute("height", "100%")')

    def add_path_to_queue(self, path: SvgJsPath):
        assert path.node not in self.paths_in_animation, "Animation queue must not contain duplicates"
        self.paths_in_animation.add(path.node)
        self.print(
            f'{self.js_animation_queue}.push({{ '
            f'{self.js_kind} : {self.js_kind_path}, '
            f'{self.js_event_obj} : [{path.js_name}] }})')

    def _add_group_to_queue(
            self,
            group: SvgJsGroup,
            simultaneously: bool = False):
        path_nodes = [js_path.node for js_path in group.paths]
        assert 0 == len(self.paths_in_animation.intersection(
            path_nodes)), "Animation queue must not contain duplicates"
        self.paths_in_animation.update(path_nodes)
        if simultaneously:
            self.print()
        else:
            self.print(
                f'{group.js_name}.forEach(function(x) {{\n'
                f'  {self.js_animation_queue}.push({{ '
                f'     {self.js_kind} : {self.js_kind_path}, '
                f'     {self.js_event_obj} : [x] }});'
                f'}});')

    def add_paths_in_group_to_queue(self, group: ET.Element):
        js_group = SvgJsGroup(group, self.out)
        self._add_group_to_queue(js_group)

    def add_stop_event_to_queue(self):
        self.print(
            f'{self.js_animation_queue}.push({{ '
            f'{self.js_kind} : {self.js_kind_stop_animation} }});')

    def clear_paths_from_screen(self):
        """Output JS call to function that removes all paths from screen."""

        self.print(
            f'{self.js_animation_queue}.forEach(function(x) {{ '
            f'{self.js_foo_clear_path}(x)  }});')

    def start_animation(self):
        """Output JS call to function that starts the animation."""

        self.print(f'window.requestAnimationFrame({self.js_foo_next_frame})')

    def set_initial_camera(self, rectangle: ET.Element):
        """Sets the intial camera before the animation starts.

        Must be called exactly once before any calls to `add_camera_event_to_queue`.
        """

        assert len(self.cameras) == 0, "set_initial_camera called incorrectly"
        new_camera = _convert_rectangle_to_array(rectangle)
        self.cameras.append(new_camera)
        new_camera_str = ", ".join(new_camera)
        self.print(f'let original_camera = [{new_camera_str}]')
        self.print(f'{self.js_foo_event_camera}(original_camera)')

    def add_camera_event_to_queue(self, rectangle: ET.Element, duration=1000):
        """Adds an event to set the camera to the area of rectangle.

        Must be called after set_initial_camera.
        Time is the duration of the animation in ms.
        """

        old_cam = ", ".join(self.cameras[-1])
        new_cam = _convert_rectangle_to_array(rectangle)
        self.cameras.append(new_cam)
        new_cam = ", ".join(new_cam)
        self.print(
            f'{self.js_animation_queue}.push({{ '
            f'{self.js_kind} : {self.js_kind_camera}, '
            f'{self.js_event_obj} : {{ '
            f'old_cam : [{old_cam}], new_cam : [{new_cam}], '
            f'duration : {duration} }} }});')


def _convert_rectangle_to_array(rectangle: ET.Element):
    assert rectangle.tag == SvgUtils._rectangle_tag, "Camera must be set with a Svg Rectangle object."
    array = [rectangle.get(key)
             for key in ["x", "y", "width", "height"]]
    assert None not in array, "Expected rectangle to have all 4 values"
    return array
