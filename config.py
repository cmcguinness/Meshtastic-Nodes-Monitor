import tomllib
import logging

logger = logging.getLogger(__name__)

class Config:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            with open("config.toml", "rb") as f:
                self.data = tomllib.load(f)
            self.initialized = True

    def get(self, keys, default=None):
        """

        :param keys: can be either a list of keys or key or key1.key2...
        :param default: What to return if not found
        :return: either default or the value
        """
        data = self.data
        if '.' in keys:
            keys = keys.split('.')
        for key in keys:
            if key not in data:
                logger.warning(f'Key {keys} not found in config file.')
                return default
            data = data[key]
        return data


if __name__ == "__main__":
    c = Config()
    pass
