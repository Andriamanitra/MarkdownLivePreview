# MarkdownLivePreview

A simple plugin to preview your markdown as you type right in Sublime Text.
No dependencies!

## Differences with upstream

You probably want to use the [upstream version](https://github.com/math2001/MarkdownLivePreview) instead.
My changes include:
* Preview is opened in the same window, on the right hand side, rather than in a new window
* The "show_markdown_preview" command has been replaced by "toggle_markdown_preview"
* Toggling preview is available on plaintext files

These changes come with the following drawbacks:
* Files **MUST** be saved in order to preview
* You can only have one preview at a time
* Enabling preview always changes the current window layout to two columns, even if you had more open
* There are probably more bugs

## How to install

It's available on package control!

## Setting a keybinding

The open the preview, you can search up in the command palette
(<kbd>ctrl+shift+p</kbd>) `MarkdownLivePreview: Open Preview`. But if you
prefer to have a shortcut, add this to your keybindings file:

```json
{
    "keys": ["alt+m"],
    "command": "open_markdown_preview"
}
```

## How to contribute

If you know what feature you want to implement, or what bug you wanna fix, then
go ahead and hack! Maybe raise an issue before hand so that we can talk about
it if it's a big feature.

But if you wanna contribute just to say thanks, and don't really know what you
could be working on, then there are a bunch of `FIXME`s all over this package.
Just pick one and fix it :-)

```
$ git clone https://github.com/math2001/MarkdownLivePreview
$ cd MarkdownLivePreview
$ grep -R FIXME
```

### Hack it!

1. Fork this repo
2. Make your own branch (the name of the branch should be the feature you are
   implementing eg. `improve-tables`, `fix-crash-on-multiple-preview`
3. All your code should be formated by black.
4. Send a PR!

### Known limitations

#### Numbered lists are rendered as unordered lists

```md
1. first
2. second
3. third
```

will be previewed the exact same way as

```md
- first
- second
- third
```

The issue comes from [Sublime Text's minihtml](https://www.sublimetext.com/docs/3/minihtml.html) which [doesn't support ordered lists](https://github.com/sublimehq/sublime_text/issues/1767). If you think feel like implementing a workaround, feel free to contribute, but it's not something I'm planning on doing. It isn't a critical feature, and support should come with time...
