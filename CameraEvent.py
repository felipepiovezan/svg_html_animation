import SvgUtils


class CameraEvent:
    """Class to create a camera animation.

    Advances each (x, y, width, heigh) component of the camera into the
    direction of the new camera.

    If the value of `old_cam` is meaningless, e.g. not known during the
    start of the animation, an arbitrary value can be passed as long as
    duration = 0, since duration = 0 implies immediately setting the camera
    to `new_cam`. Attempting to undo a CameraEvent in this case will set
    the camera to the meaningless value.

    Requires elapsed starting at 0, i.e., it must be placed inside a
    container providing this abstraction.
    """

    def __init__(self, old_cam, new_cam, duration, svg_root, out):
        assert SvgUtils.is_root(svg_root)
        root_id = SvgUtil.get_id(svg_root)

        self.js_name = CameraEvent.gen_unique_name()
        self.new_cam = new_cam
        self.old_cam = old_cam
        self.duration = duration
        self.out = out
        old_cam_str = ", ".join(old_cam) if old_cam is not None else "undefined"
        new_cam_str = ", ".join(new_cam)
        print(f'let {self.js_name} = new CameraEvent('
              f'[{self.old_cam_str}], [{self.new_cam_str}], '
              f'{duration}, {root})', file=out)

    def print_js_class(out):
        print(f'''
            class CameraEvent {{
              constructor(old_cam, new_cam, duration, root) {{
                this.old_cam = old_cam;
                this.new_cam = new_cam;
                this.duration = duration;
                this.root = root;
              }}

              process_event(elapsed) {{
                if (this.duration === 0) {{
                  this.root.setAttribute("viewBox", this.new_cam.join(" "));
                  return true;
                }}
                const progress = Math.min(1, elapsed / this.duration);
                const total_delta = this.new_cam.map((n, idx) => n - this.old_cam[idx]);
                const cam = this.old_cam.map((n, idx) => n + progress * total_delta[idx])
                this.root.setAttribute("viewBox", cam.join(" "));
                return progress === 1;
              }}
            }}''', file=out)

    gid = -1

    def gen_unique_name():
        CameraEvent.gid += 1
        return 'p' + str(CameraEvent.gid)
