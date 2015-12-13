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

    def _get_region(self, view, startLine, startColumn, endLine, endColumn):
        return sublime.Region(
            view.text_point(startLine, startColumn),
            view.text_point(endLine, endColumn))

# Export a top-level client variable that is used by other modules
editor = EditorClient()