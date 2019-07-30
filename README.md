# Notedown for Sublime Text

Notedown lets you use [Sublime Text](http://sublimetext.com/) to manage notes stored as [Markdown](https://en.wikipedia.org/wiki/Markdown) files.

Out of the box, Sublime Text with its built-in Markdown support, is already pretty good for managing notes. However, it lacks one key feature: **linking between notes**.

Notedown fills this gap. It lets you to link to another note with

```text
[[Note title]]
```

Follow a link with **Ctrl + Alt + Left Mouse Button** or by positioning the cursor and pressing **Ctrl + Alt + O** or selecting **Notedown: Open Link** in the command palette.

## Features

Features provided by Notedown:

- **Link to another note** with `[[Note title]]`.
- **Note title auto-completion.** Type `[[` and you're shown a list of notes you can link to.
- **Note renaming.** Change the Markdown heading and the note file is automatically renamed to match.
- **Open a URL** conforming to the Markdown syntax with the same shortcuts you use for opening a note.
- **Create a new note** by attempting to open a link to a note that does not exist.
- **Note link validation.** On save, you'll be shown a list of broken note links.

Note keeping features built into Sublime Text:

* **Search for a note** with *Goto Anything* (**Command + P** or **Ctrl + P**).
* **Goto a heading within a note** with *Goto Symbol* (**Command + R** or **Ctrl + R**).

## Note links

Note link syntax:

```text
[[<text>]]
```

`<text>` can be a note title, an *alternative* note title, or a filename with the Markdown extension omitted.

For example, all of these links,

```text
[[Foo]]
[[Bar]]
[[Goo]]
[[Foo (Bar, Goo)]]
```

link to the file,

```text
Foo (Bar, Goo).md
```

## Note titles and file names

Each note has one title and any number of *alternative* titles defined by the note's file name:

```text
<title>.md
<title> (<alternative title>).md
<title> (<alternative title>, <alternative title>, ...).md
```

Any common Markdown file extension -- `.md`, `.mdown`, `.markdown`, or `.markdn` -- can be used.

`<title>` and `<alternative title>` must not include any of these characters:

```text
( ) ,
```

## Commands

Notedown provides these Sublime Text commands:

- **notedown_open_link**: Opens the note link or URL under the cursor or mouse selection.

    - Default mouse map: **Ctrl + Alt + Left Mouse Button**
    - Default keyboard map: **Ctrl + Alt + O**

- **notedown_lint**: Lints the current note. This is run automatically when a note is saved.

## Settings

Notedown looks for settings in `Notedown.sublime-settings`.

Notedown supports these settings:

- **markdown_extension**: The file extension used when creating new notes. This should not include a leading period (`.`). If not defined, `md` is used. Example: `"markdown_extension": "markdown"`.

- **note_folder_patterns**: Defines which folders contain *notes* compatible with Notedown. The folder patterns (which may use wildcards compatible with [fnmatch](https://docs.python.org/3/library/fnmatch.html#fnmatch.fnmatch)) are matched against the name of a Markdown file's containing folder to determine if the file should be considered a note. If not defined or an empty list, then all Markdown files are considered to be notes. Example: `"note_folder_patterns": ["Notes"]`.

