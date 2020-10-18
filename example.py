from HtmlUtils import HtmlPrinter
from SvgUtils import svg_groups
from SvgJsAnimator import SvgJsAnimator, SvgJsGroup
import xml.etree.ElementTree as ET

html = HtmlPrinter("temp.html")
with html.html_ctx():
    with open("example.svg", "r") as svg_file:
        html.print(svg_file.read())

with html.js_ctx():
    animator = SvgJsAnimator(html.file)
    root = ET.parse('example.svg').getroot()
    groups_to_draw = [SvgJsGroup(group, html.file)
                      for group in svg_groups(root)]
    [(animator.add_group_to_queue(group), animator.add_stop_event_to_queue())
     for group in groups_to_draw]
    animator.clear_paths_from_screen()
    animator.start_animation()
