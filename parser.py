import xml.etree.ElementTree as ET


def filter(root, predicate):
    return [child for child in root if predicate(child)]

def filter_tag(root, tag):
    return filter(root, lambda x : x.tag == tag)

svg_namespace = '{http://www.w3.org/2000/svg}'
title_tag = svg_namespace + 'title'
def titles(root: ET.Element):
    return filter_tag(root, title_tag)
group_tag = svg_namespace + 'g'
def groups(root: ET.Element):
    return filter_tag(root, group_tag)
paths_tag = svg_namespace + 'path'
def paths(root: ET.Element):
    return filter_tag(root, paths_tag)

class SvgPath:
    gid = -1
    def gen_unique_name():
        SvgPath.gid += 1
        return 'path' + str(SvgPath.gid)

    def __init__(self, node : ET.Element, printer):
        self.printer = printer
        self.node = node
        self.name_js = SvgPath.gen_unique_name()
        self.html_id = node.get("id")
        self.__declare()

    def __declare(self):
        query_js = f'document.getElementById("{self.html_id}")'
        self.printer.print(f'let {self.name_js} = {{path: {query_js}, length: {query_js}.getTotalLength()}}')


class SvgGroup:
    gid = -1
    def gen_unique_name():
        SvgGroup.gid += 1
        return 'group' + str(SvgGroup.gid)

    def __init__(self, node : ET.Element, printer):
        self.printer = printer
        self.node = node
        self.name_js = SvgGroup.gen_unique_name()
        self.paths = [SvgPath(path, printer) for path in paths(node)]
        self.__declare()

    def __declare(self):
        list_str = ', '.join([f'{path.name_js}' for path in self.paths])
        self.printer.print(f'let {self.name_js} = [{list_str}]')

    def clear_strokes(self):
        for idx, path in enumerate(self.paths):
          curr_obj_js = f'{self.name_js}[{idx}]'
          curr_length_js = f'{self.name_js}[{idx}].length'
          self.printer.print(f'{curr_obj_js}.path.style.strokeDasharray = {curr_length_js} + " " + {curr_length_js}')
          self.printer.print(f'{curr_obj_js}.path.style.strokeDashoffset = {curr_length_js}')


class SvgAnimator:
  def __init__(self, printer):
    self.printer = printer
    self.paths_to_draw_js = 'paths_to_draw'
    self.printer.print(f'let {self.paths_to_draw_js} = []')
    self.drawing_idx_js = 'drawing_idx'
    self.printer.print(f'let {self.drawing_idx_js} = 0')
    self.length_per_ms = .5
    self.draw_func_js = 'step'
    self.__print_draw_function()
  def __print_draw_function(self):
    current_path_js = f'{self.paths_to_draw_js}[{self.drawing_idx_js}]'
    self.printer.print(f'''
    let start;
    let handle = 0;
    function {self.draw_func_js}(timestamp) {{
      if ({self.drawing_idx_js} == {self.paths_to_draw_js}.length) {{
        window.cancelAnimationFrame(handle);
        return
      }}

      if (start === undefined)
        start = timestamp;

      const elapsed = timestamp - start;
      const total_time =  {current_path_js}.length / {self.length_per_ms};
      const percentage = elapsed/total_time
      const progress = Math.min(1, percentage)
      {current_path_js}.path.style.strokeDashoffset = Math.floor({current_path_js}.length * (1 - progress));
      handle = window.requestAnimationFrame(step);

      if (progress === 1) {{
        start = timestamp;
        {self.drawing_idx_js}++;
      }}
    }}
    ''')
  def add_path_to_draw(self, path: SvgPath):
    self.printer.print(f'{self.paths_to_draw_js}.push({path.name_js})')
  def add_group_to_draw(self, group: SvgGroup):
    for path in group.paths:
      self.add_path_to_draw(path)
  def start_animation(self):
    self.printer.print(f'window.requestAnimationFrame({self.draw_func_js})')

class Hprinter:
    def __init__(self, filename:str):
        self.file = open(filename, "w")
        self.to_draw_js = 'to_draw'
    def print(self, to_print):
        print(to_print, file=self.file)
    def begin_html(self):
        self.print('<!DOCTYPE html>')
        self.print('<html>')
    def end_html(self):
        self.print('</html>')
    def begin_script(self):
        self.print('<script>')
    def end_script(self):
        self.print('</script>')
    def svg_from_file(self, filename):
        with open(filename, "r") as file:
            self.print(file.read())

doc = Hprinter("test.html")
doc.begin_html()
doc.svg_from_file("twos_complement.svg")
doc.end_html()
doc.begin_script()

animator = SvgAnimator(doc)
tree = ET.parse('twos_complement.svg')
root =  tree.getroot();
groups_to_draw = [SvgGroup(group, doc) for group in groups(root)]
for svg_group in groups_to_draw:
  svg_group.clear_strokes()
  animator.add_group_to_draw(svg_group)
animator.start_animation()
doc.end_script()
