import unittest
import SvgUtils as Svg
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
        paths0 = Svg._filter(groups[0], lambda x: x.tag == 'path')
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
        groups = Svg._filter(Input1.root, lambda x: x.tag == 'g')
        Input1.inspect_groups(groups, self)
        groups = Svg._filter(Input2.root, lambda x: x.tag == 'g')
        Input2.inspect_groups(groups, self)

    def test_filter_tag(self):
        groups = Svg._filter_tag(Input1.root, 'g')
        Input1.inspect_groups(groups, self)
        groups = Svg._filter_tag(Input2.root, 'g')
        Input2.inspect_groups(groups, self)


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
        Input3.inspect_groups(groups, self)

    def test_svg_paths(self):
        paths_root = Svg.svg_paths(Input3.root)
        groups = Svg.svg_groups(Input3.root)
        paths_g0 = Svg.svg_paths(groups[0])
        paths_g1 = Svg.svg_paths(groups[1])
        rectangles = Svg.svg_rectangles(Input3.root)
        Input3.inspect_paths_root(paths_root, self)
        Input3.inspect_paths_group0(paths_g0, self)
        Input3.inspect_paths_group1(paths_g1, self)
        Input3.inspect_rectangles(rectangles, self)


if __name__ == '__main__':
    unittest.main()
