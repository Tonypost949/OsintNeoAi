import os
import streamlit.components.v1 as components

# Build the component
parent_dir = os.path.dirname(os.path.abspath(__file__))
build_dir = os.path.join(parent_dir, "frontend")
_component_func = components.declare_component("folder_picker", path=build_dir)


def folder_picker(key=None):
    """
    Folder picker button. Returns list of file dicts when user picks a folder.
    """
    return _component_func(default=[], key=key)
