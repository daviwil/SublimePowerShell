import os
import sublime

_PowerShellExtensions = set([
        "ps1",
        "psd1",
        "psm1",
        "ps1xml",
        "pssc",
        "psrc"
    ])

def is_ps_file(view):
    filePath = view.file_name()
    if filePath:
        (root, ext) = os.path.splitext(filePath)
        return ext.lstrip('.') in _PowerShellExtensions
    else:
        # TODO: Support untitled buffers marked as PowerShell
        return False

def get_view_contents(view):
    return view.substr(sublime.Region(0, view.size()))