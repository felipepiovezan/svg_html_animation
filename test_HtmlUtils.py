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

    def test_html_ctx(self):
        buff = io.StringIO()
        printer = Html.HtmlPrinter(buff, "buffer")
        with printer.html_ctx() as _:
            self.assertEqual(buff.getvalue(), "<html>\n")
            printer.print("hello")
            self.assertEqual(buff.getvalue(), "<html>\nhello\n")
        self.assertEqual(buff.getvalue(), "<html>\nhello\n</html>\n")

    def test_js_ctx(self):
        buff = io.StringIO()
        printer = Html.HtmlPrinter(buff, "buffer")
        with printer.js_ctx() as _:
            self.assertEqual(buff.getvalue(), "<script>\n")
            printer.print("hello")
            self.assertEqual(buff.getvalue(), "<script>\nhello\n")
        self.assertEqual(buff.getvalue(), "<script>\nhello\n</script>\n")


if __name__ == '__main__':
    unittest.main()
