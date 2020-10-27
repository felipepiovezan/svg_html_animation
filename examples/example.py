from svganimator.HtmlUtils import HtmlPrinter
from svganimator.SvgVisitors import SimpleVisitor
from svganimator.SvgJsAnimator import SvgJsAnimator
import xml.etree.ElementTree as ET
import sys

assert len(sys.argv) == 2, "Incorrect number of arguments"
svg_filename = sys.argv[1]

html = HtmlPrinter("temp.html")
with html.html_ctx():
    with open(svg_filename, "r") as svg_file:
        html.print(svg_file.read())

with html.js_ctx():
    root = ET.parse(svg_filename).getroot()
    events = SimpleVisitor(html.file).visit_root(root)
    animator = SvgJsAnimator(html.file, events, root)
    animator.start_animation()
