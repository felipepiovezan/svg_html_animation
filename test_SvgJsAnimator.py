import io
import SvgJsAnimator
import SvgUtils
import unittest
import xml.etree.ElementTree as ET

root = ET.fromstring('''
<svg
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
        animator = SvgJsAnimator.SvgJsAnimator(out)
        out_str = out.getvalue()
        self.assertRegex(
            out_str,
            f'''function {animator.js_clear_path_foo}\(.*\) {{
.*if \(.*hasOwnProperty\("path"\)\) {{
.*strokeDasharray = (?P<length>.*) \+ " " \+ (?P=length)
.*strokeDashoffset = (?P=length)''')
        self.assertRegex(
            out_str,
            f'function {animator.js_next_frame_foo}\(.*\) {{')
        self.assertIn(
            f'window.requestAnimationFrame({animator.js_next_frame_foo})',
            out_str)
        self.assertIn(
            "document.addEventListener('keydown', (event) => {", out_str)

    def test_repeated_paths(self):
        out = io.StringIO()
        pathToAdd = SvgJsAnimator.SvgJsPath(path, out)
        animator = SvgJsAnimator.SvgJsAnimator(out)
        animator.add_path_to_queue(pathToAdd)
        with self.assertRaises(AssertionError):
            animator.add_path_to_queue(pathToAdd)
        groupToAdd = SvgJsAnimator.SvgJsGroup(group_two_paths, out)
        animator.add_group_to_queue(groupToAdd)
        with self.assertRaises(AssertionError):
            animator.add_group_to_queue(groupToAdd)

    def test_add_path(self):
        out = io.StringIO()
        pathToAdd = SvgJsAnimator.SvgJsPath(path, out)
        animator = SvgJsAnimator.SvgJsAnimator(out)
        animator.add_path_to_queue(pathToAdd)
        out_str = out.getvalue()
        self.assertIn(
            f'{animator.js_animation_queue}.push({pathToAdd.js_name})',
            out_str)

    def test_add_group(self):
        out = io.StringIO()
        groupToAdd = SvgJsAnimator.SvgJsGroup(group_two_paths, out)
        animator = SvgJsAnimator.SvgJsAnimator(out)
        animator.add_group_to_queue(groupToAdd)
        out_str = out.getvalue()
        self.assertIn(
            f'{groupToAdd.js_name}.forEach(function(x) {{ {animator.js_animation_queue}.push(x)  }});',
            out_str)

    def test_clear_paths(self):
        out = io.StringIO()
        animator = SvgJsAnimator.SvgJsAnimator(out)
        animator.clear_paths_from_screen()
        out_str = out.getvalue()
        self.assertIn(
            f'{animator.js_animation_queue}.forEach(function(x) {{ {animator.js_clear_path_foo}(x)  }});',
            out_str)

    def test_add_stop_event(self):
        out = io.StringIO()
        animator = SvgJsAnimator.SvgJsAnimator(out)
        animator.add_stop_event_to_queue()
        out_str = out.getvalue()
        self.assertIn(
            f'{animator.js_animation_queue}.push({animator.js_stop_animation_event});',
            out_str)


    def test_start_animation(self):
        out = io.StringIO()
        animator = SvgJsAnimator.SvgJsAnimator(out)
        animator.start_animation()
        out_str = out.getvalue()
        self.assertIn(
            f'window.requestAnimationFrame({animator.js_next_frame_foo})',
            out_str)


if __name__ == '__main__':
    unittest.main()
