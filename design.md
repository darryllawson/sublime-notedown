# Design of Notedown

## Design philosophy

- Minimalism, simplicity, and speed.
- Do nothing that conflicts with the design philosophy of Sublime Text.
- Orthogonal to Markdown and HTML.

## How to debug

Enable debug output from the Sublime Text console with:

    >>> import Notedown
    >>> Notedown.notedown.debug()

## Design decisions

Why Markdown? It's popular, provides a "good enough" structure and syntax for notes, provides syntax highlighting for improved readability, and it provides heading navigation (with ⌘R).

Why the [[Note name]] syntax? Avoids conflict with Markdown or HTML syntax, distinguishable from normal prose, easy to read, and efficient to parse. Additionally, this syntax is used in other popular note-taking apps such as Bear (which uses Markdown too) and Notational Velocity.

Why not WikiWord links? Because you can get false matches with names from code and ordinary prose, parsing is less efficient, and auto-completion is less useful.

Why not use Sublime Text's built-in auto-completion for completing note names? I did originally, but it had some major limitations: didn't work for note titles containing punctuation (e.g. "C++") and it behaved unexpectedly for spaces - hitting space is treated as finalizing the completion, but note titles may contain spaces.

Why tilde to separate note titles? Need a character that does not clash with typical note titles (rules out - , .) and can be used on all operating systems (rules out |).

Only support a single flat directory of notes because this is simple, fast, and requires no configuration. I believe notes should be a flat concept anyway. Perhaps tags can be supported one day.
