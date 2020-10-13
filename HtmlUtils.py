
class HtmlPrinter:
    """Helper class for outputting HTML to a file."""

    def __init__(self, obj, mode="filename"):
        """Create a new instance of HtmlPrinter that outputs to `obj`.

        If mode is `filename`, obj is expected to be the name of a file, which
        gets opened for writing and its contents are overwritten (if such file
        already exists).

        If mode is `buffer`, `obj` is used as is and it is expected to be
        usable as the `file` argument of `print`.
        """

        if mode == "filename":
            self.file = open(obj, "w")
        if mode == "buffer":
            self.file = obj

    def print(self, to_print=""):
        """Outputs `to_print` to the buffer specified during construction."""

        print(to_print, file=self.file)
