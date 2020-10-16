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
    """

    def __init__(self, out):
        """Prints the boilerplate JS code to `out`."""

        self.print = lambda msg: print(msg, file=out)
        self.js_animation_queue = 'animation_queue'
        self.js_drawing_idx = 'drawing_idx'
        self.print(f'let {self.js_animation_queue} = []')
        self.print(f'let {self.js_drawing_idx} = 0')
        self.length_per_ms = .5

        self.js_clear_path_foo = 'clear_path'
        self._print_clear_path_foo()

        self.js_next_frame_foo = 'next_frame'
        self._print_next_frame_foo()

    def _print_clear_path_foo(self):
        js_path_arg = 'path'
        js_length = f'{js_path_arg}.length'
        self.print(f'''
        function {self.js_clear_path_foo}({js_path_arg}) {{
            {js_path_arg}.path.style.strokeDasharray = {js_length} + " " + {js_length}
            {js_path_arg}.path.style.strokeDashoffset = {js_length}
        }}
        ''')

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

      if (start === undefined)
        start = timestamp;

      const elapsed = timestamp - start;
      const total_time =  {js_current_path}.length / {self.length_per_ms};
      const percentage = elapsed/total_time
      const progress = Math.min(1, percentage)
      {js_current_path}.path.style.strokeDashoffset = Math.floor({js_current_path}.length * (1 - progress));
      handle = window.requestAnimationFrame(step);

      if (progress === 1) {{
        start = timestamp;
        {self.js_drawing_idx}++;
      }}
    }}
    ''')
