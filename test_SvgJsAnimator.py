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
</svg>
''')

group = SvgUtils.svg_groups(root)[0]
group_no_id = SvgUtils.svg_groups(root)[1]
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
.*strokeDasharray = (?P<length>.*) \+ " " \+ (?P=length)
.*strokeDashoffset = (?P=length)''')
        self.assertRegex(
            out_str,
            f'function {animator.js_next_frame_foo}\(.*\) {{')


if __name__ == '__main__':
    unittest.main()
