"""Sublime Text Notedown plugins

Design philosophy
-----------------

- Minimalism, simplicity, and speed.
- Do nothing that conflicts with the design philosophy of Sublime Text.
- Orthogonal to Markdown and HTML.

Debugging
---------

Enable debug output from the Sublime Text console with:

    >>> import Notedown
    >>> Notedown.notedown.debug()

Design decisions
----------------

Why Markdown? It is popular, provides a "good enough" structure and
syntax for notes, provides syntax highlighting for improved readability, and
it provides heading navigation.

Why [[Note name]] syntax? 1) avoids conflict with Markdown or HTML syntax,
2) distinguishable from normal prose, 3) easy to read, 4) efficient to
parse, and 5) can enable for advanced features. Additionally, this syntax is
used in popular note-taking apps such as Notational Velocity and Bear notes.

Why not WikiWord links? 1) You can get false matches with names from code
and ordinary prose, 2) parsing is less efficient, 3) auto-completion is less
useful, and 4) no scope for more advanced features.

Only support a single flat directory of notes, because this is simple, fast,
and requires no configuration. I believe notes should be a flat concept
anyway. Perhaps tags can be supported one day.
"""

import fnmatch
import functools
import os
import re
import sys
import timeit
import webbrowser

import sublime
import sublime_plugin

_FILENAME_REGEX = re.compile(
    r'^('
    r'(.*?)'                             # Title
    r'(?:\s*\((.*)\))?'                  # Alternative titles
    r')'
    r'\.(?:md|mdown|markdown|markdn)$',  # Extension
    flags=re.I)

_DEFAULT_EXTENSION = 'md'

_NOTE_TEMPLATE = """\
# {}

See also:

- [[{}]]
"""


def _log_duration(f):
    def wrapper(*args, **kwargs):
        started = timeit.default_timer()
        value = f(*args, **kwargs)
        _debug_log('{:.3f}s to {}'.format(
            timeit.default_timer() - started,
            f.__name__.strip('_').replace('_', ' ')))
        return value
    return wrapper


class _NotedownTextCommand(sublime_plugin.TextCommand):

    def is_enabled(self):
        return _viewing_a_note(self.view)

    def is_visible(self):
        return _viewing_a_note(self.view)


class NotedownOpenLinkCommand(_NotedownTextCommand):

    def run(self, edit):
        notes = _find_notes(self.view)
        link_regions = _find_link_regions(self.view)
        for selection in self.view.sel():
            self._handle_selection(selection, link_regions, notes)

    def _handle_selection(self, selection, link_regions, notes):
        if selection.empty():
            point = selection.begin()
            if self.view.match_selector(point, 'markup.underline.link'):
                target = self.view.substr(self.view.extract_scope(point))
                webbrowser.open(target)
            else:
                title = self._title_at_point(point, link_regions)
                if title:
                    self._open_note(title, notes)
        else:  # Text is selected
            self._open_note(self.view.substr(selection), notes)

    def _title_at_point(self, point, link_regions):
        for region in link_regions:
            if region.contains(point):
                return self.view.substr(region)[2:-2]
        return self.view.substr(self.view.word(point))

    def _open_note(self, title, notes):
        try:
            filenames = [x for _, x in notes[title.lower()]]
        except KeyError:
            filename = _create_note(title, self.view)
            if not filename:
                return
            filenames = [filename]

        def on_done(index):
            if index != -1:  # Not canceled
                self.view.window().open_file(filenames[index])

        if len(filenames) > 1:
            self.view.window().show_quick_panel(filenames, on_done)
        else:
            self.view.window().open_file(filenames.pop())


class NotedownLintCommand(_NotedownTextCommand):

    def run(self, edit):
        notes = _find_notes(self.view)

        # TODO: check for a valid note title
        _note_title(self.view)

        self._validate_links(notes)

    def _validate_links(self, notes):
        link_regions = _find_link_regions(self.view)
        broken = []
        for region in link_regions:
            title = self.view.substr(region)[2:-2]
            if title.lower() not in notes:
                broken.append((region, title))
        self._highlight(broken)
        self._show_list(broken)

    def _highlight(self, broken):
        self.view.add_regions('notedown', [x for x, y in broken],
                              'invalid.illegal', '', sublime.DRAW_NO_FILL)

    def _show_list(self, broken):
        self.view.window().show_quick_panel(
            [self._format_item(x, y) for x, y in broken],
            lambda x: self._on_item_selected(x, broken))

    def _format_item(self, region, text):
        row, _ = self.view.rowcol(region.begin())
        return ['Note file not found',
                'Line {}: [[{}]]'.format(row + 1, text)]

    def _on_item_selected(self, index, broken):
        if index == -1:  # Canceled by user
            return
        region, _ = broken[index]
        self.view.sel().clear()
        self.view.sel().add(sublime.Region(region.begin() + len('[['),
                                           region.end() - len(']]')))
        self.view.show(self.view.sel())


class NotedownEventListener(sublime_plugin.EventListener):

    def on_pre_close(self, view):
        if view.is_primary():  # Only one view on buffer
            try:
                del _link_regions_cache[view.buffer_id()]
            except KeyError:
                pass

    def on_post_save_async(self, view):
        if not _viewing_a_note(view):
            return

        renamed = self._reflect_title_in_filename(view)
        if not renamed:
            view.run_command('notedown_lint')

    def on_query_completions(self, view, prefix, locations):
        if not _viewing_a_note(view):
            return False

        if not self._can_show_completions(view, locations):
            return

        file_name = view.file_name()
        titles = {y for x in _find_notes(view).values() for y, z in x
                  if not os.path.samefile(z, file_name)}
        return [[x + '\tNote', x + ']]'] for x in sorted(titles)]

    def _can_show_completions(self, view, locations):
        # Show completions if not in raw scope and [[ has been typed.
        point = locations[0]
        if view.match_selector(point, 'markup.raw'):
            return False
        pre_text = view.substr(sublime.Region(view.line(point).begin(),
                                              point))
        if not re.match(r'.*\[\[(.*?)(?!\]\])', pre_text):
            return False
        return True

    def _reflect_title_in_filename(self, view):
        """Returns True if the file was renamed."""
        try:
            title = _note_title(view)
        except _NoTitleError:
            return False  # Lint will show this error

        old_title, ext = os.path.splitext(os.path.basename(view.file_name()))
        if title == old_title:
            return False  # Nothing to do

        new_filename = title + ext
        text = 'Rename this file to {}?'.format(new_filename)
        if not sublime.ok_cancel_dialog(text, 'Rename File'):
            return False

        old_filename = view.file_name()
        new_filename = os.path.join(os.path.dirname(old_filename),
                                    new_filename)

        window = view.window()
        try:
            os.rename(old_filename, new_filename)
        except OSError as exp:  # noqa
            sublime.error_message('Could not rename {}:\n\n{}'
                                  .format(old_filename, exp))
            return False
        view.close()
        window.open_file(new_filename)

        return True


def debug(enable=True):
    global _debug_enabled
    _debug_enabled = enable


def _note_title(view):
    """Extracts a note's title from the first line of the view text.

    Raises _NoTitleError if the note does not have a valid title.
    """
    first_line = view.substr(view.line(0))
    if not view.match_selector(0, 'markup.heading.1.markdown'):
        raise _NoTitleError(first_line)
    return first_line[2:].strip()


class _NoTitleError(Exception):

    def __init__(self, first_line):
        self.first_line = first_line


@_log_duration
def _find_notes(view):
    """Returns a {<lowercase title>: [(<title>, <filename>)]} dictionary
    representing the notes in the directory containing the file shown in view.

    Results are cached in _notes_cache.
    """
    path = os.path.dirname(view.file_name())

    mtime, notes = _notes_cache.get(path, (None, None))
    if mtime == os.stat(path).st_mtime:
        return notes

    notes = {}
    for name in os.listdir(path):
        titles = _parse_filename(name)
        if titles:
            filename = os.path.join(path, name)
            for lower_title, title in titles:
                if lower_title in notes:
                    notes[lower_title].append((title, filename))
                else:
                    notes[lower_title] = [(title, filename)]
    _notes_cache[path] = os.stat(path).st_mtime, notes
    return notes


@functools.lru_cache(maxsize=2 ** 16)
def _parse_filename(filename):
    """Returns a list of (<lower case title>, <title>) 2-tuples describing
    all the valid titles for the note in filename. The first element is
    the "primary" name.
    """
    match = _FILENAME_REGEX.match(filename)
    if not match:
        return []
    full, primary, alt = match.groups()
    names = [primary]
    if alt:
        names.append(full)
        names.extend(x.strip() for x in alt.split(','))
    return [(x.lower(), x) for x in names]


def _create_note(title, view):
    """Creates a new note.

    Returns the filename of the new note or None if the user canceled or
    there was an error.
    """
    basename = '{}.{}'.format(title, _setting('markdown_extension', str,
                                              _DEFAULT_EXTENSION))
    text = 'Do you want to create {}?'.format(basename)
    if not sublime.ok_cancel_dialog(text, 'Create File'):
        return
    filename = os.path.join(os.path.dirname(view.file_name()), basename)

    back_titles = _parse_filename(os.path.basename(view.file_name()))
    primary_back_title = back_titles[0][1]
    try:
        with open(filename, 'w') as fileobj:
            fileobj.write(_NOTE_TEMPLATE.format(title, primary_back_title))
    except IOError as exp:
        sublime.error_message('Could not create {}:\n\n{}'
                              .format(filename, exp))
        return

    return filename


@_log_duration
def _find_link_regions(view):
    """Returns a list of sublime.Region objects describing link locations
    within a Markdown file.

    Results are cached in _link_regions_cache.
    """
    last_change_count, regions = _link_regions_cache.get(view.buffer_id(),
                                                         (None, None))
    if view.change_count() == last_change_count:
        return regions

    regions = [x for x in view.find_all(r'\[\[.+?\]\]')
               if not view.match_selector(x.begin(), 'markup.raw')]
    _link_regions_cache[view.buffer_id()] = view.change_count(), regions
    return regions


def _viewing_a_note(view):
    if not view.match_selector(0, 'text.html.markdown'):
        return False

    note_folder_patterns = _setting('note_folder_patterns', list)
    if not note_folder_patterns:
        return True
    if any(not isinstance(x, str) for x in note_folder_patterns):
        _invalid_setting('note_folder_patterns', note_folder_patterns,
                         '[str, ...]')
        return False

    note_folder = os.path.basename(os.path.dirname(view.file_name()))
    return any(fnmatch.fnmatch(note_folder, x) for x in note_folder_patterns)


def _setting(name, type_, default=None):
    value = sublime.load_settings('Notedown.sublime-settings').get(name,
                                                                   default)
    if value is not default and not isinstance(value, type_):
        _invalid_setting(name, value, type_)
        return default
    else:
        return value


def _invalid_setting(name, value, type_):
    sublime.error_message('Invalid Notedown setting "{}":\n\n{!r}\n\n'
                          'Must be of type {}.'.format(name, value, type_))


def _debug_log(message):
    if _debug_enabled:
        _log(message)


def _log(message):
    sys.stdout.write('Notedown: {}\n'.format(message))
    sys.stdout.flush()


_debug_enabled = False
_notes_cache = {}             # {path: (mtime, notes dict)}
_link_regions_cache = {}      # {buffer id: (change count, regions)}
