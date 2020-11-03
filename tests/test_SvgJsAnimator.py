from svganimator.SvgJsAnimator import SvgJsAnimator
from svganimator.SvgVisitors import SimpleVisitor
import io
import unittest
import xml.etree.ElementTree as ET


class TestSvgJsAnimator(unittest.TestCase):
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
        events = visitor.visit_root(TestSvgJsAnimator.nested_root)
        animator = SvgJsAnimator(out, events, TestSvgJsAnimator.nested_root)

        out = out.getvalue()

        cam_event = events[0]
        seq_container = events[1]
        self.assertIn(
            f'let {animator.js_event_idx} = 0',
            out)
        self.assertIn(
            f'let {animator.js_event_list} = [{cam_event.js_name}, {seq_container.js_name}]',
            out)

        self.assertIn(f'function {animator.js_foo_next_frame}', out)
        self.assertIn(f'function {animator.js_foo_undo_last_event}', out)
        self.assertIn(
            f'{animator.js_svg_root}.setAttribute("width" , "100%")', out)
        self.assertIn(
            f'{animator.js_svg_root}.setAttribute("height", "80%")', out)
        self.assertIn(f"document.addEventListener('keydown', (event)", out)
        self.assertIn(
            f'{animator.js_svg_root}.onpointerdown = pointerdown_handler;',
            out)


if __name__ == '__main__':
    unittest.main()
