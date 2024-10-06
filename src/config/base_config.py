class Config:
    def __init__(self, config_dict):
        self.config = config_dict

    @classmethod
    def get_config(cls):
        return cls.config
