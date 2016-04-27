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

        hostPath = settings.developer.editorServicesHostPath
        if not hostPath:
            hostPath = os.path.expanduser("~\\.vscode\\extensions\\ms-vscode.PowerShell\\bin\\Microsoft.PowerShell.EditorServices.Host.exe")
            log.info("Using default PowerShell Editor Services Host path: %s", hostPath)
        else:
            log.info("Found PowerShell Editor Services Host Path from settings: %s", hostPath)

        if os.path.exists(hostPath):
            client.start(hostPath, settings.developer.waitForDebugger)

            # Start the editor client
            editor.start()

            log.info("PowerShell plugin started.")



        else:
            log.error("Could not find PowerShell Editor Services Host at this path!")

    else:
        # TODO: Show message to user?
        log.error("PowerShell Editor Services currently does not run on non-Windows OSes.")

def plugin_unloaded():

    log.info("PowerShell plugin stopping...")

    client.stop()

    log.info("PowerShell plugin stopped.")
