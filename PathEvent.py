import SvgUtils
import xml.etree.ElementTree as ET

class PathEvent:
    def __init__(self, node: ET.Element, out):
        assert SvgUtils.is_path(node)

        html_id = SvgUtils.get_id(node)
        js_query = f'document.getElementById("{html_id}")'
        self.js_name = PathEvent.gen_unique_name()
        print(f'let {self.js_name} = new PathEvent({js_query})', file=out)
        print(f'{self.js_name}.clear_from_screen()', file=out)

    def print_js_class(out):
        print(f'''
            class PathEvent {{
              constructor(path) {{
                this.path = path;
                this.length = path.getTotalLength();
                this.total_time = this.length / {PathEvent.path_speed};
              }}

              // Draws paths on the screen based on time elapsed and draw speed.
              // Returns true if the path has been drawn entirely.
              process_event(elapsed) {{
                const percentage = elapsed/this.total_time;
                const progress = Math.min(1, percentage);
                this.path.style.strokeDashoffset = Math.floor(this.length * (1 - progress));
                return progress === 1;
              }}

              // Clears the path from screen
              clear_from_screen() {{
                this.path.style.strokeDasharray = this.length + " " + this.length;
                this.path.style.strokeDashoffset = this.length;
              }}
            }}''', file=out)

    gid = -1

    def gen_unique_name():
        PathEvent.gid += 1
        return '_path' + str(PathEvent.gid)

    # TODO: make this a path paremeter.
    path_speed = 1.0
