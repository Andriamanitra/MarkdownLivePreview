"""
Terminology
original_view: the view in the regular editor, without it's own window
markdown_view: the markdown view, in the special window
preview_view: the preview view, in the special window
original_window: the regular window
preview_window: the window with the markdown file and the preview
"""

import time
import os.path
import struct
import sublime
import sublime_plugin

from functools import partial

from .markdown2html import markdown2html

MARKDOWN_VIEW_INFOS = "markdown_view_infos"
PREVIEW_VIEW_INFOS = "preview_view_infos"
SETTING_DELAY_BETWEEN_UPDATES = "delay_between_updates"

resources = {}
preview_view = None

def plugin_loaded():
    global DELAY
    resources["base64_404_image"] = parse_image_resource(get_resource("404.base64"))
    resources["base64_loading_image"] = parse_image_resource(
        get_resource("loading.base64")
    )
    resources["stylesheet"] = get_resource("stylesheet.css")
    # FIXME: how could we make this setting update without restarting sublime text
    #        and not loading it every update as well
    DELAY = get_settings().get(SETTING_DELAY_BETWEEN_UPDATES)


class MdlpInsertCommand(sublime_plugin.TextCommand):
    def run(self, edit, point, string):
        self.view.insert(edit, point, string)


class ToggleMarkdownPreviewCommand(sublime_plugin.TextCommand):
    def run(self, edit):

        """ If the file is saved exists on disk, we close it, and reopen it in a new
        window. Otherwise, we copy the content, erase it all (to close the file without
        a dialog) and re-insert it into a new view into a new window """

        global preview_view
        if preview_view:
            preview_view.close()
            return

        original_view = self.view
        original_window_id = original_view.window().id()
        file_name = original_view.file_name()

        if not file_name:
            sublime.message_dialog("The file must be saved to be previewed!")
            return

        syntax_file = original_view.settings().get("syntax")

        original_view.close()
        
        preview_window = sublime.active_window()

        preview_window.run_command(
            "set_layout",
            {
                "cols": [0.0, 0.5, 1.0],
                "rows": [0.0, 1.0],
                "cells": [[0, 0, 1, 1], [1, 0, 2, 1]],
            },
        )

        preview_window.focus_group(1)
        preview_view = preview_window.new_file()
        preview_view.set_scratch(True)
        preview_view.settings().set(PREVIEW_VIEW_INFOS, {})
        preview_view.settings().set("line_numbers", False)
        
        view_name = os.path.split(file_name)[-1] + " (Markdown Preview)"
        preview_view.set_name(view_name)
        # FIXME: hide number lines on preview

        preview_window.focus_group(0)

        markdown_view = preview_window.open_file(file_name)

        markdown_view.set_syntax_file(syntax_file)
        markdown_view.settings().set(
            MARKDOWN_VIEW_INFOS, {"original_window_id": original_window_id,},
        )

    def is_enabled(self):
        # FIXME: is this the best way there is to check if the current syntax is markdown?
        #        should we only support default markdown?
        #        what about "md"?
        # FIXME: what about other languages, where markdown preview roughly works?
        current_syntax = self.view.settings().get("syntax").lower()
        return "markdown" in current_syntax or "plain" in current_syntax


class MarkdownLivePreviewListener(sublime_plugin.EventListener):

    phantom = None

    # we schedule an update for every key stroke, with a delay of DELAY
    # then, we update only if now() - last_update > DELAY
    last_update = 0

    def on_pre_close(self, view):
        self.window = view.window()

    def on_close(self, view):
        global preview_view
        if preview_view and view.id() == preview_view.id():
            self.phantom = None
            preview_view = None
            if not self.window.views_in_group(1):
                # Restore single column layout if the preview was the last view in the group
                self.window.run_command(
                    "set_layout",
                    {
                        "cols": [0.0, 1.0],
                        "rows": [0.0, 1.0],
                        "cells": [[0, 0, 1, 1]],
                    },
                )

    def on_load_async(self, markdown_view):
        infos = markdown_view.settings().get(MARKDOWN_VIEW_INFOS)
        if not infos:
            return

        global preview_view
        self.phantom = sublime.PhantomSet(preview_view)
        self._update_preview(markdown_view)

    # here, views are NOT treated independently, which is theoretically wrong
    # but in practice, you can only edit one markdown file at a time, so it doesn't really
    # matter.
    # @min_time_between_call(.5)
    def on_modified_async(self, markdown_view):

        infos = markdown_view.settings().get(MARKDOWN_VIEW_INFOS)
        if not infos:
            return

        # we schedule an update, which won't run if an
        sublime.set_timeout(partial(self._update_preview, markdown_view), DELAY)

    def _update_preview(self, markdown_view):
        # if the buffer id is 0, that means that the markdown_view has been closed
        # This check is needed since a this function is used as a callback for when images
        # are loaded from the internet (ie. it could finish loading *after* the user
        # closes the markdown_view)
        if time.time() - self.last_update < DELAY / 1000:
            return

        if markdown_view.buffer_id() == 0 or self.phantom is None:
            return

        self.last_update = time.time()

        total_region = sublime.Region(0, markdown_view.size())
        markdown = markdown_view.substr(total_region)

        global preview_view
        viewport_width = preview_view.viewport_extent()[0]

        basepath = os.path.dirname(markdown_view.file_name())
        html = markdown2html(
            markdown,
            basepath,
            partial(self._update_preview, markdown_view),
            resources,
            viewport_width,
        )

        self.phantom.update(
            [
                sublime.Phantom(
                    sublime.Region(0),
                    html,
                    sublime.LAYOUT_BLOCK,
                    lambda href: sublime.run_command("open_url", {"url": href}),
                )
            ]
        )


def get_settings():
    return sublime.load_settings("MarkdownLivePreview.sublime-settings")


def get_resource(resource):
    path = "Packages/MarkdownLivePreview/resources/" + resource
    abs_path = os.path.join(sublime.packages_path(), "..", path)
    if os.path.isfile(abs_path):
        with open(abs_path, "r") as fp:
            return fp.read()
    return sublime.load_resource(path)


def parse_image_resource(text):
    width, height, base64_image = text.splitlines()
    return base64_image, (int(width), int(height))


# try to reload the resources if we save this file
try:
    plugin_loaded()
except OSError:
    pass
