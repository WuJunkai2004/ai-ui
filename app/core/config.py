import tomli
import os
from pydantic import BaseModel

class Settings(BaseModel):
    api_base: str
    api_key: str
    model: str
    max_tokens: int = 4096
    temperature: float = 0.6
    mcp_config_path: str = "mcp_config.json"

    @classmethod
    def load(cls) -> "Settings":
        config_path = "config.toml"
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"{config_path} not found")
        
        with open(config_path, "rb") as f:
            data = tomli.load(f)
            
        # Map config keys to Settings keys
        return cls(
            api_base=data.get("api"),
            api_key=data.get("secret"),
            model=data.get("model"),
            max_tokens=data.get("max_tokens", 4096),
            temperature=data.get("temperature", 0.6)
        )

settings = Settings.load()
