from .protocol import request, event

# Request Types

@request("initialize")
class InitializeRequest:
    def __init__(self, rootPath):
        self.rootPath = rootPath
        self.capabilities = {}

# Event Types

@event("textDocument/didOpen")
class FileOpenedEvent:
    def __init__(self, uri, text):
        self.uri = uri
        self.text = text

@event("textDocument/didClose")
class FileClosedEvent:
    def __init__(self, uri):
        self.uri = uri

@event("textDocument/didClose")
class FileChangedEvent:
    def __init__(self, uri, region, text):
        self.uri = uri
        self.contentChanges = [
            {
                "start": {
                    "line": region.start.line
                },
                "end": {

                }
            }
        ]
        self.text = text

@event("textDocument/publishDiagnostics")
class DiagnosticsEvent:
    def __init__(self, params):
        self.uri = params.get("uri")
        self.diagnostics = params.get("diagnostics", [])

# Utility Types

#class Region:

#    def __init__(self, startLine, startColumn, endLine, endColumn):
#        this.