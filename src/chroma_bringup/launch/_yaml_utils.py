"""
_yaml_utils.py
Shared utilities for loading, patching, and merging YAML files in launch scripts.
"""
import yaml
import copy
import tempfile

def merge_dicts(base, override):
    """Recursively merges override dictionary into base."""
    for key, value in override.items():
        if isinstance(value, dict) and key in base:
            merge_dicts(base[key], value)
        else:
            base[key] = copy.deepcopy(value)
    return base

def write_temp_yaml(data, prefix):
    """Writes a dictionary to a temporary YAML file, returning the path."""
    tmp = tempfile.NamedTemporaryFile(mode='w', prefix=prefix, suffix='.yaml', delete=False)
    yaml.dump(data, tmp)
    tmp.close()
    return tmp.name

def patch_and_write_yaml(filepath, replacements, prefix):
    """Reads a file, performs string replacements, and writes to a temp file."""
    with open(filepath, 'r') as f:
        content = f.read()

    for placeholder, value in replacements:
        content = content.replace(placeholder, value)

    tmp = tempfile.NamedTemporaryFile(mode='w', prefix=prefix, suffix='.yaml', delete=False)
    tmp.write(content)
    tmp.close()
    return tmp.name