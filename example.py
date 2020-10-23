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

    # The list constructor is required to convert an ET.Element into a list
    # containing all of its children.
    rectangles = list(SvgUtils.svg_elements_named("cameras", root)[0])
    groups = list(SvgUtils.svg_elements_named("to_draw", root)[0])

    animator = SvgJsAnimator(html.file, root)
    animator.set_initial_camera(rectangles[0])

    animator.add_paths_in_group_to_queue(groups[0])
    animator.add_stop_event_to_queue()

    animator.add_camera_event_to_queue(rectangles[1])
    [(animator.add_paths_in_group_to_queue(g), animator.add_stop_event_to_queue())
     for g in groups[1:]]
    animator.add_camera_event_to_queue(rectangles[2])

    animator.clear_paths_from_screen()
    animator.start_animation()
