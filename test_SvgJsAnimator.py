import io
import SvgJsAnimator
import SvgUtils
import unittest
import xml.etree.ElementTree as ET

root = ET.fromstring('''
<svg
  id="svg_root"
  xmlns="http://www.w3.org/2000/svg"
  xmlns:svg="http://www.w3.org/2000/svg">
  <g id="group0">
    <path id="path0" />
  </g>
  <g/>
  <path/>

  <g id="group1">
    <path id="path10" />
    <path id="path11" />
  </g>

  <rect id="rect1"
    x="1"
    y="2"
    width="3"
    height="4"/>
  <rect id="rect2"
    x="5"
    y="6"
    width="7"
    height="8"/>
</svg>
''')

group = SvgUtils.svg_groups(root)[0]
group_no_id = SvgUtils.svg_groups(root)[1]
group_two_paths = SvgUtils.svg_groups(root)[2]
path = SvgUtils.svg_paths(group)[0]
path_no_id = SvgUtils.svg_paths(root)[0]


class TestSvgJsPath(unittest.TestCase):
    def test_invalid_init_not_path(self):
        out = io.StringIO()
        with self.assertRaises(AssertionError):
            SvgJsAnimator.SvgJsPath(root, out)

    def test_invalid_init_no_id(self):
        out = io.StringIO()
        with self.assertRaises(AssertionError):
            SvgJsAnimator.SvgJsPath(path_no_id, out)

    def test_ok_path(self):
        out = io.StringIO()
        SvgJsAnimator.SvgJsPath(path, out)
        out_str = out.getvalue()
        query_js = 'document.getElementById("path0")'
        self.assertIn(f'{{path: {query_js}', out_str)
        self.assertIn(f', length: {query_js}.getTotalLength()}}', out_str)


class TestSvgJsGroup(unittest.TestCase):
    def test_invalid_init_not_group(self):
        out = io.StringIO()
        with self.assertRaises(AssertionError):
            SvgJsAnimator.SvgJsGroup(root, out)

    def test_valid_init_no_id_and_no_paths(self):
        out = io.StringIO()
        js_group = SvgJsAnimator.SvgJsGroup(group_no_id, out)
        out_str = out.getvalue()
        self.assertIn(f'{js_group.js_name} = []', out_str)

    def test_ok_group(self):
        out = io.StringIO()
        js_group = SvgJsAnimator.SvgJsGroup(group, out)
        out_str = out.getvalue()
        self.assertIn(
            f'{js_group.js_name} = [{js_group.paths[0].js_name}]',
            out_str)


class TestSvgJsAnimator(unittest.TestCase):

    def test_foo_defs(self):
        out = io.StringIO()
        animator = SvgJsAnimator.SvgJsAnimator(out, root)
        out_str = out.getvalue()
        self.assertRegex(
            out_str,
            f'''function {animator.js_foo_clear_path}\(.*\) {{
.*if \(.* != {animator.js_kind_path}\)
.*return;
.*(?P<path_event>.*)=.*
.*(?P=path_event).forEach.*
.*const (?P<length>[a-z]*) =.*.length;
.*(?P<path>[a-z]*) =.*.path;
.*(?P=path).style.strokeDasharray = (?P=length) \+ " " \+ (?P=length);
.*(?P=path).style.strokeDashoffset = (?P=length);''')
        self.assertRegex(
            out_str,
            f'function {animator.js_foo_next_frame}\(.*\) {{')
        self.assertIn(
            f'window.requestAnimationFrame({animator.js_foo_next_frame})',
            out_str)
        self.assertIn(
            "document.addEventListener('keydown', (event) => {", out_str)

    def test_repeated_paths(self):
        out = io.StringIO()
        pathToAdd = SvgJsAnimator.SvgJsPath(path, out)
        animator = SvgJsAnimator.SvgJsAnimator(out, root)
        animator.add_path_to_queue(pathToAdd)
        with self.assertRaises(AssertionError):
            animator.add_path_to_queue(pathToAdd)
        animator.add_paths_in_group_to_queue(group_two_paths)
        with self.assertRaises(AssertionError):
            animator.add_paths_in_group_to_queue(group_two_paths)

    def test_add_path(self):
        out = io.StringIO()
        pathToAdd = SvgJsAnimator.SvgJsPath(path, out)
        animator = SvgJsAnimator.SvgJsAnimator(out, root)
        animator.add_path_to_queue(pathToAdd)
        out_str = out.getvalue()
        self.assertIn(
            f'{animator.js_animation_queue}.push({{ '
            f'{animator.js_kind_event} : {animator.js_kind_path}, '
            f'{animator.js_event_obj} : [{pathToAdd.js_name}] }})', out_str)

    def test_add_group(self):
        out = io.StringIO()
        animator = SvgJsAnimator.SvgJsAnimator(out, root)
        animator.add_paths_in_group_to_queue(group_two_paths)
        out_str = out.getvalue()
        self.assertRegex(
            out_str, rf'group[0-9]*.forEach(?s:.*)'
            rf'{animator.js_animation_queue}.push\({{.*'
            f'{animator.js_kind_event} : {animator.js_kind_path},.*'
            f'{animator.js_event_obj} : \[x\] }}')

    def test_clear_paths(self):
        out = io.StringIO()
        animator = SvgJsAnimator.SvgJsAnimator(out, root)
        animator.clear_paths_from_screen()
        out_str = out.getvalue()
        self.assertIn(
            f'{animator.js_animation_queue}.forEach(function(x) {{ '
            f'{animator.js_foo_clear_path}(x)  }});', out_str)

    def test_add_stop_event(self):
        out = io.StringIO()
        animator = SvgJsAnimator.SvgJsAnimator(out, root)
        animator.add_stop_event_to_queue()
        out_str = out.getvalue()
        self.assertIn(
            f'{animator.js_animation_queue}.push({{ '
            f'{animator.js_kind_event} : {animator.js_kind_stop_animation} }})',
            out_str)

    def test_start_animation(self):
        out = io.StringIO()
        animator = SvgJsAnimator.SvgJsAnimator(out, root)
        animator.start_animation()
        out_str = out.getvalue()
        self.assertIn(
            f'window.requestAnimationFrame({animator.js_foo_next_frame})',
            out_str)

    def test_set_dimensions_to_100pc(self):
        out = io.StringIO()
        animator = SvgJsAnimator.SvgJsAnimator(out, root)
        out_str = out.getvalue()
        svg_html_id = root.get("id")
        self.assertIn(
            f'{animator.js_svg_root}.setAttribute("width" , "100%")',
            out_str)
        self.assertIn(
            f'{animator.js_svg_root}.setAttribute("height", "100%")',
            out_str)

    def test_add_camera_event_to_queue(self):
        out = io.StringIO()
        animator = SvgJsAnimator.SvgJsAnimator(out, root)
        animator.set_initial_camera(SvgUtils.svg_rectangles(root)[0])
        animator.add_camera_event_to_queue(
            SvgUtils.svg_rectangles(root)[1], 1234)
        out_str = out.getvalue()
        self.assertIn(
            f'{animator.js_animation_queue}.push({{ '
            f'{animator.js_kind_event} : {animator.js_kind_camera}, '
            f'{animator.js_event_obj} : {{ old_cam : [1, 2, 3, 4], '
            f'new_cam : [5, 6, 7, 8], duration : 1234 }} }})', out_str)


if __name__ == '__main__':
    unittest.main()
