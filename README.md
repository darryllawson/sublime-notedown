# Notedown for Sublime Text

Notedown lets you use [Sublime Text](http://sublimetext.com/) to manage a collection of notes stored as [Markdown](https://en.wikipedia.org/wiki/Markdown) files.

Out of the box, Sublime Text with its built-in Markdown support is already fairly effective for managing notes. However, it lacks one key feature: **linking between notes**.

Notedown fills this gap. It allows you to link to another note with this syntax:

```text
[[Note title]]
```

Follow a link with **Ctrl + Alt + Left Mouse Button** or **Ctrl + Alt + O** (the *Notedown: Open Link* command).

## Feature

- **Link to other notes** with this syntax: `[[Note title]]`.
- **Note title auto-completion.** Type `[[` and you will be shown a list of notes you can link to.
- **Note renaming.** Change the Markdown Heading on the first line of the note and the note file will automatically be renamed to match.
- **Open a URL** with the same shortcuts you use for opening a note.
- **Note creation.** Click on a link to a note that does not exist and you'll be prompted to create it.
- **Note link validation.** When you save a note, you'll be shown a list of broken note links.

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

Notedown defines two commands:

- **notedown_open_link**: Opens the note link or URL under the cursor or mouse selection.

    - Default mouse map: **Ctrl + Alt + Left Mouse Button**
    - Default keyboard map: **Ctrl + Alt + O**

- **notedown_lint**: Lints the current file. This is run automatically when a Markdown file is saved.

## User Settings

Notedown looks for user settings in `Notedown.sublime-settings`.

Notedown supports a single user setting:

- **markdown_extension**: Defines the file extension to use when creating new notes. Do not include a leading period (`.`). If not defined, `md` is used.
