import io
import os
import tempfile
import base64

try:
    from functools import cache
except ImportError:
    from functools import lru_cache
    cache = lru_cache

import requests
from PIL import Image

from .provider import default_provider


def fetch_tile(pos, provider=None):
    if provider is None:
        provider = default_provider
    url = provider(pos)
    r = requests.get(url)
    if r.status_code != 200:
        raise ValueError(f'Failed to download tile {pos} from {url}')
    byts = io.BytesIO(r.content)
    image = Image.open(byts)
    return image


class CachedFetcher:
    def __init__(self, cache_path=None, provider=None):
        self.cache_path = cache_path
        self.tmp = cache_path is None
        if self.tmp:
            self.cache_path = tempfile.mkdtemp()
        else:
            if not os.path.exists(self.cache_path):
                os.makedirs(self.cache_path)
        if provider is None:
            provider = default_provider
        self.provider = provider

    @cache
    def __call__(self, pos, provider=None):
        if provider is None:
            provider = self.provider
        url = provider(pos)
        file_name = base64.b32hexencode(url.encode('utf-8')).decode('utf-8')
        file_path = os.path.join(self.cache_path, file_name)
        if not os.path.exists(file_path):
            r = requests.get(url)
            if r.status_code != 200:
                x, y, z = pos
                raise ValueError(f'Failed to download tile {x},{y},{z} from {url}')
            with open(file_path, 'wb') as f:
                f.write(r.content)
            byts = io.BytesIO(r.content)
            image = Image.open(byts)
            return image
        else:
            with open(file_path, 'rb') as f:
                byts = io.BytesIO(f.read())
                image = Image.open(byts)
                return image

    def fetch(self, pos, provider=None):
        if provider is None:
            provider = self.provider
        return self(pos, provider)

    def close(self):
        if self.tmp and os.path.exists(self.cache_path):
            os.rmdir(self.cache_path)

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
