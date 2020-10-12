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


class TestStringMethods(unittest.TestCase):

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


if __name__ == '__main__':
    unittest.main()
