import unittest

__all__ = ["test"]


def test():
    loader = unittest.TestLoader()
    tests = loader.discover(start_dir="getoptify.tests")
    runner = unittest.TextTestRunner()
    result = runner.run(tests)
    return result
