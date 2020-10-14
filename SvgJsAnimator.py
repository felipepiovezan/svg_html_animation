import xml.etree.ElementTree as ET
import SvgUtils


class SvgJsPath:
    gid = -1

    def gen_unique_name():
        SvgJsPath.gid += 1
        return 'p' + str(SvgJsPath.gid)

    def __init__(self, node: ET.Element, out):
        assert node.tag == SvgUtils._path_tag, "SvgJsPath must be created with an Svg path"
        self.out = out
        self.node = node
        self.js_name = SvgJsPath.gen_unique_name()
        self.html_id = node.get("id")
        assert self.html_id is not None, "Path should have an id value"
        self.__declare()

    def __declare(self):
        query_js = f'document.getElementById("{self.html_id}")'
        print(
            f'let {self.js_name} = {{path: {query_js}, length: {query_js}.getTotalLength()}}',
            file=self.out)
