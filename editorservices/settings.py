import sublime

class PowerShellPluginSettings:

    def __init__(self, settingsPath):
        userSettings = sublime.load_settings(settingsPath)
        pluginSettings = userSettings.get('powershell_plugin', {})
        
        self.developer = PowerShellPluginDeveloperSettings(pluginSettings.get("developer", {}))

class PowerShellPluginDeveloperSettings:

    def __init__(self, settings):
        self.editorServicesHostPath = settings.get("editor_services_host_path")
        self.waitForDebugger = settings.get("wait_for_debugger", False)