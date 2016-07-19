import os
import sublime
import sublime_plugin
from .logger import log
from .client import client
from .editor import editor
from .messages import *

class PowerShellEventListener(sublime_plugin.EventListener):

    def __init__(self):
        self.awaitingCompletions = False
        self.pendingCompletions = []

    def on_new(self, view):
        log.debug("on_new event")

    def on_load(self, view):
        editor.file_opened(view)

    def on_close(self, view):
        editor.file_closed(view)

    def on_modified(self, view):
        # NOTE: This method may not capture all changes to file contents,
        # especially around undo/redo.  Need to pay close attention to the
        # different scenarios.
        log.debug("on_modified")
        editor.file_changed(view)

    def on_query_completions(self, view, prefix, locations):
        log.debug("on_query_completions: '%s'", prefix)
        completionsList = []
        if self.awaitingCompletions:
            # This should be the second invocation after results have come back
            self.awaitingCompletions = False
            completionsList = self.pendingCompletions
            self.pendingCompletions = []
        else:
            # Request completions from the language server
            self.awaitingCompletions = True
            editor.get_completions(view, view.rowcol(locations[0]), self._handle_completions_result)

        return (completionsList, sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)

    def _handle_completions_result(self, view, completions):
        log.debug("Completion handler called!  Count: " + str(len(completions)))
        if self.awaitingCompletions and len(completions) > 0:
            # Hide the current auto-complete list and invoke it
            # again to show the list of pending completions
            self.pendingCompletions = [(completion["label"], completion["insertText"]) for completion in completions]
            view.run_command('hide_auto_complete')
            view.run_command("auto_complete", {
                'disable_auto_insert': True,
                'api_completions_only': False,
                'next_completion_if_showing': False,
                'auto_complete_commit_on_tab': True,
            })

    def post_text_command(self, view, command_name, args):
        log.debug("post_text_command %s: %s", command_name, args)
        editor.file_changed(view)

    def on_window_command(self, window, command_name, args):
        if command_name == "exit":
            log.info("Stopping client and exiting...")
            client.stop()
        elif command_name in ["close_all", "close_window", "close_project"]:
            log.info("Stopping client and exiting...")
            client.stop()

        return None