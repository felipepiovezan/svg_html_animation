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
        self.out = out
        self.node = node
        self.js_name = SvgJsPath.gen_unique_name()
        self.html_id = node.get("id")
        assert self.html_id is not None, "Path should have an id value"
        self.__declare()

    def __declare(self):
        js_query = f'document.getElementById("{self.html_id}")'
        print(
            f'let {self.js_name} = {{path: {js_query}, length: {js_query}.getTotalLength()}}',
            file=self.out)


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

    def __init__(self, out):
        """Prints the boilerplate JS code to `out`."""

        self.print = lambda msg: print(msg, file=out)
        self.js_animation_queue = 'animation_queue'
        self.animation_queue = set()
        self.js_drawing_idx = 'drawing_idx'
        self.print(f'let {self.js_animation_queue} = []')
        self.print(f'let {self.js_drawing_idx} = 0')
        self.length_per_ms = .5

        self.js_stop_animation_event = '"stop_animation"'

        self.js_clear_path_foo = 'clear_path'
        self._print_clear_path_foo()

        self.js_listen_to_kb = 'listen_to_kb'
        self.print(f'let {self.js_listen_to_kb} = false')
        self.js_next_frame_foo = 'next_frame'
        self._print_next_frame_foo()
        self._print_keyboard_event_foo()

    def _print_clear_path_foo(self):
        js_path_arg = 'path'
        js_length = f'{js_path_arg}.length'
        self.print(f'''
function {self.js_clear_path_foo}({js_path_arg}) {{
  if ({js_path_arg}.hasOwnProperty("path")) {{
    {js_path_arg}.path.style.strokeDasharray = {js_length} + " " + {js_length}
    {js_path_arg}.path.style.strokeDashoffset = {js_length}
  }}
}}''')

    def _print_next_frame_foo(self):
        js_current_path = f'{self.js_animation_queue}[{self.js_drawing_idx}]'
        self.print(f'''
let start;
let handle = 0;
function {self.js_next_frame_foo}(timestamp) {{
  if ({self.js_drawing_idx} == {self.js_animation_queue}.length) {{
    window.cancelAnimationFrame(handle);
    return
  }}

  if ({self.js_animation_queue}[{self.js_drawing_idx}] === {self.js_stop_animation_event}) {{
    {self.js_drawing_idx}++;
    window.cancelAnimationFrame(handle);
    {self.js_listen_to_kb} = true;
    return
  }}

  if (start === undefined)
    start = timestamp;

  const elapsed = timestamp - start;
  const total_time =  {js_current_path}.length / {self.length_per_ms};
  const percentage = elapsed/total_time
  const progress = Math.min(1, percentage)
  {js_current_path}.path.style.strokeDashoffset = Math.floor({js_current_path}.length * (1 - progress));
  handle = window.requestAnimationFrame({self.js_next_frame_foo});

  if (progress === 1) {{
    start = timestamp;
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
      handle = window.requestAnimationFrame({self.js_next_frame_foo});
    default:
      return;
  }}
}}, false);
''')

    def set_dimensions_to_100pc(self, svg: ET.Element):
        """Remove the `width` and `height` attributes from the SVG node.

        If these attributes are empty, they instead become 100%, and the svg
        container will take all the space available on the top level container,
        scaling accordingly.

        This allows further manipulation of the viewbox, setting its dimensions
        to be those of a rectangle, effectively manipulating the "camera".
        """

        svg_html_id = svg.get("id")
        assert svg_html_id is not None, "Svg node should have an id value"
        assert svg.tag == SvgUtils._svg_tag, "Setting dimensions is only possible with SVG node"

        js_query = f'document.getElementById("{svg_html_id}")'
        self.print(f'{js_query}.setAttribute("width" , "100%")')
        self.print(f'{js_query}.setAttribute("height", "100%")')

    def add_path_to_queue(self, path: SvgJsPath):
        assert path not in self.animation_queue, "Animation queue must not contain duplicates"
        self.animation_queue.add(path)
        self.print(f'{self.js_animation_queue}.push({path.js_name})')

    def add_group_to_queue(self, group: SvgJsGroup):
        assert 0 == len(self.animation_queue.intersection(
            group.paths)), "Animation queue must not contain duplicates"
        self.animation_queue.update(group.paths)
        self.print(
            f'{group.js_name}.forEach(function(x) {{ {self.js_animation_queue}.push(x)  }});')

    def add_stop_event_to_queue(self):
        self.print(
            f'{self.js_animation_queue}.push({self.js_stop_animation_event});')

    def clear_paths_from_screen(self):
        """Output JS call to function that removes all paths from screen."""

        self.print(
            f'{self.js_animation_queue}.forEach(function(x) {{ {self.js_clear_path_foo}(x)  }});')

    def start_animation(self):
        """Output JS call to function that starts the animation."""

        self.print(f'window.requestAnimationFrame({self.js_next_frame_foo})')
