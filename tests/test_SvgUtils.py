from svganimator import SvgUtils as Svg
import io
import unittest
import xml.etree.ElementTree as ET


class Input1:
    root = ET.fromstring('''
      <svg>
        <g id="group0">
          <path id="path0_0" />
        </g>
        <g id="group1">
          <path id="path1_0" />
          <path id="path1_1" />
        </g>
      </svg>
      ''')

    def inspect_groups(groups, tester: unittest.TestCase):
        tester.assertEqual(len(groups), 2)
        tester.assertEqual(Svg.get_id(groups[0]), "group0")
        tester.assertEqual(Svg.get_id(groups[1]), "group1")
        paths0 = Svg.filter(groups[0], lambda x: x.tag == 'path')
        tester.assertEqual(Svg.get_id(paths0[0]), "path0_0")


class Input2:
    root = ET.fromstring('''
        <svg id="rootid">
        </svg>
        ''')

    def inspect_groups(groups, tester: unittest.TestCase):
        tester.assertEqual(len(groups), 0)


class TestFilterMethods(unittest.TestCase):

    def test_get_id(self):
        with self.assertRaises(AssertionError):
            Svg.get_id(Input1.root)
        id = Svg.get_id(Input2.root)
        self.assertEqual(id, "rootid")

    def test_filter(self):
        groups = Svg.filter(Input1.root, lambda x: x.tag == 'g')
        Input1.inspect_groups(groups, self)
        groups = Svg.filter(Input2.root, lambda x: x.tag == 'g')
        Input2.inspect_groups(groups, self)

    def test_filter_tag(self):
        groups = Svg.filter_tag(Input1.root, 'g')
        Input1.inspect_groups(groups, self)
        groups = Svg.filter_tag(Input2.root, 'g')
        Input2.inspect_groups(groups, self)

    def test_filter_named(self):
        g0 = Svg.svg_elements_named("group0", Input1.root)[0]
        g1 = Svg.svg_elements_named("group1", Input1.root)[0]
        Input1.inspect_groups([g0, g1], self)
        empty = Svg.svg_elements_named("", Input2.root)
        Input2.inspect_groups(empty, self)


class Input3:
    root = ET.fromstring('''
      <svg
         xmlns="http://www.w3.org/2000/svg"
         xmlns:svg="http://www.w3.org/2000/svg">
        <g id="group0">
          <path id="path0_0" />
        </g>
        <g id="group1">
          <path id="path1_0" />
          <path id="path1_1" />
        </g>
        <rect id="rect1"
          width="8"
          height="8"
          x="8"
          y="8"/>
      </svg>
      ''')

    def inspect_groups(groups, tester: unittest.TestCase):
        tester.assertEqual(len(groups), 2)
        tester.assertEqual(Svg.get_id(groups[0]), "group0")
        tester.assertEqual(Svg.get_id(groups[1]), "group1")
        tester.assertEqual(Svg.get_id(groups[0][0]), "path0_0")
        tester.assertEqual(Svg.get_id(groups[1][0]), "path1_0")
        tester.assertEqual(Svg.get_id(groups[1][1]), "path1_1")

    def inspect_paths_root(paths, tester: unittest.TestCase):
        tester.assertEqual(len(paths), 0)

    def inspect_paths_group0(paths, tester: unittest.TestCase):
        tester.assertEqual(len(paths), 1)
        tester.assertEqual(Svg.get_id(paths[0]), "path0_0")

    def inspect_paths_group1(paths, tester: unittest.TestCase):
        tester.assertEqual(len(paths), 2)
        tester.assertEqual(Svg.get_id(paths[0]), "path1_0")
        tester.assertEqual(Svg.get_id(paths[1]), "path1_1")

    def inspect_rectangles(rectangles, tester: unittest.TestCase):
        tester.assertEqual(len(rectangles), 1)
        tester.assertEqual(Svg.get_id(rectangles[0]), "rect1")


class TestSvgMethods(unittest.TestCase):

    def test_svg_groups(self):
        groups = Svg.svg_groups(Input3.root)
        for group in groups:
            self.assertTrue(Svg.is_group(group))
        Input3.inspect_groups(groups, self)

    def test_svg_paths(self):
        paths_root = Svg.svg_paths(Input3.root)
        for path in paths_root:
            self.assertTrue(Svg.is_path(path))

        groups = Svg.svg_groups(Input3.root)
        for group in groups:
            self.assertTrue(Svg.is_group(group))

        paths_g0 = Svg.svg_paths(groups[0])
        for path in paths_g0:
            self.assertTrue(Svg.is_path(path))
        paths_g1 = Svg.svg_paths(groups[1])
        for path in paths_g1:
            self.assertTrue(Svg.is_path(path))

        rectangles = Svg.svg_rectangles(Input3.root)
        for rectangle in rectangles:
            self.assertTrue(Svg.is_rectangle(rectangle))

        Input3.inspect_paths_root(paths_root, self)
        Input3.inspect_paths_group0(paths_g0, self)
        Input3.inspect_paths_group1(paths_g1, self)
        Input3.inspect_rectangles(rectangles, self)


class TestHideNode(unittest.TestCase):
    def test_hide_node(self):
        for group in Svg.svg_groups(Input3.root):
            node_id = Svg.get_id(group)
            buff = io.StringIO()
            Svg.hide_svg_obj(group, buff)
            self.assertIn(
                f'let obj = document.getElementById("{node_id}");\n'
                f'obj.style.opacity = 0', buff.getvalue())


if __name__ == '__main__':
    unittest.main()
