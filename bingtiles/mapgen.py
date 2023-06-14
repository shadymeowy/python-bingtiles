import math
import numpy as np
from PIL import Image
from multiprocessing.dummy import Pool as ThreadPool

try:
    import cv2
except ImportError:
    cv2 = None

from .utils import geodetic2tile
from .fetch import fetch_tile


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
    xs = np.arange(tile_mn[0], tile_mx[0] + 1, dtype=np.int32)
    ys = np.arange(tile_mn[1], tile_mx[1] + 1, dtype=np.int32)
    poses = np.array(np.meshgrid(xs, ys)).T.reshape(-1, 2)
    zs = lod * np.ones(len(poses), dtype=np.int32)
    poses = np.concatenate([poses, zs[:, None]], axis=1)
    return poses, tile_mx - tile_mn, tile_mn_frac, tile_mx_frac


def generate_map(geo1, geo2, lod=18, provider=None, progress=False, parallel=True, as_array=False, fetcher=None):
    if fetcher is None:
        fetcher = fetch_tile
    if progress:
        from tqdm import tqdm
    poses, tile_size, tile_mn_frac, tile_mx_frac = calculate_coverage(geo1, geo2, lod)

    def func(pos):  # TODO: rewrite this
        return (pos[0], fetcher(pos.tolist(), provider=provider))
    if parallel:
        pool = ThreadPool()
        tiles = pool.imap(func, poses)
        if progress:
            tiles = list(tqdm(tiles, total=len(poses)))
        else:
            tiles = list(tiles)
        pool.close()
        pool.join()
    else:
        if progress:
            poses = tqdm(poses)
        tiles = list(map(func, poses))
    images = [list() for _ in range(tile_size[0] + 1)]
    for tile in tiles:
        x, image = tile
        images[x - poses[0][0]].append(image)
    images = [np.concatenate(row, axis=0) for row in images]
    image = np.concatenate(images, axis=1)
    tile_mx_frac -= 256
    e0 = tile_mx_frac[0] if tile_mx_frac[0] != 0 else None
    e1 = tile_mx_frac[1] if tile_mx_frac[1] != 0 else None
    image_cropped = image[tile_mn_frac[1]:e1, tile_mn_frac[0]:e0]
    if not as_array:
        image_cropped = Image.fromarray(image_cropped)
    return image_cropped


def split_map(image, geo1, geo2, lod=18, as_array=False):
    if isinstance(image, Image.Image):
        image = np.array(image).astype(np.uint8)
    compound = calculate_coverage(geo1, geo2, lod)
    poses, tile_size, tile_mn_frac, tile_mx_frac = compound
    image_full_size = 256 * (tile_size + 1)
    image_full_size = np.concatenate([image_full_size, [3]])
    image_size = 256 * tile_size + tile_mx_frac - tile_mn_frac
    if image_size != image.shape:
        image = cv2.resize(image, tuple(image_size))
    padded = np.zeros(image_full_size, dtype=np.uint8)
    padded[tile_mn_frac[1]:tile_mn_frac[1] + image_size[1], tile_mn_frac[0]:tile_mn_frac[0] + image_size[0]] = image
    images = []
    for pos in poses:
        x, y, _ = pos - poses[0]
        image = padded[y * 256:(y + 1) * 256, x * 256:(x + 1) * 256]
        if not as_array:
            image = Image.fromarray(image)
        images.append((pos, image))
    return images
