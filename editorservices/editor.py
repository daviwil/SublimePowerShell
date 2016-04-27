import sublime
from .client import client
from .logger import log
from .messages import *
from .utils import *

class EditorClient:

    def __init__(self):
        self.openedFiles = {}

    def start(self):
        # Attach event handlers to the client
        log.debug("Initializing listeners")
        client.setEventHandler(DiagnosticsEvent, self._handle_diagnostics)
        client.setEventHandler(OutputEvent, self._handle_output)

        client.setEventHandler(ExtensionCommandAddedEvent, self._handle_command_added)
        client.setRequestHandler(InsertTextRequest, self._handle_insert_text)

        # Open all existing PowerShell views in the language server
        win = sublime.active_window()
        for view in win.views():
            self.file_opened(view)

    def file_opened(self, view):
        file_name = view.file_name()
        if is_ps_file(view):
            if file_name not in self.openedFiles:
                client.sendEvent(
                    FileOpenedEvent(
                        view.file_name(),
                        get_view_contents(view)))

            # Add the file and view to the opened files list
            fileViews = self.openedFiles.get(file_name, set())
            fileViews.add(view.id())
            self.openedFiles[file_name] = fileViews
            log.debug("Added new view '%d' for file '%s'", view.id(), file_name)

    def file_closed(self, view):
        file_name = view.file_name()
        if is_ps_file(view):
            fileViews = self.openedFiles.get(file_name)
            if fileViews:
                # Remove the view and see if any other views are left
                fileViews.remove(view.id())
                if len(fileViews) == 0:
                    # Close the file and remove it from the opened files list
                    del self.openedFiles[file_name]
                    client.sendEvent(
                        FileClosedEvent(
                            view.file_name()))

    def file_changed(self, view):
        pass

    def _handle_diagnostics(self, diagnostics):
        log.debug("Diagnostics received for file: %s", diagnostics.uri)
        win = sublime.active_window()
        view = win.find_open_file(diagnostics.uri)

        if view:
            log.debug("Found view for file, adding regions")
            regions = []
            for diagnostic in diagnostics.diagnostics:
                markerRange = diagnostic.get("range")
                start = markerRange.get("start")
                end = markerRange.get("end")
                regions.append(
                    self._get_region(
                        view,
                        int(start.get("line")),
                        int(start.get("character")),
                        int(end.get("line")),
                        int(end.get("character"))))

            view.add_regions(
                "powershell_errors",
                regions,
                "keyword",
                flags=sublime.DRAW_SQUIGGLY_UNDERLINE|sublime.DRAW_NO_FILL|sublime.DRAW_NO_OUTLINE
            )

    def _handle_output(self, output):
        win = sublime.active_window()
        win.run_command("powershell_write_output", { "outputText": output.output.replace("\r", "") })

    def _handle_command_added(self, command):
        log.debug("COMMAND ADDED EVENT: %s", command.displayName)
        win = sublime.active_window()
        sublime.run_command("powershell_add_command", { "command": { "name": command.name, "displayName": command.displayName }})

    def _handle_insert_text(self, insertDetails):
        log.debug("INSERTING TEXT: %s", insertDetails.InsertText)
        fileView = sublime.active_window().find_open_file(insertDetails.FilePath)
        if fileView:
            fileView.run_command("powershell_insert_text", {
                "insertText": insertDetails.InsertText.replace("\r", ""),
                "insertRange": insertDetails.InsertRange.to_dict()
            })
            return 1   # Value of OK
        else:
            # TODO: Should open the file to be edited...
            log.debug("Could not find open file to apply edit: %s", insertDetails.FilePath)
            return 0

    def _get_region(self, view, startLine, startColumn, endLine, endColumn):
        return sublime.Region(
            view.text_point(startLine, startColumn),
            view.text_point(endLine, endColumn))

# Export a top-level client variable that is used by other modules
editor = EditorClient()