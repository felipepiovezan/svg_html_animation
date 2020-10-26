import io
from PathEvent import PathEvent
from SequentialEventContainer import SequentialEventContainer
import SvgUtils
import xml.etree.ElementTree as ET
import unittest


class TestSequentialEventContainer(unittest.TestCase):
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
        p_event0 = PathEvent(TestSequentialEventContainer.paths[0], buff)
        p_event1 = PathEvent(TestSequentialEventContainer.paths[1], buff)
        seqEvent = SequentialEventContainer([p_event0, p_event1], buff)
        self.assertIsNotNone(seqEvent.js_name)

        buff = buff.getvalue()
        self.assertIn(
            f'let {seqEvent.js_name} = new SequentialEventContainer('
            f'[{p_event0.js_name}, {p_event1.js_name}]', buff)

    def test_print_class(self):
        buff = io.StringIO()
        SequentialEventContainer.print_js_class(buff)
        buff = buff.getvalue()
        self.assertIn('class SequentialEventContainer', buff)
        self.assertIn('constructor(events)', buff)
        self.assertIn('process_event(elapsed)', buff)
        self.assertIn('undo()', buff)


if __name__ == '__main__':
    unittest.main()
