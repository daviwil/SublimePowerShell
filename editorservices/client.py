from .protocol import write_message, read_message, MessageType
from .messages import InitializeRequest
from .logger import log
import io
import os
import sublime
import subprocess
import threading

class LanguageServerClient:
    __isRunning = False

    def start(self, editorServicesHostPath, waitForDebugger=False):
        self._editorServicesHostPath = editorServicesHostPath
        self.messageId = 0

        args = [self._editorServicesHostPath]
        startupinfo = None
        
        if os.name == "nt":
            # Hide the console on startup
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.SW_HIDE | subprocess.STARTF_USESHOWWINDOW

        if waitForDebugger:
            args.append("/waitForDebugger")

        self.languageServerProcess = subprocess.Popen(
            args,
            bufsize=io.DEFAULT_BUFFER_SIZE,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            startupinfo=startupinfo,
            universal_newlines=False)

        self.stdIn = self.languageServerProcess.stdin
        self.stdOut = self.languageServerProcess.stdout

        self.requestCallbacks = {}
        self.eventHandlers = {}

        # Start a new thread for the message loop
        LanguageServerClient.__isRunning = True
        self.readerThread = threading.Thread(
            target=LanguageServerClient.__messageLoop,
            args=(self.stdIn, self.stdOut, self.requestCallbacks, self.eventHandlers))
        self.readerThread.daemon = True
        self.readerThread.start()

        # Send the Initialize message
        self.sendRequest(InitializeRequest(""), self.__handleInitializeResponse)

    def stop(self):
        sublime.message_dialog("Kill it!")
        if LanguageServerClient.__isRunning:
            LanguageServerClient.__isRunning = False
            self.languageServerProcess.kill()
            sublime.message_dialog("SHould be killed!")
            self.languageServerProcess = None

    def sendRequest(self, request, callback):
        self.messageId = self.messageId + 1
        self.requestCallbacks[self.messageId] = callback
        write_message(request, self.messageId, self.stdIn)

    def sendEvent(self, event):
        write_message(event, 0, self.stdIn)

    def setEventHandler(self, eventType, eventHandler):
        log.debug("Attempting to set handler...")
        
        # Is the type an event?
        if hasattr(eventType, "__type") and \
            hasattr(eventType, "__method") and \
            getattr(eventType, "__type") == MessageType.Event:

            def _handler(params):
                # Create an instance of the event type and pass its params
                eventHandler(eventType(params))

            methodName = getattr(eventType, "__method")
            self.eventHandlers[methodName] = _handler
            log.debug("Registered handler for event '%s'", methodName)

        else:
            log.error("Attempted to register handler for non-event type '%s'", eventType)

    def __handleInitializeResponse(self, response):
        log.debug("Client got initialize response!")
        #print response

    @staticmethod
    def __messageLoop(stdIn, stdOut, requestCallbacks, eventHandlers):
        while LanguageServerClient.__isRunning:
            message = read_message(stdOut)

            #print "GOT MESSAGE: " + str(message)

            messageId = int(message.get("id", "0"))
            if messageId == 0 and "params" in message:
                # Handle the event
                method = message.get("method")
                log.debug("Received event '%s'", method)
                handler = eventHandlers.get(method)
                if handler:
                    handler(message.get("params"))
                else:
                    log.debug("No event handler found for event '%s'", method)

            elif messageId > 0:
                method = message.get("method", None)
                if not method:
                    # Handle the response
                    responseCallback = requestCallbacks.get(messageId)
                    if responseCallback:
                        # TODO: Handle error
                        responseCallback(message.get("result", {}))
                        del requestCallbacks[messageId]
                else:
                    # Received a request?  Error?
                    pass

            else:
                #print "Unexpected message contents!"
                #print message
                pass

    @staticmethod
    def setActiveClient(languageServerClient):
        client = languageServerClient
        
# Export a top-level client variable that is used by other modules
client = LanguageServerClient()
