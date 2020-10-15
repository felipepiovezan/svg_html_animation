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
    <path/>
  </g>
</svg>
''')

group = SvgUtils.svg_groups(root)[0]
path = SvgUtils.svg_paths(group)[0]
path_no_id = SvgUtils.svg_paths(group)[1]


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


if __name__ == '__main__':
    unittest.main()
