from svganimator import SvgUtils
import xml.etree.ElementTree as ET


class CircleEvent:
    """Class to create a circle animation.

    Manipulates the opacity property of circles in order to create the illusion
    of a circle drawing itself.

    The time taken to reach full opacity is proportional to the perimeter.
    """

    def __init__(self, node: ET.Element, out):
        """Creates a CircleEvent from an SVG Circle node.

        Note that process_event takes as an argument the number of milliseconds
        elapsed since this event began.
        """

        assert SvgUtils.is_circle(node)

        html_id = SvgUtils.get_id(node)
        js_query = f'document.getElementById("{html_id}")'
        self.js_name = CircleEvent.gen_unique_name()
        print(f'let {self.js_name} = new CircleEvent({js_query})', file=out)
        print(f'{self.js_name}.clear_from_screen()', file=out)

    def print_js_class(out):
        print(f'''
            class CircleEvent {{
              constructor(circle) {{
                this.circle = circle;
                this.total_time = circle.getTotalLength() / {CircleEvent.circle_speed};
              }}

              // Draws circles on the screen based on time elapsed and draw speed.
              // Returns true if the circle has been drawn entirely.
              process_event(elapsed, finish_requested) {{
                const percentage = elapsed/this.total_time;
                let progress = Math.min(1, percentage);
                if (finish_requested)
                  progress = 1
                this.circle.style.opacity = progress;
                return progress === 1;
              }}

              // Clears the circle from screen
              clear_from_screen() {{
                this.circle.style.opacity = 0;
              }}

              undo() {{
                this.clear_from_screen();
              }}
            }}''', file=out)

    gid = -1

    def gen_unique_name():
        CircleEvent.gid += 1
        return '_circle' + str(CircleEvent.gid)

    # TODO: make this a circle paremeter.
    circle_speed = 0.4
