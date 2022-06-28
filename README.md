# Notedown for Sublime Text

The *Notedown* package helps you use [Sublime Text](http://sublimetext.com/) for keeping notes stored as [Markdown](https://en.wikipedia.org/wiki/Markdown) files.

Sublime Text, with its built-in Markdown support, is pretty good at managing notes. But it lacks one key feature: **linking between notes**.

Notedown fills this gap. It lets you to link to another note with

```text
[[Note title]]
```

Follow a link with **Ctrl + Alt + Left Mouse Button** or by positioning the cursor then pressing **Ctrl + Alt + O** or selecting **Notedown: Open** from the command palette.

## Features

Features provided by Notedown:

- **Link to another note** with `[[Note title]]`.
- **Note title auto-completion.** Type `[[` and you're shown a list of notes you can link to.
- **Note renaming.** Change the Markdown heading and the note file is automatically renamed to match and all backlinks are updated.
- **Open a URL** conforming to the Markdown syntax with the same shortcuts you use for opening a note.
- **Create a new note** by attempting to open a link to a note that does not exist.
- **Note link validation.** On save, you'll be shown a list of broken note links.

Note keeping features built into Sublime Text:

* **Search for a note** with *Goto Anything* (**Command + P** or **Ctrl + P**).
* **Goto a heading within a note** with *Goto Symbol* (**Command + R** or **Ctrl + R**).

## Note filenames and titles

A note has one or more titles defined by its file name:

```text
<title>.md
<title> ~ <title>.md
```

The tilde character (`~`) is used to separate multiple note titles. `<title>` must not contain tilde characters.

Any Markdown file extension (`.md`, `.mdown`, `.markdown`, or `.markdn`) can be used.

## Note links

Note link syntax:

```text
[[<title>]]
```

For example, all of the following links,

```text
[[Foo]]
[[Bar]]
[[Goo]]
```

link to the same file:

```text
Foo ~ Bar ~ Goo.md
```

Links within *raw* markup are ignored. For example:

```text
`[[This]] is a not link.`
```

## Commands

Notedown provides these Sublime Text commands:

- **notedown_open**: Open the link under the cursor or mouse selection.

    - Default mouse map: **Ctrl + Alt + Left Mouse Button**
    - Default keyboard map: **Ctrl + Alt + O**

- **notedown_lint**: Lints the current note. Runs automatically when a note is saved.

## Settings

Notedown looks for settings in `Notedown.sublime-settings`.

Notedown supports these settings:

- **markdown_extension**: The file extension used when creating new notes. This should not include a leading period (`.`). If not defined, `md` is used. Example: `"markdown_extension": "markdown"`.

- **note_folder_patterns**: Defines which folders contain *notes* compatible with Notedown. The folder patterns (which may use wildcards compatible with [fnmatch](https://docs.python.org/3/library/fnmatch.html#fnmatch.fnmatch)) are matched against the name of a Markdown file's containing folder to determine if the file should be considered a note. If not defined or an empty list, then all Markdown files are considered to be notes. Example: `"note_folder_patterns": ["Notes"]`.

- **reflect_title_in_filename**: Whether to propose a new file name that will reflect title found in the note text. If not defined or `true` then synchronization of filename to title is enabled. Example: `"reflect_title_in_filename": false`.
