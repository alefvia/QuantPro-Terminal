"""Runtime configuration for the Rithmic Test market-data connector.

Secrets are read only from environment variables. Vendor protobuf modules are loaded
from a runtime directory supplied from the user's licensed R|Protocol package and are
not redistributed by QuantPro.
"""

from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(frozen=True)
class RithmicRuntimeConfig:
    user: str
    password: str
    websocket_url: str
    proto_python_dir: Path
    system_name: str = "Rithmic Test"
    exchange: str = "CME"
    root_symbol: str = "MNQ"

    @classmethod
    def from_env(cls) -> "RithmicRuntimeConfig":
        required = {
            "RITHMIC_API_USER": os.getenv("RITHMIC_API_USER"),
            "RITHMIC_API_PASSWORD": os.getenv("RITHMIC_API_PASSWORD"),
            "RITHMIC_WSS_URL": os.getenv("RITHMIC_WSS_URL"),
            "RITHMIC_PROTO_PY_DIR": os.getenv("RITHMIC_PROTO_PY_DIR"),
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise RuntimeError("Missing Rithmic runtime secrets/config: " + ", ".join(missing))
        url = str(required["RITHMIC_WSS_URL"])
        if not url.startswith("wss://"):
            raise RuntimeError("RITHMIC_WSS_URL must use wss://")
        return cls(
            user=str(required["RITHMIC_API_USER"]),
            password=str(required["RITHMIC_API_PASSWORD"]),
            websocket_url=url,
            proto_python_dir=Path(str(required["RITHMIC_PROTO_PY_DIR"])),
        )
