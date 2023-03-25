import math
import numpy as np
from PIL import Image
from multiprocessing.dummy import Pool as ThreadPool

from .utils import geodetic2tile
from .fetch import fetch_tile


def generate_map(geo1, geo2, lod=18, provider=None, progress=False, parallel=True, fetcher=None):
    if fetcher is None:
        fetcher = fetch_tile
    if progress:
        from tqdm import tqdm
    tile1 = geodetic2tile(*geo1, lod)
    tile2 = geodetic2tile(*geo2, lod)
    tile_mn = min(tile1[0], tile2[0]), min(tile1[1], tile2[1])
    tile_mx = max(tile1[0], tile2[0]), max(tile1[1], tile2[1])
    tile_mn = tuple(map(math.floor, tile_mn))
    tile_mx = tuple(map(math.ceil, tile_mx))
    poses = []
    for x in range(tile_mn[0], tile_mx[0] + 1):
        for y in range(tile_mn[1], tile_mx[1] + 1):
            poses.append((x, y))

    def func(pos):  # TODO: rewrite this
        return (pos[0], fetcher((pos[0], pos[1], lod), provider=provider))
    if parallel:
        pool = ThreadPool()
        tiles = pool.imap(func, poses)
        tiles = list(tqdm(tiles, total=len(poses)))
        pool.close()
        pool.join()
    else:
        if progress:
            poses = tqdm(poses)
        tiles = list(map(func, poses))
    images = [list() for _ in range(tile_mn[0], tile_mx[0] + 1)]
    for tile in tiles:
        x, image = tile
        images[x - tile_mn[0]].append(image)
    images = [np.concatenate(row, axis=0) for row in images]
    image = np.concatenate(images, axis=1)
    image = Image.fromarray(image)
    return image
