import os
import time
import sublime
from .editorservices.client import client
from .editorservices.editor import editor
from .editorservices.logger import log
from .editorservices.settings import PowerShellPluginSettings
from .editorservices.listeners import *
from .editorservices.commands import *

def plugin_loaded():

    log.info("PowerShell plugin starting...")

    if os.name == 'nt':

        # Load user settings
        settings = PowerShellPluginSettings("Preferences.sublime-settings")

        modulePath = settings.developer.editorServicesModulePath
        if modulePath:
            log.info("Found PowerShell Editor Services module path from settings: %s", modulePath)

        # Start the editor client
        client.start(modulePath, settings.developer.waitForDebugger)
        editor.start()

        log.info("PowerShell plugin started.")

    else:
        # TODO: Show message to user?
        log.error("PowerShell Editor Services currently does not run on non-Windows OSes.")

def plugin_unloaded():

    log.info("PowerShell plugin stopping...")

    client.stop()

    log.info("PowerShell plugin stopped.")
