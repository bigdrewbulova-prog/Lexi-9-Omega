import platform
from typing import Dict


def get_system_info() -> Dict[str, str]:
    return {
        "platform": platform.system(),
        "platform_version": platform.version(),
        "machine": platform.machine(),
    }
