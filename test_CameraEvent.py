import io
from CameraEvent import CameraEvent
import SvgUtils
import HtmlUtils as Html
import xml.etree.ElementTree as ET
import unittest


class TestCameraEvent(unittest.TestCase):
    root = ET.fromstring('''
      <svg
         xmlns="http://www.w3.org/2000/svg"
         xmlns:svg="http://www.w3.org/2000/svg"
         id="root_id">
      </svg>
      ''')

    def test_ctor_with_old_cam(self):
        old_cam = [0, 1, 2, 3]
        new_cam = [4, 5, 6, 7]
        duration = 1717
        buff = io.StringIO()

        event = CameraEvent(
            old_cam,
            new_cam,
            duration,
            TestCameraEvent.root,
            buff)

        self.assertIsNotNone(event.js_name)
        self.assertEqual(event.new_cam, new_cam)
        self.assertEqual(event.old_cam, old_cam)
        self.assertEqual(event.duration, duration)

        root_id = SvgUtils.get_id(TestCameraEvent.root)
        out = buff.getvalue()

        self.assertRegex(
            out, rf'{event.js_name} = new CameraEvent\('
            f'\[0, 1, 2, 3\], \[4, 5, 6, 7\], {duration}, {root_id}\)')

    def test_ctor_no_old_cam(self):
        new_cam = [4, 5, 6, 7]
        duration = 0
        buff = io.StringIO()

        event = CameraEvent(
            None,
            new_cam,
            duration,
            TestCameraEvent.root,
            buff)

        self.assertIsNotNone(event.js_name)
        self.assertEqual(event.new_cam, new_cam)
        self.assertIsNone(event.old_cam)
        self.assertEqual(event.duration, duration)

        root_id = SvgUtils.get_id(TestCameraEvent.root)
        out = buff.getvalue()

        self.assertRegex(
            out, rf'{event.js_name} = new CameraEvent\('
            f'undefined, \[4, 5, 6, 7\], {duration}, {root_id}\)')

    def test_ctor_no_old_cam_not_zero_duration(self):
        new_cam = [4, 5, 6, 7]
        duration = 17
        buff = io.StringIO()

        with self.assertRaises(AssertionError):
            event = CameraEvent(
                None,
                new_cam,
                duration,
                TestCameraEvent.root,
                buff)

    def test_print_class(self):
        buff = io.StringIO()
        CameraEvent.print_js_class(buff)
        out = buff.getvalue()

        self.assertIn('class CameraEvent', out)
        self.assertIn('constructor(old_cam, new_cam, duration, root) {', out)
        self.assertIn('process_event(elapsed)', out)


if __name__ == '__main__':
    unittest.main()
