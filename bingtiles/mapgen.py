import numpy as np
from PIL import Image
from multiprocessing.dummy import Pool as ThreadPool
from tqdm import tqdm
from functools import lru_cache

try:
    import cv2
except ImportError:
    cv2 = None

from .utils import geodetic2tile
from .fetch import fetch_tile


class MapGenerator:
    def __init__(self, provider=None, fetcher=None, progress=False, parallel=True):
        self.provider = provider
        self.fetcher = fetcher
        self.progress = progress
        self.parallel = parallel

        if self.fetcher is None:
            self.fetcher = fetch_tile
        if self.parallel:
            self.pool = ThreadPool()

        self._rough_gen = lru_cache(maxsize=4)(self._rough_gen)

    def generate_map(self, geo1, geo2, lod, as_array=False):
        compound = calculate_coverage(geo1, geo2, lod)
        tile_mn, tile_mx, tile_mn_frac, tile_mx_frac = compound

        tile_mn = tuple(map(int, tile_mn))
        tile_mx = tuple(map(int, tile_mx))
        image = self._rough_gen(tile_mn, tile_mx, lod)
        tile_mx_frac -= 256
        e0 = tile_mx_frac[0] if tile_mx_frac[0] != 0 else None
        e1 = tile_mx_frac[1] if tile_mx_frac[1] != 0 else None
        image_cropped = image[tile_mn_frac[1]:e1, tile_mn_frac[0]:e0]
        if not as_array:
            image_cropped = Image.fromarray(image_cropped)
        return image_cropped

    __call__ = generate_map

    def _rough_gen(self, tile_mn, tile_mx, lod):
        tile_mn = np.array(tile_mn, np.int32)
        tile_mx = np.array(tile_mx, np.int32)
        tile_size = tile_mx - tile_mn
        poses = _tile_grid(tile_mn, tile_mx, lod)
        if self.parallel:
            tiles = self.pool.imap(self._fetch, poses)
            if self.progress:
                tiles = list(tqdm(tiles, total=len(poses)))
            else:
                tiles = list(tiles)
        else:
            if self.progress:
                poses = tqdm(poses)
            tiles = list(map(self._fetch, poses))
        images = [list() for _ in range(tile_size[0] + 1)]

        for tile in tiles:
            x, image = tile
            images[x - poses[0][0]].append(image)

        images = [np.concatenate(row, axis=0) for row in images]
        image = np.concatenate(images, axis=1)
        return image

    def _fetch(self, pos):
        if self.provider is None:
            return (pos[0], self.fetcher(tuple(pos.tolist()), as_array=True))
        else:
            return (pos[0], self.fetcher(tuple(pos.tolist()), provider=self.provider, as_array=True))

    def close(self):
        if self.parallel:
            self.pool.close()
            self.pool.join()

    def __del__(self):
        self.close()


def generate_map(geo1, geo2, lod=18, provider=None, progress=False, parallel=True, as_array=False, fetcher=None):
    generator = MapGenerator(
        provider=provider, fetcher=fetcher, progress=progress, parallel=parallel)
    return generator.generate_map(geo1, geo2, lod, as_array=as_array)


def _tile_grid(tile_mn, tile_mx, lod):
    xs = np.arange(tile_mn[0], tile_mx[0] + 1, dtype=np.int32)
    ys = np.arange(tile_mn[1], tile_mx[1] + 1, dtype=np.int32)
    poses = np.array(np.meshgrid(xs, ys)).T.reshape(-1, 2)
    zs = lod * np.ones(len(poses), dtype=np.int32)
    poses = np.concatenate([poses, zs[:, None]], axis=1)
    return poses


def calculate_coverage(geo1, geo2, lod=18):
    tile1 = np.array(geodetic2tile(*geo1, lod)[:2], np.float64)
    tile2 = np.array(geodetic2tile(*geo2, lod)[:2], np.float64)
    tile_mn_f = np.min([tile1, tile2], axis=0)
    tile_mx_f = np.max([tile1, tile2], axis=0)
    tile_mn = np.array(tile_mn_f, np.int32)
    tile_mx = np.array(tile_mx_f, np.int32)
    tile_mn_frac = 256 * (tile_mn_f - tile_mn)
    tile_mx_frac = 256 * (tile_mx_f - tile_mx)
    tile_mn_frac = np.round(tile_mn_frac).astype(np.int32)
    tile_mx_frac = np.round(tile_mx_frac).astype(np.int32)
    return tile_mn, tile_mx, tile_mn_frac, tile_mx_frac


def split_map(image, geo1, geo2, lod=18, as_array=False):
    if isinstance(image, Image.Image):
        image = np.array(image).astype(np.uint8)
    compound = calculate_coverage(geo1, geo2, lod)
    tile_mn, tile_mx, tile_mn_frac, tile_mx_frac = compound
    poses = _tile_grid(tile_mn, tile_mx, lod)
    tile_size = tile_mx - tile_mn
    image_full_size = 256 * (tile_size + 1)
    if len(image.shape) == 3:
        image_full_size = np.concatenate([image_full_size[::-1], [3]])
    else:
        image_full_size = image_full_size[::-1]
    image_size = 256 * tile_size + tile_mx_frac - tile_mn_frac
    if not np.equal(image_size[::-1], image.shape[:2]).all():
        image = cv2.resize(image, tuple(image_size),
                           interpolation=cv2.INTER_NEAREST)
    padded = np.zeros(image_full_size, dtype=image.dtype)
    tile_mx_frac -= 256
    e0 = tile_mx_frac[0] if tile_mx_frac[0] != 0 else None
    e1 = tile_mx_frac[1] if tile_mx_frac[1] != 0 else None
    padded[tile_mn_frac[1]:e1, tile_mn_frac[0]:e0] = image
    images = []
    for pos in poses:
        x, y, _ = pos - poses[0]
        image = padded[y * 256:(y + 1) * 256, x * 256:(x + 1) * 256]
        if not as_array:
            image = Image.fromarray(image)
        images.append((pos, image))
    return images
