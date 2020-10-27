from svganimator import SvgUtils
from svganimator.ParallelEventContainer import ParallelEventContainer
from svganimator.PathEvent import PathEvent
import io
import unittest
import xml.etree.ElementTree as ET


class TestParallelEventContainer(unittest.TestCase):
    root = ET.fromstring('''
      <svg
         xmlns="http://www.w3.org/2000/svg"
         xmlns:svg="http://www.w3.org/2000/svg"
         id="root_id">
         <path id="path0"/>
         <path id="path1"/>
      </svg>
      ''')
    paths = SvgUtils.svg_paths(root)

    def test_ctor(self):
        buff = io.StringIO()
        p_event0 = PathEvent(TestParallelEventContainer.paths[0], buff)
        p_event1 = PathEvent(TestParallelEventContainer.paths[1], buff)
        parEvent = ParallelEventContainer([p_event0, p_event1], buff)
        self.assertIsNotNone(parEvent.js_name)

        buff = buff.getvalue()
        self.assertIn(
            f'let {parEvent.js_name} = new ParallelEventContainer('
            f'[{p_event0.js_name}, {p_event1.js_name}]', buff)

    def test_print_class(self):
        buff = io.StringIO()
        ParallelEventContainer.print_js_class(buff)
        buff = buff.getvalue()
        self.assertIn('class ParallelEventContainer', buff)
        self.assertIn('constructor(events)', buff)
        self.assertIn('process_event(elapsed)', buff)
        self.assertIn('undo()', buff)


if __name__ == '__main__':
    unittest.main()
