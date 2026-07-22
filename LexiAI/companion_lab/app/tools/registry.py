from typing import Dict

ALLOWLISTED_TOOLS: Dict[str, str] = {
    "file.read": "Read file contents from the local workspace",
    "file.list": "List files in a directory",
    "system.info": "Gather system information",
}


def get_tool_registry():
    return ALLOWLISTED_TOOLS
