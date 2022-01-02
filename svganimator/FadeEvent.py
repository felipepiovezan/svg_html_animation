from svganimator import SvgUtils
import xml.etree.ElementTree as ET


class FadeEvent:
    """Class to create a fade animation.

    Manipulates the opacity property of objects in order to create a fade-int
    animation.

    The time taken to reach full opacity is proportional to the perimeter.
    """

    def __init__(self, node: ET.Element, out):
        """Creates a FadeEvent from an SVG Circle node.

        Note that process_event takes as an argument the number of milliseconds
        elapsed since this event began.
        """

        html_id = SvgUtils.get_id(node)
        js_query = f'document.getElementById("{html_id}")'
        self.js_name = FadeEvent.gen_unique_name()
        print(f'let {self.js_name} = new FadeEvent({js_query})', file=out)
        print(f'{self.js_name}.clear_from_screen()', file=out)

    def print_js_class(out):
        print(f'''
            class FadeEvent {{
              constructor(obj, total_time = 0.1) {{
                this.obj = obj;
                this.total_time = total_time;
              }}

              // Draws objs on the screen based on time elapsed and draw speed.
              // Returns true if the obj has been drawn entirely.
              process_event(elapsed, finish_requested) {{
                const percentage = elapsed/this.total_time;
                let progress = Math.min(1, percentage);
                if (finish_requested)
                  progress = 1
                this.obj.style.opacity = progress;
                return progress === 1;
              }}

              // Clears the obj from screen
              clear_from_screen() {{
                this.obj.style.opacity = 0;
              }}

              undo() {{
                this.clear_from_screen();
              }}
            }}''', file=out)

    gid = -1

    def gen_unique_name():
        FadeEvent.gid += 1
        return '_fadeobj' + str(FadeEvent.gid)
