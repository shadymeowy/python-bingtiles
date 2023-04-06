import math

EARTH_RADIUS = 6378137
MIN_LATITUDE = -85.05112878
MAX_LATITUDE = 85.05112878
MIN_LONGITUDE = -180
MAX_LONGITUDE = 180


def _clip(n, min_value, max_value):
    """
        Clips a number to the specified minimum and maximum values.
        :param n: The number to clip.
        :param min_value: Minimum allowable value.
        :param max_value: Maximum allowable value.
        :return: The clipped value.
    """
    return min(max(n, min_value), max_value)


def get_map_size(level_of_detail):
    """
        Determines the map width and height (in pixels) at a specified level of detail.
        :param level_of_detail: Level of detail, from 1 (lowest detail) to 23 (highest detail).
        :return: The map width and height in pixels.
    """
    return 256 << level_of_detail


def ground_resolution(latitude, level_of_detail):
    """
        Determines the ground resolution (in meters per pixel) at a specified latitude and level of detail.
        :param latitude: Latitude (in degrees) at which to measure the ground resolution.
        :param level_of_detail: Level of detail, from 1 (lowest detail) to 23 (highest detail).
        :return: The ground resolution, in meters per pixel.
    """
    latitude = _clip(latitude, MIN_LATITUDE, MAX_LATITUDE)
    return math.cos(latitude * math.pi / 180) * 2 * math.pi * EARTH_RADIUS / get_map_size(level_of_detail)


def map_scale(latitude, level_of_detail, screen_dpi):
    """
        Determines the map scale at a specified latitude, level of detail, and screen resolution.
        :param latitude: Latitude (in degrees) at which to measure the map scale.
        :param level_of_detail: Level of detail, from 1 (lowest detail) to 23 (highest detail).
        :param screen_dpi: Resolution of the screen, in dots per inch.
        :return: The map scale, expressed as the denominator N of the ratio 1 : N.
    """
    return ground_resolution(latitude, level_of_detail) * screen_dpi / 0.0254


def geodetic2pixel(latitude, longitude, level_of_detail):
    """
        Converts a point from latitude/longitude WGS-84 coordinates (in degrees) into pixel XY coordinates at a specified level of detail.
        :param latitude: Latitude of the point, in degrees.
        :param longitude: Longitude of the point, in degrees.
        :param level_of_detail: Level of detail, from 1 (lowest detail) to 23 (highest detail).
        :return: The pixel coordinates in pixels.
    """
    latitude = _clip(latitude, MIN_LATITUDE, MAX_LATITUDE)
    longitude = _clip(longitude, MIN_LONGITUDE, MAX_LONGITUDE)

    x = (longitude + 180) / 360
    sin_latitude = math.sin(latitude * math.pi / 180)
    y = 0.5 - math.log((1 + sin_latitude) / (1 - sin_latitude)) / (4 * math.pi)

    map_size_ = get_map_size(level_of_detail)
    pixel_x = _clip(x * map_size_ + 0.5, 0, map_size_ - 1)
    pixel_y = _clip(y * map_size_ + 0.5, 0, map_size_ - 1)
    return pixel_x, pixel_y, level_of_detail


def pixel2geodetic(pixel_x, pixel_y, level_of_detail):
    """
        Converts a pixel from pixel XY coordinates at a specified level of detail into latitude/longitude WGS-84 coordinates (in degrees).
        :param pixel_x: X coordinate of the point, in pixels.
        :param pixel_y: Y coordinates of the point, in pixels.
        :param level_of_detail: Level of detail, from 1 (lowest detail) to 23 (highest detail).
        :return: The latitude and longitude of the specified pixel in degrees.
    """
    map_size_ = get_map_size(level_of_detail)
    x = (_clip(pixel_x, 0, map_size_ - 1) / map_size_) - 0.5
    y = 0.5 - (_clip(pixel_y, 0, map_size_ - 1) / map_size_)

    latitude = 90 - 360 * math.atan(math.exp(-y * 2 * math.pi)) / math.pi
    longitude = 360 * x
    return latitude, longitude


def pixel2pixel(pixel_x, pixel_y, level_of_detail, new_level_of_detail):
    """
        Converts pixel XY coordinates into tile XY coordinates of the tile containing the specified pixel.
        :param pixel_x: Pixel X coordinate.
        :param pixel_y: Pixel Y coordinate.
        :param level_of_detail: Level of detail, from 1 (lowest detail) to 23 (highest detail).
        :param new_level_of_detail: Level of detail, from 1 (lowest detail) to 23 (highest detail).
        :return: The pixel coordinates in pixels.
    """
    map_size_ = get_map_size(level_of_detail)
    new_map_size_ = get_map_size(new_level_of_detail)
    x = (pixel_x - 0.5) / map_size_
    y = (pixel_y - 0.5) / map_size_
    new_pixel_x = _clip(x * new_map_size_ + 0.5, 0, new_map_size_ - 1)
    new_pixel_y = _clip(y * new_map_size_ + 0.5, 0, new_map_size_ - 1)
    return new_pixel_x, new_pixel_y, new_level_of_detail


def pixel2tile(pixel_x, pixel_y, level_of_detail):
    """
        Converts pixel XY coordinates into tile XY coordinates of the tile containing the specified pixel.
        :param pixel_x: Pixel X coordinate.
        :param pixel_y: Pixel Y coordinate.
        :return: The tile X and Y coordinates.
    """
    tile_x = pixel_x / 256
    tile_y = pixel_y / 256
    return tile_x, tile_y, level_of_detail


def tile2pixel(tile_x, tile_y, level_of_detail):
    """
        Converts tile XY coordinates into pixel XY coordinates of the upper-left pixel of the specified tile.
        :param tile_x: Tile X coordinate.
        :param tile_y: Tile Y coordinate.
        :return: The pixel X and Y coordinates.
    """
    pixel_x = tile_x * 256
    pixel_y = tile_y * 256
    return pixel_x, pixel_y, level_of_detail


def tile2tile(tile_x, tile_y, level_of_detail, new_level_of_detail):
    """
        Converts tile XY coordinates into tile XY coordinates of the tile at a specified level of detail.
        :param tile_x: Tile X coordinate.
        :param tile_y: Tile Y coordinate.
        :param level_of_detail: Level of detail, from 1 (lowest detail) to 23 (highest detail).
        :param new_level_of_detail: Level of detail, from 1 (lowest detail) to 23 (highest detail).
        :return: The tile X and Y coordinates.
    """
    pixel = tile2pixel(tile_x, tile_y, level_of_detail)
    new_pixel = pixel2pixel(*pixel, new_level_of_detail)
    return pixel2tile(*new_pixel)


def tile2geodetic(tile_x, tile_y, level_of_detail):
    """
        Converts tile XY coordinates into a QuadKey at a specified level of detail.
        :param tile_x: Tile X coordinate.
        :param tile_y: Tile Y coordinate.
        :param level_of_detail: Level of detail, from 1 (lowest detail) to 23 (highest detail).
        :return: A string containing the QuadKey.
    """
    pixel = tile2pixel(tile_x, tile_y, level_of_detail)
    return pixel2geodetic(*pixel)


def geodetic2tile(latitude, longitude, level_of_detail):
    """
        Converts a point from latitude/longitude WGS-84 coordinates (in degrees) into tile XY coordinates of the tile containing the specified point.
        :param latitude: Latitude of the point, in degrees.
        :param longitude: Longitude of the point, in degrees.
        :param level_of_detail: Level of detail, from 1 (lowest detail) to 23 (highest detail).
        :return: The tile X and Y coordinates.
    """
    pixel = geodetic2pixel(latitude, longitude, level_of_detail)
    return pixel2tile(*pixel)


def tile2quad(tile_x, tile_y, level_of_detail, nearest=False):
    """
        Converts tile XY coordinates into a QuadKey at a specified level of detail.
        :param tile_x: Tile X coordinate.
        :param tile_y: Tile Y coordinate.
        :param level_of_detail: Level of detail, from 1 (lowest detail) to 23 (highest detail).
        :return: A string containing the QuadKey.
    """
    if not nearest and (not isinstance(tile_x, int) or not isinstance(tile_y, int)):
        raise TypeError('tile_x, tile_y must be integers, consider rounding them first')
    tile_x = int(tile_x)
    tile_y = int(tile_y)
    quad_key = []
    for i in range(level_of_detail, 0, -1):
        digit = 0
        mask = 1 << (i - 1)
        if (tile_x & mask) != 0:
            digit += 1
        if (tile_y & mask) != 0:
            digit += 2
        quad_key.append(digit)
    return ''.join(map(str, quad_key))


def quad2tile(quad_key):
    """
        Converts a QuadKey into tile XY coordinates.
        :param quad_key: QuadKey of the tile.
        :return: The tile X and Y coordinates and the level of detail.
    """
    tile_x = 0
    tile_y = 0
    level_of_detail = len(quad_key)
    for i in range(level_of_detail, 0, -1):
        mask = 1 << (i - 1)
        if quad_key[level_of_detail - i] == '0':
            pass
        elif quad_key[level_of_detail - i] == '1':
            tile_x |= mask
        elif quad_key[level_of_detail - i] == '2':
            tile_y |= mask
        elif quad_key[level_of_detail - i] == '3':
            tile_x |= mask
            tile_y |= mask
        else:
            raise Exception('Invalid QuadKey digit sequence.')
    return tile_x, tile_y, level_of_detail


def get_server_num(tile_x, tile_y, max_server_num=4):
    """
        Returns a server number for a given tile.
        :param tile_x: Tile X coordinate.
        :param tile_y: Tile Y coordinate.
        :param level_of_detail: Level of detail, from 1 (lowest detail) to 23 (highest detail).
        :return: A server number.
    """
    return (tile_x + 2 * tile_y) % max_server_num
