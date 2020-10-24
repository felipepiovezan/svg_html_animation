import xml.etree.ElementTree as ET
import SvgUtils
from CameraEvent import CameraEvent
from SequentialEventContainer import SequentialEventContainer
from ParallelEventContainer import ParallelEventContainer
from PathEvent import PathEvent


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
        # Helper function to print to `out`.
        self.out = out
        self.print = lambda msg: print(msg, file=out)

        # Save root and give it a name.
        assert SvgUtils.is_root(svg_root)
        self.svg_root = svg_root
        root_id = SvgUtils.get_id(svg_root)
        self.js_svg_root = 'svg_root'
        self.print(
            f'{self.js_svg_root} = document.getElementById("{root_id}")')

        # Reset root dimensions to 100% so that BBox setting works properly.
        self.set_dimensions_to_100pc()

        # Print all JS classes
        ParallelEventContainer.print_js_class(self.out)
        SequentialEventContainer.print_js_class(self.out)
        PathEvent.print_js_class(self.out)
        CameraEvent.print_js_class(self.out)

        self.js_event_idx = "event_idx"
        self.js_event_list = "event_list"
        self.print(f'let {self.js_event_list} = []')

        self.js_listen_to_kb = 'listen_to_kb'
        self.print(f'let {self.js_listen_to_kb} = false')

        self.js_foo_next_frame = 'next_frame'
        self._print_next_frame_foo()

        self._print_keyboard_event_foo()

    def _print_next_frame_foo(self):
        self.print(f'''
          let handle = 0;
          function {self.js_foo_next_frame}(timestamp) {{
            if ({self.js_event_idx} == {self.js_event_list}.length) {{
              window.cancelAnimationFrame(handle);
              return
            }}

            let finished = {self.js_event_list}[{self.js_event_idx}].process_event(timestamp);
            if (finished) {{
              window.cancelAnimationFrame(handle);
              {self.js_listen_to_kb} = true;
              {self.js_event_idx}++;
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
          }}, false);''')

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

    def start_animation(self):
        """Output JS call to function that starts the animation."""

        self.print(f'window.requestAnimationFrame({self.js_foo_next_frame})')
