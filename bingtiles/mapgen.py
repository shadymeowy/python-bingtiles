import math
import numpy as np
from PIL import Image

from .utils import geodetic2tile
from .fetch import fetch_tile


def generate_map(geo1, geo2, lod=18, provider=None, progress=False, fetcher=None):
    if fetcher is None:
        fetcher = fetch_tile
    tile1 = geodetic2tile(*geo1, lod)
    tile2 = geodetic2tile(*geo2, lod)
    tile_mn = min(tile1[0], tile2[0]), min(tile1[1], tile2[1])
    tile_mx = max(tile1[0], tile2[0]), max(tile1[1], tile2[1])
    tile_mn = tuple(map(math.floor, tile_mn))
    tile_mx = tuple(map(math.ceil, tile_mx))
    tiles = []
    for x in range(tile_mn[0], tile_mx[0] + 1):
        for y in range(tile_mn[1], tile_mx[1] + 1):
            tiles.append((x, y))
    if progress:
        from tqdm import tqdm
        it = tqdm(tiles)
    else:
        it = iter(tiles)
    images = [list() for _ in range(tile_mn[0], tile_mx[0] + 1)]
    for x, y in it:
        pos = x, y, lod
        image = fetcher(pos, provider=provider)
        images[x - tile_mn[0]].append(image)
    images = [np.concatenate(row, axis=0) for row in images]
    image = np.concatenate(images, axis=1)
    image = Image.fromarray(image)
    return image
