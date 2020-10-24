from HtmlUtils import HtmlPrinter
import xml.etree.ElementTree as ET

html = HtmlPrinter("temp.html")
with html.html_ctx():
    with open("example.svg", "r") as svg_file:
        html.print(svg_file.read())

with html.js_ctx():
    root = ET.parse('example.svg').getroot()
