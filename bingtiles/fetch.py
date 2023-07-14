import io
import os
import tempfile
import base64
import functools

import requests
from PIL import Image
import numpy as np

try:
    import cv2
except ImportError:
    cv2 = None

from .provider import default_provider, providers


@functools.lru_cache(maxsize=1024)
def fetch_tile(pos, provider=None, as_array=False):
    if provider is None:
        provider = default_provider
    url = provider(pos)
    if os.path.exists(url):
        try:
            image = cv2.imread(url, cv2.IMREAD_UNCHANGED)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            if not as_array:
                image = Image.fromarray(image)
            return image
        except:
            image = Image.open(url)
            if as_array:
                image = np.array(image)
            return image
    r = requests.get(url)
    if r.status_code != 200:
        raise ValueError(f'Failed to download tile {pos} from {url}')
    byts = io.BytesIO(r.content)
    image = Image.open(byts)
    if as_array:
        image = np.array(image)
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
            provider = providers[default_provider]
        self.provider = provider
        self.__call__ = functools.lru_cache(maxsize=1024)(self.__call__)

    def __call__(self, pos, provider=None, only_cached=False, as_array=False):
        if provider is None:
            provider = self.provider
        url = provider(pos)
        file_name = base64.urlsafe_b64encode(url.encode('utf-8')).decode('utf-8')
        file_name += '.png'
        file_path = os.path.join(self.cache_path, file_name)
        if os.path.exists(file_path):
            image = self.read_image(file_path)
            if not as_array:
                image = Image.fromarray(image)
            return image
        elif not only_cached:
            pos = tuple(pos)
            image = fetch_tile(pos, provider)
            with open(file_path, 'wb') as f:
                image.save(f, format='png')
            if not as_array:
                image = Image.fromarray(image)
            return image
        else:
            return None

    def fetch(self, pos, provider=None, only_cached=False):
        if provider is None:
            provider = self.provider
        return self(pos, provider, only_cached)

    def close(self):
        if self.tmp and os.path.exists(self.cache_path):
            os.rmdir(self.cache_path)

    def read_image(self, path):
        try:
            image = cv2.imread(path, cv2.IMREAD_UNCHANGED)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            return image
        except:
            image = Image.open(path)
            return image

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
