class Config:
    def __init__(self, config_dict: dict, credentials: dict):
        self.config = config_dict

    @classmethod
    def get_config(cls) -> dict[str, str]:
        return cls.config
