from svganimator import SvgUtils
from svganimator.PathEvent import PathEvent
import io
import unittest
import xml.etree.ElementTree as ET


class TestPathEvent(unittest.TestCase):
    root = ET.fromstring('''
      <svg
         xmlns="http://www.w3.org/2000/svg"
         xmlns:svg="http://www.w3.org/2000/svg"
         id="root_id">
         <path id="path0"/>
      </svg>
      ''')
    path = SvgUtils.svg_paths(root)[0]

    def test_ctor(self):
        buff = io.StringIO()
        event = PathEvent(TestPathEvent.path, buff)
        self.assertIsNotNone(event.js_name)

        out = buff.getvalue()
        self.assertRegex(out, f'let {event.js_name} = new PathEvent')
        self.assertRegex(out, f'{event.js_name}.clear_from_screen()')

    def test_print_class(self):
        buff = io.StringIO()
        PathEvent.print_js_class(buff)
        out = buff.getvalue()
        self.assertIn('class PathEvent', out)
        self.assertIn('constructor(path)', out)
        self.assertIn('process_event(elapsed, finish_requested)', out)
        self.assertIn('clear_from_screen()', out)
        self.assertIn('undo()', out)


if __name__ == '__main__':
    unittest.main()
