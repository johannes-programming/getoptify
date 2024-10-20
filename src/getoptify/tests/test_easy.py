import getopt
import unittest
from unittest.mock import patch

from getoptify.core import command, decorator, process


class TestCommandFunctions(unittest.TestCase):

    def test_command_creates_partial_decorator(self):
        # Test if command creates a partial function of decorator
        partial_decorator = command(shortopts="a:")
        self.assertTrue(callable(partial_decorator))
        self.assertEqual(partial_decorator.keywords["shortopts"], "a:")

    def test_decorator_modifies_function(self):
        # Test if decorator modifies a function as expected
        @command(shortopts="b:")
        def sample_func(args):
            return args

        with patch("sys.argv", ["prog", "-b", "value"]):
            self.assertEqual(sample_func(), ["-bvalue", "--"])

    def test_process_with_short_options(self):
        # Test process function with short options
        args = ["-a", "value1", "-b", "value2"]
        result = process(args, shortopts="ab:")
        self.assertEqual(result, ["-a", "-bvalue2", "--", "value1"])

    def test_process_with_long_options(self):
        # Test process function with long options
        args = ["--option1", "value1", "--option2=value2"]
        result = process(args, shortopts="", longopts=["option1", "option2="])
        self.assertEqual(result, ["--option1", "--option2=value2", "--", "value1"])

    def test_process_with_positional_arguments(self):
        # Test process function with positional arguments included
        args = ["pos1", "--option1", "value1", "pos2"]
        result = process(args, shortopts="", longopts=["option1="])
        self.assertEqual(result, ["--option1=value1", "--", "pos1", "pos2"])

    def test_process_without_allow_argv(self):
        # Test process function with allow_argv set to False
        with self.assertRaises(TypeError):
            with patch("sys.argv", ["prog", "-c", "value"]):
                process(None, shortopts="c:", allow_argv=False)

    def test_process_with_unsupported_longopt(self):
        # Test process function with unsupported long option
        args = ["--unsupported", "value"]
        with self.assertRaises(getopt.GetoptError):
            process(args, shortopts="", longopts=["supported"])


if __name__ == "__main__":
    unittest.main()
