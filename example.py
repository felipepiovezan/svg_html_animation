from HtmlUtils import HtmlPrinter
import SvgUtils
from SvgJsAnimator import SvgJsAnimator, SvgJsGroup
import xml.etree.ElementTree as ET

html = HtmlPrinter("temp.html")
with html.html_ctx():
    with open("example.svg", "r") as svg_file:
        html.print(svg_file.read())

with html.js_ctx():
    root = ET.parse('example.svg').getroot()
    animator = SvgJsAnimator(html.file, root)
    rectangles = SvgUtils.svg_rectangles(root)
    animator.set_initial_camera(rectangles[0])
    groups_to_draw = [SvgJsGroup(group, html.file)
                      for group in SvgUtils.svg_groups(root)]
    animator.add_group_to_queue(groups_to_draw[0])
    animator.add_stop_event_to_queue()
    animator.add_camera_event_to_queue(rectangles[1])
    [(animator.add_group_to_queue(g), animator.add_stop_event_to_queue())
     for g in groups_to_draw[1:]]
    animator.add_camera_event_to_queue(rectangles[2])
    animator.clear_paths_from_screen()
    animator.start_animation()
