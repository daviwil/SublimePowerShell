import sublime

class PowerShellPluginSettings:

    def __init__(self, settingsPath):
        userSettings = sublime.load_settings(settingsPath)
        pluginSettings = userSettings.get('powershell_plugin', {})

        self.developer = PowerShellPluginDeveloperSettings(pluginSettings.get("developer", {}))

class PowerShellPluginDeveloperSettings:

    def __init__(self, settings):
        self.editorServicesModulePath = settings.get("editor_services_module_path")
        self.waitForDebugger = settings.get("wait_for_debugger", False)