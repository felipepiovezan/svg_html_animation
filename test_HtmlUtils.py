import io
import HtmlUtils as Html
import unittest


class TestHtmlPrinter(unittest.TestCase):
    def test_print(self):
        buff = io.StringIO()
        printer = Html.HtmlPrinter(buff, "buffer")
        printer.print("hello")
        self.assertEqual(buff.getvalue(), "hello\n")
        printer.print("hello2")
        self.assertEqual(buff.getvalue(), "hello\nhello2\n")
        printer.print("")
        self.assertEqual(buff.getvalue(), "hello\nhello2\n\n")
        printer.print()
        self.assertEqual(buff.getvalue(), "hello\nhello2\n\n\n")


if __name__ == '__main__':
    unittest.main()
