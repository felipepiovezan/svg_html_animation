from svganimator import SvgUtils
from svganimator.FadeEvent import FadeEvent
import io
import unittest
import xml.etree.ElementTree as ET


class TestFadeEvent(unittest.TestCase):
    root = ET.fromstring('''
      <svg
         xmlns="http://www.w3.org/2000/svg"
         xmlns:svg="http://www.w3.org/2000/svg"
         id="root_id">
         <circle id="circle0"/>
      </svg>
      ''')
    circle = SvgUtils.svg_circles(root)[0]

    def test_ctor(self):
        buff = io.StringIO()
        event = FadeEvent(TestFadeEvent.circle, buff)
        self.assertIsNotNone(event.js_name)

        out = buff.getvalue()
        self.assertRegex(out, f'let {event.js_name} = new FadeEvent')
        self.assertRegex(out, f'{event.js_name}.clear_from_screen()')

    def test_print_class(self):
        buff = io.StringIO()
        FadeEvent.print_js_class(buff)
        out = buff.getvalue()
        self.assertIn('class FadeEvent', out)
        self.assertIn('constructor(obj, total_time = 0.1)', out)
        self.assertIn('process_event(elapsed, finish_requested)', out)
        self.assertIn('clear_from_screen()', out)
        self.assertIn('undo()', out)


if __name__ == '__main__':
    unittest.main()
