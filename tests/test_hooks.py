import unittest

from racconto.hooks.manager import HooksManager

class MethodCallLogger(object):
    def __init__(self, meth):
        self.meth = meth
        self.was_called = False

    def __call__(self, *args):
        self.meth(*args)
        self.was_called = True

def some_hook(*args):
    pass

class TestDecorators(unittest.TestCase):
    def test_register_before_all_hook(self):
        HooksManager.register_before_all_hook(some_hook)
        self.assertEqual(len(HooksManager.before_all_hooks), 1)

    def test_register_before_each_hook(self):
        HooksManager.register_before_each_hook(some_hook)
        self.assertEqual(len(HooksManager.before_each_hooks), 1)

    def test_register_after_all_hook(self):
        HooksManager.register_after_all_hook(some_hook)
        self.assertEqual(len(HooksManager.after_all_hooks), 1)

    def test_register_after_each_hook(self):
        HooksManager.register_after_each_hook(some_hook)
        self.assertEqual(len(HooksManager.after_each_hooks), 1)

class TestRunners(unittest.TestCase):

    def setUp(self):
        self.hook = MethodCallLogger(some_hook)

    def test_run_after_each_hooks(self):
        HooksManager.after_each_hooks = [self.hook]
        HooksManager.run_after_each_hooks('')
        self.assertTrue(self.hook.was_called)

    def test_run_after_all_hooks(self):
        HooksManager.after_all_hooks = [self.hook]
        HooksManager.run_after_all_hooks([], [])
        self.assertTrue(self.hook.was_called)

    def test_run_before_all_hooks(self):
        HooksManager.before_all_hooks = [self.hook]
        HooksManager.run_before_all_hooks([], [])
        self.assertTrue(self.hook.was_called)

    def test_run_before_each_hooks(self):
        HooksManager.before_each_hooks = [self.hook]
        HooksManager.run_before_each_hooks('')
        self.assertTrue(self.hook.was_called)
