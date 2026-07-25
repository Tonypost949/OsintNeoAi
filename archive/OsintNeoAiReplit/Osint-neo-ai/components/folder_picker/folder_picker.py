import os
import streamlit.components.v1 as components

_RELEASE = True

if _RELEASE:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend", "build")
    _component_func = components.declare_component("folder_picker", path=build_dir)
else:
    _component_func = components.declare_component("folder_picker", url="http://localhost:3001")


def folder_picker(label="📁 Select Folder", key=None):
    """
    Returns a list of file dicts when the user picks a folder via webkitdirectory.
    Each dict: {"name": "file.jpg", "data": base64, "size": 12345, "relative_path": "..."}
    """
    component_value = _component_func(label=label, default=None, key=key)
    return component_value
