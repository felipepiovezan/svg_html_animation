from svganimator.HtmlUtils import HtmlPrinter
from svganimator.SvgVisitors import SimpleVisitor
from svganimator.SvgJsAnimator import SvgJsAnimator
import xml.etree.ElementTree as ET
import sys

assert len(sys.argv) == 3, "Incorrect number of arguments"
svg_filename = sys.argv[1]
output_filename = sys.argv[2]

html = HtmlPrinter(output_filename)
with html.html_ctx():
    with open('examples/instructions.svg', "r") as svg_file:
        html.print(svg_file.read())
    with open(svg_filename, "r") as svg_file:
        html.print(svg_file.read())

with html.js_ctx():
    root = ET.parse(svg_filename).getroot()
    events = SimpleVisitor(html.file).visit_root(root)
    animator = SvgJsAnimator(html.file, events, root)
    animator.start_animation()
