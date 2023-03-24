from bingtiles import geodetic2tile, tile2quad, fetch_tile
from bingtiles.provider import provider_bing_hybrid

if __name__ == '__main__':
    # Specify the coordinates of the tile you want to download
    geo = 39.89093263, 32.78269956
    # Convert the coordinates to tile coordinates
    tile = geodetic2tile(*geo, 17)
    # Floor the tile coordinates since tile coordinates are integers
    tile = tuple(map(int, tile))
    # Convert the tile coordinates to quadkey
    quad = tile2quad(*tile)
    # Download the tile
    img = fetch_tile(quad, provider=provider_bing_hybrid)
    # Show the tile
    img.show()
    # Save the tile
    img.save(f'tile-{quad}.png')
