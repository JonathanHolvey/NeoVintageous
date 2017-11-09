from unittest import TestCase

from sublime import Region
from sublime import active_window

from NeoVintageous.lib.state import State
from NeoVintageous.lib.vi.utils import modes


def _make_region(view, a, b=None):
    try:
        pt_a = view.text_point(*a)
        pt_b = view.text_point(*b)

        return Region(pt_a, pt_b)
    except (TypeError, ValueError):
        pass

    if isinstance(a, int) and b is None:
        pass
    elif not (isinstance(a, int) and isinstance(b, int)):
        raise ValueError("a and b parameters must be either ints or (row, col)")

    if b is not None:
        return Region(a, b)
    else:
        return Region(a)


class ViewTestCase(TestCase):

    COMMAND_LINE_MODE = modes.COMMAND_LINE
    INSERT_MODE = modes.INSERT
    INTERNAL_NORMAL_MODE = modes.INTERNAL_NORMAL
    NORMAL_MODE = modes.NORMAL
    NORMAL_INSERT_MODE = modes.NORMAL_INSERT
    OPERATOR_PENDING_MODE = modes.OPERATOR_PENDING
    SELECT_MODE = modes.SELECT
    UNKNOWN_MODE = modes.UNKNOWN
    VISUAL_BLOCK_MODE = modes.VISUAL_BLOCK
    VISUAL_LINE_MODE = modes.VISUAL_LINE
    VISUAL_MODE = modes.VISUAL

    def setUp(self):
        self.view = active_window().new_file()
        self.view.set_scratch(True)

    def tearDown(self):
        if self.view:
            self.view.close()

    def settings(self):
        return self.view.settings()

    def content(self):
        return self.view.substr(Region(0, self.view.size()))

    def write(self, text):
        self.view.run_command('_neovintageous_test_write', {'text': text})

    def select(self, selections):
        # Create a selection on the view.
        #
        # All existing regions are cleared before adding the new ones.
        #
        # Args:
        #   selections (int|tuple|Region|list<int|tuple|Region>): *int* and
        #       *tuple* are converted to *Region*.
        #
        # Usage:
        #   >>> class TestExampleAssertSelection(ViewTestCase):
        #   >>>     def test_examples(self):
        #   >>>         self.select(3)
        #   >>>         self.select((3, 5))
        #   >>>         self.select([3, 5, 7])
        #   >>>         self.select([(3, 5), (7, 11))
        #   >>>         self.select([3, (7, 11), 17, (19, 23))
        #   >>>
        #   >>>         # The above is shorthand for:
        #   >>>         self.select(sublime.Region(3))
        #   >>>         self.select(sublime.Region(3, 5))
        #   >>>         self.select([sublime.Region(3), sublime.Region(5), sublime.Region(7)])
        #   >>>         self.select([sublime.Region(3, 5), sublime.Region(7, 11))
        #   >>>         self.select([sublime.Region(3), sublime.Region(7, 11),
        #   >>>                      sublime.Region(17), sublime.Region(19, 23)])

        self.view.sel().clear()

        if not isinstance(selections, list):
            selections = [selections]

        for selection in selections:
            if isinstance(selection, tuple):
                self.view.sel().add(Region(selection[0], selection[1]))
            else:
                self.view.sel().add(selection)

    def Region(self, a, b=None):
        # Return a Region with intial values a and b.
        #
        # Args:
        #   a (int): The first end of the region.
        #   b (int, optional): The second end of the region. Defaults to *a*.
        #       May be less that a, in which case the region is a reversed one.

        return Region(a, b)

    def assertRegion(self, expected, actual):
        # Test that *actual* and *expected* are equal.
        #
        # Args:
        #   expected (str|int|tuple|Region): Expected region. *int* and *tuple*
        #       are converted to *Region*. If *str*, then *actual* is converted
        #       to a *str* before testing if both are equal.
        #   actual (Region): Actual region.

        if isinstance(expected, str):
            self.assertEqual(expected, self.view.substr(actual))
        elif isinstance(expected, int):
            self.assertEqual(Region(expected), actual)
        elif isinstance(expected, tuple):
            self.assertEqual(Region(expected[0], expected[1]), actual)
        else:
            self.assertEqual(expected, actual)

    def assertContent(self, expected, msg=None):
        # Test that view contents and *expected* are equal.
        #
        # Args:
        #   expected (str): Expected view contents.
        #   msg (str, optional): If specified, is used as the error message on failure.

        self.assertEqual(self.content(), expected, msg)

    def assertContentRegex(self, expected, msg=None):
        # Test that view contents matches (or does not match) *expected*.
        #
        # Args:
        #   expected (str): Expected regular expression that should match view contents.
        #   msg (str, optional): If specified, is used as the error message on failure.

        self.assertRegex(self.content(), expected, msg)

    def assertSize(self, expected):
        # Test that number of view characters and *expected* are equal.
        #
        # Args:
        #   expected (int): Expected number of characters in view.

        self.assertEqual(expected, self.view.size())

    def assertSelection(self, expected):
        # Test that view selection and *expected* are equal.
        #
        # Args:
        #   expected (int|tuple|Region|list<Region>): *int* and *tuple* are
        #       converted to *Region* before evaluating.
        #
        # Usage:
        #   >>> class TestExampleAssertSelection(ViewTestCase):
        #   >>>     def test_example(self):
        #   >>>         # Assume the view content is:
        #   >>>         #
        #   >>>         #   "12345|6789" (where | is the cursor position)
        #   >>>
        #   >>>         self.assertSelection(5)
        #   >>>
        #   >>>         # The above assertion is shorthand for all the following:
        #   >>>         self.assertSelection((5, 5))
        #   >>>         self.assertSelection(self.Region(5))
        #   >>>         self.assertSelection(self.Region(5, 5))
        #   >>>         self.assertSelection(sublime.Region(5))
        #   >>>         self.assertSelection(sublime.Region(5, 5))
        #   >>>         self.assertSelection([5])
        #   >>>         self.assertSelection([(5, 5)])
        #   >>>         self.assertSelection([self.Region(5)])
        #   >>>         self.assertSelection([self.Region(5, 5)])
        #   >>>         self.assertSelection([sublime.Region(5)])
        #   >>>         self.assertSelection([sublime.Region(5, 5)])
        #   >>>         self.assertEqual([sublime.Region(5)], list(self.view.sel()))
        #   >>>         self.assertEqual([sublime.Region(5, 5)], list(self.view.sel()))
        #   >>>
        #   >>>     def test_visual_selection(self):
        #   >>>         # Assume the content of view is:
        #   >>>         #
        #   >>>         #   "123456789"
        #   >>>         #      ^^^^^ (where ^ is the visual selection)
        #   >>>
        #   >>>         self.assertSelection((2, 7))
        #   >>>
        #   >>>         # The above assertion is shorthand for all the following:
        #   >>>         self.assertSelection(self.Region(2, 7))
        #   >>>         self.assertSelection(sublime.Region(2, 7))
        #   >>>         self.assertSelection([(2, 7)])
        #   >>>         self.assertSelection([self.Region(2, 7)])
        #   >>>         self.assertSelection([sublime.Region(2, 7)])
        #   >>>         self.assertEqual([sublime.Region(2, 7)], list(self.view.sel()))

        if isinstance(expected, int):
            self.assertEqual([Region(expected)], list(self.view.sel()))
        elif isinstance(expected, tuple):
            self.assertEqual([Region(expected[0], expected[1])], list(self.view.sel()))
        elif isinstance(expected, Region):
            self.assertEqual([expected], list(self.view.sel()))
        else:  # Defaults to expect a list of Regions.
            # TODO loop through expected and convert points and tuples to regions
            self.assertEqual(expected, list(self.view.sel()))

    def assertSelectionCount(self, expected):
        # Test that view selection count and *expected* are equal.
        #
        # Args:
        #   expected (int): Expected number of selections in view.

        self.assertEqual(expected, len(self.view.sel()))

    # DEPRECATED
    @property
    def state(self):
        return State(self.view)

    # DEPRECATED Use newer API methods self.select(), self.Region()
    def _R(self, a, b=None):
        return _make_region(self.view, a, b)

    # DEPRECATED Favour newer API methods like, e.g. assertRegion(), assertSelection(), and assertContent()
    def _assertRegionsEqual(self, expected_region, actual_region, msg=None):
        """Test that regions covers the exact same region. Does not take region orientation into account."""
        if (expected_region.size() == 1) and (actual_region.size() == 1):
            expected_region = _make_region(self.view, expected_region.begin(), expected_region.end())
            actual_region = _make_region(self.view, actual_region.begin(), actual_region.end())
        self.assertEqual(expected_region, actual_region, msg)
