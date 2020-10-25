from CameraEvent import CameraEvent
from ParallelEventContainer import ParallelEventContainer
from PathEvent import PathEvent
from SequentialEventContainer import SequentialEventContainer
from SvgVisitors import SimpleVisitor
import io
import unittest
import xml.etree.ElementTree as ET


class TestSimpleVisitor(unittest.TestCase):
    empty_root = ET.fromstring('''
      <svg
         xmlns="http://www.w3.org/2000/svg"
         xmlns:svg="http://www.w3.org/2000/svg"
         id="root_id">
      </svg>''')

    def test_empty_root(self):
        out = io.StringIO()
        visitor = SimpleVisitor(out)
        events = visitor.visit_root(TestSimpleVisitor.empty_root)
        self.assertEqual(len(events), 0)

    flat_root = ET.fromstring('''
      <svg
         xmlns="http://www.w3.org/2000/svg"
         xmlns:svg="http://www.w3.org/2000/svg"
         id="root_id">
         <rect
            id="cam0"
            x="10"
            y="20"
            width="30"
            height="40"/>
         <path id="path0"/>
         <g id="empty_group"/>
         <g id="par_empty_group"/>
      </svg>''')

    def test_flat_root(self):
        out = io.StringIO()
        visitor = SimpleVisitor(out)
        events = visitor.visit_root(TestSimpleVisitor.flat_root)
        self.assertEqual(len(events), 4)

        cam_event = events[0]
        self.assertIsInstance(cam_event, CameraEvent)
        self.assertEqual(cam_event.duration, 0)
        self.assertEqual(cam_event.new_cam, [10, 20, 30, 40])

        path_event = events[1]
        self.assertIsInstance(path_event, PathEvent)

        seq_container = events[2]
        self.assertIsInstance(seq_container, SequentialEventContainer)

        par_container = events[3]
        self.assertIsInstance(par_container, ParallelEventContainer)

    nested_root = ET.fromstring('''
      <svg
         xmlns="http://www.w3.org/2000/svg"
         xmlns:svg="http://www.w3.org/2000/svg"
         id="root_id">
         <rect
            id="cam0"
            x="10"
            y="20"
            width="30"
            height="40"/>
         <g id="seq_group">
            <path id="path0"/>
            <g id="par_group">
              <path id="path1"/>
              <path id="path2"/>
              <path id="path3"/>
            </g>
         </g>
      </svg>''')

    def test_grouped_root(self):
        out = io.StringIO()
        visitor = SimpleVisitor(out)
        events = visitor.visit_root(TestSimpleVisitor.nested_root)
        self.assertEqual(len(events), 2)

        cam_event = events[0]
        self.assertIsInstance(cam_event, CameraEvent)
        self.assertEqual(cam_event.duration, 0)
        self.assertEqual(cam_event.new_cam, [10, 20, 30, 40])

        seq_container = events[1]
        self.assertIsInstance(seq_container, SequentialEventContainer)

        nested_events = seq_container.events
        self.assertEqual(len(nested_events), 2)
        self.assertIsInstance(nested_events[0], PathEvent)
        self.assertIsInstance(nested_events[1], ParallelEventContainer)

        nested2_events = nested_events[1].events
        self.assertEqual(len(nested2_events), 3)
        for event in nested2_events:
            self.assertIsInstance(event, PathEvent)


if __name__ == '__main__':
    unittest.main()