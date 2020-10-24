from HtmlUtils import HtmlPrinter
from SvgJsAnimator import SvgJsAnimator
import xml.etree.ElementTree as ET

html = HtmlPrinter("temp.html")
with html.html_ctx():
    with open("example.svg", "r") as svg_file:
        html.print(svg_file.read())

with html.js_ctx():
    root = ET.parse('example.svg').getroot()

    animator = SvgJsAnimator(html.file, root)

    animator.start_animation()
