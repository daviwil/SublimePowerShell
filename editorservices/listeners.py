import os
import sublime
import sublime_plugin
from .logger import log
from .client import client
from .editor import editor
from .messages import *

class PowerShellEventListener(sublime_plugin.EventListener):

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
        
        #editor.file_changed(view)
        pass
        
    def on_text_command(self, view, command_name, args):
        log.debug("TEXT COMMAND %s: %s", command_name, args)
        return None

    def post_text_command(self, view, command_name, args):
        log.debug("POST TEXT COMMAND %s: %s", command_name, args)

    def on_window_command(self, window, command_name, args):
        if command_name == "exit":
            log.info("Stopping client and exiting...")
            client.stop()
        elif command_name in ["close_all", "close_window", "close_project"]:
            log.info("Stopping client and exiting...")
            client.stop()
        
        return None