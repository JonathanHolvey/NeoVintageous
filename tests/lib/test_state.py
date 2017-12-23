import os
import unittest

from NeoVintageous.tests.utils import ViewTestCase

from NeoVintageous.lib.state import State
from NeoVintageous.lib.vi import cmd_defs


class TestState(ViewTestCase):

    def test_is_in_any_visual_mode(self):
        self.assertEqual(self.state.in_any_visual_mode(), False)

        self.state.mode = self.NORMAL_MODE
        self.assertEqual(self.state.in_any_visual_mode(), False)
        self.state.mode = self.VISUAL_MODE
        self.assertEqual(self.state.in_any_visual_mode(), True)
        self.state.mode = self.VISUAL_LINE_MODE
        self.assertEqual(self.state.in_any_visual_mode(), True)
        self.state.mode = self.VISUAL_BLOCK_MODE
        self.assertEqual(self.state.in_any_visual_mode(), True)

    # XXX Investigate what it is that causes these tests to fail on CI servers only. They only fail sometimes.
    @unittest.skipIf(os.environ.get('TRAVIS_OS_NAME', False) == 'osx', 'fails in Travis CI OSX server only')
    @unittest.skipIf(os.environ.get('APPVEYOR', False), 'fails in CI server only')
    def test_can_initialize(self):
        s = State(self.view)
        # Make sure the actual usage of NeoVintageous doesn't change the pristine
        # state. This isn't great, though.
        self.view.window().settings().erase('_vintageous_last_char_search_command')
        self.view.window().settings().erase('_vintageous_last_character_search')
        self.view.window().settings().erase('_vintageous_last_buffer_search')

        self.assertEqual(s.sequence, '')
        self.assertEqual(s.partial_sequence, '')
        # TODO(guillermooo): This one fails in AppVeyor, but not locally.
        self.assertEqual(s.mode, self.NORMAL_MODE)
        self.assertEqual(s.action, None)
        self.assertEqual(s.motion, None)
        self.assertEqual(s.action_count, '')
        self.assertEqual(s.glue_until_normal_mode, False)
        self.assertEqual(s.processing_notation, False)
        self.assertEqual(s.last_character_search, '')
        self.assertEqual(s.last_char_search_command, 'vi_f')
        self.assertEqual(s.non_interactive, False)
        self.assertEqual(s.must_capture_register_name, False)
        self.assertEqual(s.last_buffer_search, '')
        self.assertEqual(s.reset_during_init, True)

    def test_must_scroll_into_view(self):
        self.assertFalse(self.state.must_scroll_into_view())

        motion = cmd_defs.ViGotoSymbolInFile()
        self.state.motion = motion
        self.assertTrue(self.state.must_scroll_into_view())


class TestStateModeSwitching(ViewTestCase):

    # XXX Investigate what it is that causes these tests to fail on CI servers only. They only fail sometimes.
    @unittest.skipIf(os.environ.get('TRAVIS_OS_NAME', False) == 'osx', 'fails in Travis CI OSX server only')
    @unittest.skipIf(os.environ.get('APPVEYOR', False), 'fails in CI server only')
    def test_enter_normal_mode(self):
        self.assertEqual(self.state.mode, self.NORMAL_MODE)
        self.state.mode = self.UNKNOWN_MODE
        self.assertNotEqual(self.state.mode, self.NORMAL_MODE)
        self.state.enter_normal_mode()
        self.assertEqual(self.state.mode, self.NORMAL_MODE)

    # XXX Investigate what it is that causes these tests to fail on CI servers only. They only fail sometimes.
    @unittest.skipIf(os.environ.get('TRAVIS_OS_NAME', False) == 'osx', 'fails in Travis CI OSX server only')
    @unittest.skipIf(os.environ.get('APPVEYOR', False), 'fails in CI server only')
    def test_enter_visual_mode(self):
        self.assertEqual(self.state.mode, self.NORMAL_MODE)
        self.state.enter_visual_mode()
        self.assertEqual(self.state.mode, self.VISUAL_MODE)

    # XXX Investigate what it is that causes these tests to fail on CI servers only. They only fail sometimes.
    @unittest.skipIf(os.environ.get('TRAVIS_OS_NAME', False) == 'osx', 'fails in Travis CI OSX server only')
    @unittest.skipIf(os.environ.get('APPVEYOR', False), 'fails in CI server only')
    def test_enter_insert_mode(self):
        self.assertEqual(self.state.mode, self.NORMAL_MODE)
        self.state.enter_insert_mode()
        self.assertEqual(self.state.mode, self.INSERT_MODE)


class TestStateResettingState(ViewTestCase):

    def test_reset_sequence(self):
        self.state.sequence = 'x'
        self.state.reset_sequence()
        self.assertEqual(self.state.sequence, '')

    def test_reset_partial_sequence(self):
        self.state.partial_sequence = 'x'
        self.state.reset_partial_sequence()
        self.assertEqual(self.state.partial_sequence, '')

    def test_reset_command_data(self):
        self.state.sequence = 'abc'
        self.state.partial_sequence = 'x'
        self.state.user_input = 'f'
        self.state.action = cmd_defs.ViReplaceCharacters()
        self.state.motion = cmd_defs.ViGotoSymbolInFile()
        self.state.action_count = '10'
        self.state.motion_count = '100'
        self.state.register = 'a'
        self.state.must_capture_register_name = True

        self.state.reset_command_data()

        self.assertEqual(self.state.action, None)
        self.assertEqual(self.state.motion, None)
        self.assertEqual(self.state.action_count, '')
        self.assertEqual(self.state.motion_count, '')

        self.assertEqual(self.state.sequence, '')
        self.assertEqual(self.state.partial_sequence, '')
        self.assertEqual(self.state.register, '"')
        self.assertEqual(self.state.must_capture_register_name, False)


class TestStateResettingVolatileData(ViewTestCase):

    def test_reset_volatile_data(self):
        self.state.glue_until_normal_mode = True
        self.state.processing_notation = True
        self.state.non_interactive = True
        self.state.reset_during_init = False

        self.state.reset_volatile_data()

        self.assertFalse(self.state.glue_until_normal_mode)
        self.assertFalse(self.state.processing_notation)
        self.assertFalse(self.state.non_interactive)
        self.assertTrue(self.state.reset_during_init)


class TestStateCounts(ViewTestCase):

    def test_can_retrieve_good_action_count(self):
        self.state.action_count = '10'
        self.assertEqual(self.state.count, 10)

    def test_fails_if_bad_action_count(self):
        def set_count():
            self.state.action_count = 'x'
        self.assertRaises(AssertionError, set_count)

    def test_fails_if_bad_motion_count(self):
        def set_count():
            self.state.motion_count = 'x'
        self.assertRaises(AssertionError, set_count)

    def test_count_is_never_less_than1(self):
        self.state.motion_count = '0'
        self.assertEqual(self.state.count, 1)

        def set_count():
            self.state.motion_count = '-1'

        self.assertRaises(AssertionError, set_count)

    def test_can_retrieve_good_motion_count(self):
        self.state.motion_count = '10'
        self.assertEqual(self.state.count, 10)

    def test_can_retrieve_good_combined_count(self):
        self.state.motion_count = '10'
        self.state.action_count = '10'
        self.assertEqual(self.state.count, 100)


class TestStateModeNames(ViewTestCase):

    def test_mode_name(self):
        self.assertEqual(self.COMMAND_LINE_MODE, 'mode_command_line')
        self.assertEqual(self.INSERT_MODE, 'mode_insert')
        self.assertEqual(self.INTERNAL_NORMAL_MODE, 'mode_internal_normal')
        self.assertEqual(self.NORMAL_MODE, 'mode_normal')
        self.assertEqual(self.OPERATOR_PENDING_MODE, 'mode_operator_pending')
        self.assertEqual(self.VISUAL_MODE, 'mode_visual')
        self.assertEqual(self.VISUAL_BLOCK_MODE, 'mode_visual_block')
        self.assertEqual(self.VISUAL_LINE_MODE, 'mode_visual_line')


class TestStateRunnability(ViewTestCase):

    def test_can_run_action(self):
        self.assertEqual(self.state.can_run_action(), None)

        self.state.mode = self.VISUAL_MODE
        self.assertEqual(self.state.can_run_action(), None)

        self.state.action = cmd_defs.ViDeleteByChars()
        self.state.mode = self.VISUAL_MODE
        self.assertEqual(self.state.can_run_action(), True)

        self.state.action = cmd_defs.ViDeleteLine()
        self.state.mode = self.VISUAL_MODE
        self.assertEqual(self.state.can_run_action(), True)

        self.state.mode = self.NORMAL_MODE
        self.state.action = cmd_defs.ViDeleteByChars()
        self.assertEqual(self.state.can_run_action(), None)

        self.state.mode = self.NORMAL_MODE
        self.state.action = cmd_defs.ViDeleteLine()
        self.assertEqual(self.state.can_run_action(), True)

    def test_runnable_if_action_and_motion_available(self):
        self.state.mode = self.NORMAL_MODE
        self.state.action = cmd_defs.ViDeleteLine()
        self.state.motion = cmd_defs.ViMoveRightByChars()
        self.assertEqual(self.state.runnable(), True)

        self.state.mode = 'junk'
        self.state.action = cmd_defs.ViDeleteByChars()
        self.state.motion = cmd_defs.ViMoveRightByChars()
        self.assertRaises(ValueError, self.state.runnable)

    def test_runnable_if_motion_available(self):
        self.state.mode = self.NORMAL_MODE
        self.state.motion = cmd_defs.ViMoveRightByChars()
        self.assertEqual(self.state.runnable(), True)

        self.state.mode = self.OPERATOR_PENDING_MODE
        self.state.motion = cmd_defs.ViMoveRightByChars()
        self.assertRaises(ValueError, self.state.runnable)

    def test_runnable_if_action_available(self):
        self.state.mode = self.NORMAL_MODE
        self.state.action = cmd_defs.ViDeleteLine()
        self.assertEqual(self.state.runnable(), True)

        self.state.action = cmd_defs.ViDeleteByChars()
        self.assertEqual(self.state.runnable(), False)

        self.state.mode = self.OPERATOR_PENDING_MODE
        # ensure we can run the action
        self.state.action = cmd_defs.ViDeleteLine()
        self.assertRaises(ValueError, self.state.runnable)


class TestStateSetCommand(ViewTestCase):

    def test_raise_error_if_unknown_command_type(self):
        fake_command = {'type': 'foo'}
        self.assertRaises(AssertionError, self.state.set_command, fake_command)

    def test_raises_error_if_too_many_motions(self):
        self.state.motion = cmd_defs.ViMoveRightByChars()

        self.assertRaises(ValueError, self.state.set_command, cmd_defs.ViMoveRightByChars())

    def test_changes_mode_for_lone_motion(self):
        self.state.mode = self.OPERATOR_PENDING_MODE

        motion = cmd_defs.ViMoveRightByChars()
        self.state.set_command(motion)

        self.assertEqual(self.state.mode, self.NORMAL_MODE)

    def test_raises_error_if_too_many_actions(self):
        self.state.motion = cmd_defs.ViDeleteLine()

        self.assertRaises(ValueError, self.state.set_command, cmd_defs.ViDeleteLine())

    def test_changes_mode_for_lone_action(self):
        operator = cmd_defs.ViDeleteByChars()

        self.state.set_command(operator)

        self.assertEqual(self.state.mode, self.OPERATOR_PENDING_MODE)
