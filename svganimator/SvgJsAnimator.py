from svganimator import SvgUtils
import xml.etree.ElementTree as ET


class SvgJsAnimator:
    """Creates animations by manipulating HTML properties of SvgPaths using JS.

    Through the manipulation of `style.strokeDasharray` and
    `style.strokeDashoffset`, this class is able to hide or display [pieces of]
    paths. By interacting with the `window.requestAnimationFrame` interface, it
    creates the effect that paths are being drawn gradually.

    No more than one such object should be created for the same file, as it
    relies on global state for some of its functions.
    """

    def __init__(self, out, events, svg_root: ET.Element):
        """Prints the boilerplate JS code to `out`.

        Initializes the camera to be the bounding box of the entire svg.
        Sets the svg height and width to 100%, effectively fitting the entire
        file to the space allocated for the svg container.

        The animation event queue is set to `events`, which must be an array
        of [Path|Camera]Events or [Parallel|Sequential]Containers.

        A pause is inserted between two consecutive elements of `events`, and
        the animation is resumed upon certain keyboard events.
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

        # Print variables associated with event list.
        self.js_event_idx = 'event_idx'
        self.print(f'let {self.js_event_idx} = 0')
        self.js_event_list = 'event_list'
        events_str = ', '.join([event.js_name for event in events])
        self.print(f'let {self.js_event_list} = [{events_str}]')

        self.js_ongoing_animation = 'ongoing_animation'
        self.print(f'let {self.js_ongoing_animation} = true')

        self.js_foo_next_frame = 'next_frame'
        self._print_next_frame_foo()

        self.js_foo_undo_last_event = 'undo_last_event'
        self._print_undo_last_event_foo()

        self._print_keyboard_event_foo()
        self._print_pointer_event_foo()

    def _print_next_frame_foo(self):
        self.print(f'''
          let handle = 0;
          let last_timestamp = undefined;
          function {self.js_foo_next_frame}(timestamp) {{
            if (last_timestamp === undefined)
              last_timestamp = timestamp
            timestamp = timestamp - last_timestamp
            if ({self.js_event_idx} == {self.js_event_list}.length) {{
              window.cancelAnimationFrame(handle);
              {self.js_ongoing_animation} = false;
              return;
            }}

            let finished = {self.js_event_list}[{self.js_event_idx}].process_event(timestamp);
            if (finished) {{
              window.cancelAnimationFrame(handle);
              {self.js_ongoing_animation} = false;
              {self.js_event_idx}++;
              last_timestamp = undefined
              return;
            }}
            {self.js_ongoing_animation} = true;
            handle = window.requestAnimationFrame({self.js_foo_next_frame});
          }}''')

    def _print_undo_last_event_foo(self):
        self.print(f'''
          function {self.js_foo_undo_last_event}() {{
            if ({self.js_event_idx} == 0)
              return;
            {self.js_event_idx}--;
            {self.js_event_list}[{self.js_event_idx}].undo();
          }}''')

    def _print_keyboard_event_foo(self):
        self.print(f'''
          function onNextInput() {{
            if (!{self.js_ongoing_animation}) {{
              handle = window.requestAnimationFrame({self.js_foo_next_frame});
            }}
          }}
          function onPreviousInput() {{
            if (!{self.js_ongoing_animation}) {{
              {self.js_foo_undo_last_event}();
            }}
          }}
        ''')
        self.print(f'''
          document.addEventListener('keydown', (event) => {{
            switch (event.key) {{
              case "Down": // IE/Edge
              case "ArrowDown":
              case "Right": // IE/Edge
              case "ArrowRight":
              case "Enter":
              case " ":
                onNextInput();
                return;
              case "Up": // IE/Edge
              case "ArrowUp":
              case "Left": // IE/Edge
              case "ArrowLeft":
                onPreviousInput();
                return;
              default:
                return;
            }}
          }}, false);''')

    def _print_pointer_event_foo(self):
        self.print(f'''
          function pointerdown_handler(event) {{
            if (!event.isPrimary)
              return;
            const svg_width = {self.js_svg_root}.clientWidth;
            if (event.clientX > .7 * svg_width) {{
              onNextInput();
              return;
            }}
            if (event.clientX < .3 * svg_width) {{
              onPreviousInput();
              return;
            }}
          }}
          // Note the use of `svg_root` as opposed to `document`, since we
          // we only process click events targeting the SVG area.
          {self.js_svg_root}.onpointerdown = pointerdown_handler;''')

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
