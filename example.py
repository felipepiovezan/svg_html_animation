from HtmlUtils import HtmlPrinter
from SvgVisitors import SimpleVisitor
from SvgJsAnimator import SvgJsAnimator
import xml.etree.ElementTree as ET

html = HtmlPrinter("temp.html")
with html.html_ctx():
    with open("example.svg", "r") as svg_file:
        html.print(svg_file.read())

with html.js_ctx():
    root = ET.parse('example.svg').getroot()
    events = SimpleVisitor(html.file).visit_root(root)
    animator = SvgJsAnimator(html.file, events, root)
    animator.start_animation()
