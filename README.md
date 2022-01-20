# MarkdownLivePreview

A simple plugin to preview your markdown as you type right in Sublime Text.
No dependencies!

## Differences with upstream

You probably want to use (and contribute to) the [upstream version](https://github.com/math2001/MarkdownLivePreview) instead.
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

Linux:
```
git clone git@github.com:Andriamanitra/MarkdownLivePreview.git ~/.config/sublime-text/Packages/MarkdownLivePreview
```

## Setting a keybinding

The open the preview, you can search up in the command palette
(<kbd>ctrl+shift+p</kbd>) `MarkdownLivePreview: Open Preview`. But if you
prefer to have a shortcut, add this to your keybindings file:

```json
{
    "keys": ["alt+m"],
    "command": "toggle_markdown_preview"
}
```

## Known limitations

### Numbered lists are rendered as unordered lists

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
