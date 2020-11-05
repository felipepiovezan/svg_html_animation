from svganimator import SvgUtils


class CameraEvent:
    """Class to create a camera animation.

    Advances each (x, y, width, heigh) component of the camera into the
    direction of the new camera.
    """

    def __init__(self, old_cam, new_cam, duration, svg_root, out):
        """Create a new camera event for svg_root.

        Duration = 0 implies immediately setting the camera to `new_cam`
        For the first camera event, `old_cam` should be set to `new_cam`, in
        which case there will be no camera motion.
        """

        assert old_cam is not None and new_cam is not None
        assert SvgUtils.is_root(svg_root)
        root_id = SvgUtils.get_id(svg_root)

        self.js_name = CameraEvent.gen_unique_name()
        self.new_cam = new_cam
        self.old_cam = old_cam
        self.duration = duration
        old_cam_str = str(old_cam) if old_cam is not None else "undefined"
        new_cam_str = str(new_cam)
        print(f'let {self.js_name} = new CameraEvent('
              f'{old_cam_str}, {new_cam_str}, '
              f'{duration}, {root_id})', file=out)

    def print_js_class(out):
        print(f'''
            class CameraEvent {{
              constructor(old_cam, new_cam, duration, root) {{
                this.old_cam = old_cam;
                this.new_cam = new_cam;
                this.total_delta = new_cam.map((n, idx) => n - old_cam[idx]);
                this.duration = duration;
                this.root = root;
              }}

              static smoothing(percentage) {{
                // doubleExponentialSigmoid
                const param = 0.727;
                if (percentage <= 0.5)
                  return Math.pow(2. * percentage, 1./param) / 2.;
                return 1 - Math.pow(2. * (1 - percentage), 1./param) / 2.;;
              }}

              progress(elapsed, finish_requested) {{
                if (this.duration === 0 || finish_requested)
                  return 1;
                const percentage = Math.min(1, elapsed / this.duration);
                return CameraEvent.smoothing(percentage);
              }}

              process_event(elapsed, finish_requested) {{
                const progress = this.progress(elapsed, finish_requested)
                const cam = this.old_cam.map((n, idx) => n + progress * this.total_delta[idx])
                this.root.setAttribute("viewBox", cam.join(" "));
                return progress === 1;
              }}

              undo() {{
                if (typeof this.old_cam !== "undefined")
                  this.root.setAttribute("viewBox", this.old_cam.join(" "));
              }}
            }}''', file=out)

    gid = -1

    def gen_unique_name():
        CameraEvent.gid += 1
        return '_cam' + str(CameraEvent.gid)
