# Copyright (C) 2018 The NeoVintageous Team (NeoVintageous).
#
# This file is part of NeoVintageous.
#
# NeoVintageous is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# NeoVintageous is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NeoVintageous.  If not, see <https://www.gnu.org/licenses/>.

import os
import tempfile

from NeoVintageous.tests import unittest


def mock_async_save():
    """Mock saving view via ex command.

    Async saving makes testing flaky.
    """
    def wrapper(f):
        @unittest.mock.patch('NeoVintageous.nv.ex_cmds.save')
        def wrapped(self, *args, **kwargs):
            save = args[-1]
            save.side_effect = lambda obj: obj.run_command('save', {'async': False})

            return f(self, *args[:-1], **kwargs)
        return wrapped
    return wrapper


class Test_ex_write(unittest.FunctionalTestCase):

    @unittest.mock_status_message()
    def test_no_file_name(self):
        self.normal('1\n|buzz\nfizz\n4\n')
        self.feed(':write')
        self.assertStatusMessage('E32: No file name')

    @unittest.mock_hide_panel()
    @unittest.mock_status_message()
    @mock_async_save()
    def test_write(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            file_name = os.path.join(tmpdirname, 'new.txt')
            file_name_alt = os.path.join(tmpdirname, 'new_alt.txt')
            file_name_noop = os.path.join(tmpdirname, 'new_noop.txt')

            # Test a new file can be saved.
            self.normal('fizz\n')
            self.feed(':write ' + file_name)
            self.assertEqual(file_name, self.view.file_name())
            with open(file_name, 'r') as f:
                self.assertEqual('fizz\n', f.read())

            # Test an existing file can be saved.
            self.write('buzz\n')
            self.feed(':write')
            self.assertEqual(file_name, self.view.file_name())
            with open(file_name, 'r') as f:
                self.assertEqual('buzz\n', f.read())

            # Test can append to current file.
            self.feed(':write >>')
            self.assertEqual(file_name, self.view.file_name())
            with open(file_name, 'r') as f:
                self.assertEqual('buzz\nbuzz\n', f.read())

            # Test can write to another file.
            self.feed(':write ' + file_name_alt)
            self.assertEqual(file_name_alt, self.view.file_name())
            with open(file_name_alt, 'r') as f:
                self.assertEqual('buzz\nbuzz\n', f.read())

            self.assertNoStatusMessage()

            # Test can append to file.
            self.feed(':write >> ' + file_name)
            self.assertStatusMessage('Appended to %s' % file_name)
            self.assertEqual(file_name_alt, self.view.file_name())
            with open(file_name_alt, 'r') as f:
                self.assertEqual('buzz\nbuzz\n', f.read())
            with open(file_name, 'r') as f:
                self.assertEqual('buzz\nbuzz\nbuzz\nbuzz\n', f.read())

            # Test trying to append to non-existing file.
            self.feed(':write >> ' + file_name_noop)
            self.assertStatusMessage('E212: Can\'t open file for writing: %s' % file_name_noop)

            # Test force append to non-existing file.
            self.feed(':write! >> ' + file_name_noop)
            self.assertStatusMessage('Appended to %s' % file_name_noop)

            # Test appending from a line range.
            self.assertEqual(file_name_alt, self.view.file_name())
            self.normal('1\n2\n3\n4\n5\n6\n7\n8\n9\n0\n')
            self.feed(':write')
            self.feed(':3,6write >> ' + file_name_alt)
            self.assertStatusMessage('Appended to %s' % file_name_alt)
            with open(file_name_alt, 'r') as f:
                self.assertEqual('1\n2\n3\n4\n5\n6\n7\n8\n9\n0\n3\n4\n5\n6\n', f.read())

            # Test readonly emits status message
            self.view.run_command('insert', {'characters': 'x'})
            self.view.set_read_only(True)
            self.feed(':write')
            self.assertStatusMessage("E45: 'readonly' option is set (add ! to override)")
            self.view.set_read_only(False)
