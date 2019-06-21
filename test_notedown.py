import os
import shutil
import sys
import tempfile
import unittest
import unittest.mock as mock


def setUpModule():
    global notedown, sublime, sublime_plugin
    sys.modules['sublime'] = sublime = mock.Mock()
    sys.modules['sublime_plugin'] = sublime_plugin = mock.Mock()
    sublime_plugin.TextCommand = MockTextCommand
    sublime_plugin.EventListener = MockEventListener
    import notedown


def tearDownModule():
    del sys.modules['sublime']
    del sys.modules['sublime_plugin']
    notedown._parse_filename.cache_clear()
    notedown._debug_enabled = False
    notedown._notes_cache = {}
    notedown._link_regions_cache = {}


class NotedownTestCase(unittest.TestCase):

    def setUp(self):
        self.notes_dir = tempfile.mkdtemp()
        self.note_1 = self.create_file('Note one')
        self.note_2 = self.create_file('Note two (Alt one)')
        self.note_3 = self.create_file('Note three (Alt two, ALT one)')
        self.not_md = self.create_file('not_md', ext='.txt')
        self.view_1 = self.mock_view(self.note_1)

    # TODO: these mock methods should be functions?
    def mock_view(self, file_name, ident=1):
        view = mock.Mock()
        view.file_name = mock.Mock(return_value=file_name)
        view.buffer_id = mock.Mock(return_value=1)
        view.change_count = mock.Mock(return_value=100)
        view.find_all = mock.Mock(return_value=[self.mock_region(),
                                                self.mock_region()])
        view.match_selector = mock.Mock(return_value=False)
        view.is_primary = mock.Mock(return_value=False)
        return view

    def mock_region(self, begin=100):
        region = mock.Mock()
        region.begin = mock.Mock(return_value=begin)
        return region

    def tearDown(self):
        shutil.rmtree(self.notes_dir)

    def create_file(self, title, text='', ext='.md'):
        filename = os.path.join(self.notes_dir, title + ext)
        with open(filename, 'w') as fp:
            fp.write(text)
        return filename


class TestNotedownOpenLinkCommand(NotedownTestCase):

    def setUp(self):
        super().setUp()
        self.command = notedown.NotedownOpenLinkCommand(self.view_1)

    def test_enabled_and_visible_when_viewing_markdown(self):
        self.view_1.match_selector.return_value = True
        self.assertTrue(self.command.is_enabled())
        self.assertTrue(self.command.is_visible())

    def test_not_enabled_or_visible_when_not_viewing_markdown(self):
        self.view_1.match_selector.return_value = False
        self.assertFalse(self.command.is_enabled())
        self.assertFalse(self.command.is_visible())


class TestNotedownLintCommand(NotedownTestCase):

    def setUp(self):
        super().setUp()
        self.command = notedown.NotedownLintCommand(self.view_1)

    def test_enabled_and_visible_when_viewing_markdown(self):
        self.view_1.match_selector.return_value = True
        self.assertTrue(self.command.is_enabled())
        self.assertTrue(self.command.is_visible())

    def test_not_enabled_or_visible_when_not_viewing_markdown(self):
        self.view_1.match_selector.return_value = False
        self.assertFalse(self.command.is_enabled())
        self.assertFalse(self.command.is_visible())


class TestNotedownEventListener(NotedownTestCase):

    def setUp(self):
        super().setUp()
        self.listener = notedown.NotedownEventListener()

    @mock.patch('notedown._link_regions_cache', {1: 'X'})
    def test_on_pre_close(self):
        self.view_1.is_primary.return_value = False
        self.listener.on_pre_close(self.view_1)
        self.assertIn(1, notedown._link_regions_cache)  # Still there

        self.view_1.is_primary.return_value = True
        self.listener.on_pre_close(self.view_1)
        self.assertFalse(notedown._link_regions_cache)  # Gone

        # Handle key error
        self.listener.on_pre_close(self.view_1)


class TestFindingNotes(NotedownTestCase):

    def test_notes_dict(self):
        notes = notedown._find_notes(self.view_1)
        self.assertEqual(notes.keys(), {'note one', 'note two', 'note three',
                                        'alt one', 'alt two'})
        self.assertEqual(notes['note one'], [('Note one', self.note_1)])
        self.assertEqual(notes['note two'], [('Note two', self.note_2)])
        self.assertEqual(notes['note three'], [('Note three', self.note_3)])
        self.assertEqual(notes['alt one'], [('Alt one', self.note_2),
                                            ('ALT one', self.note_3)])
        self.assertEqual(notes['alt two'], [('Alt two', self.note_3)])

    def test_cache(self):
        notes = notedown._find_notes(self.view_1)
        self.assertIs(notedown._notes_cache[self.notes_dir][1], notes)

        # No change in notes dir, cache is unchanged
        notedown._find_notes(self.view_1)
        self.assertIs(notedown._notes_cache[self.notes_dir][1], notes)

        # Note added, cache is updated
        self.create_file('Note three')
        notedown._find_notes(self.view_1)
        self.assertIsNot(notedown._notes_cache[self.notes_dir][1], notes)


@mock.patch('sublime.load_settings', return_value={})
@mock.patch('sublime.ok_cancel_dialog', return_value=True)
class TestCreatingNote(NotedownTestCase):

    def note_exists(self, filename):
        return os.path.isfile(os.path.join(self.notes_dir, filename))

    def create_note(self, title):
        notedown._create_note(title, self.view_1)

    def test_default_extension(self, ok_cancel_dialog, load_settings):
        self.create_note('Foo')
        self.assertTrue(self.note_exists('Foo.md'))

    def test_defined_extension(self, ok_cancel_dialog, load_settings):
        load_settings.return_value = {'markdown_extension': 'abc'}
        self.create_note('Foo')
        self.assertTrue(self.note_exists('Foo.abc'))

    def test_user_cancelled(self, ok_cancel_dialog, load_settings):
        ok_cancel_dialog.return_value = False
        self.create_note('Foo')
        self.assertFalse(self.note_exists('Foo.md'))

    def test_dialog_message(self, ok_cancel_dialog, load_settings):
        self.create_note('Foo')
        ok_cancel_dialog.assert_called_once_with(
            'Do you want to create Foo.md?', 'Create File')

    def test_note_contents(self, *mocks):
        self.create_note('Foo')
        with open(os.path.join(self.notes_dir, 'Foo.md'), 'r') as f:
            self.assertEqual(f.read(), '# Foo\n\n'
                                       'See also:\n\n'
                                       '- [[Note one]]\n')

    @mock.patch('sublime.error_message')
    @mock.patch('notedown.open', side_effect=IOError('boom'))
    def test_creation_error(self, open_, error_message, ok_cancel_dialog,
                            load_settings):
        self.create_note('Foo')
        self.assertFalse(self.note_exists('Foo.md'))
        message = 'Could not create {}:\n\nboom'.format(
            os.path.join(self.notes_dir, 'Foo.md'))
        error_message.assert_called_once_with(message)


class TestFindingLinkRegions(NotedownTestCase):

    def test_not_in_cache_and_changed(self):
        regions = notedown._find_link_regions(self.view_1)
        self.assertEqual(len(regions), 2)

    def test_in_cache_and_changed(self):
        regions = notedown._find_link_regions(self.view_1)
        self.view_1.change_count = unittest.mock.Mock(return_value=1001)
        # self.view_1._change_count += 1
        new_regions = notedown._find_link_regions(self.view_1)
        self.assertEqual(len(new_regions), 2)
        self.assertIsNot(new_regions, regions)

    def test_in_cache_and_not_changed(self):
        regions = notedown._find_link_regions(self.view_1)
        new_regions = notedown._find_link_regions(self.view_1)
        self.assertIs(new_regions, regions)


class MockTextCommand():

    def __init__(self, view):
        self.view = view


class MockEventListener():
    pass


if __name__ == '__main__':
    unittest.main()
