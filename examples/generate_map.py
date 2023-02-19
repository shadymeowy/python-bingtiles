from bingtiles import generate_map

if __name__ == '__main__':
    # Specify corner coordinates of the map
    geo1 = 39.89250693, 32.78414742
    geo2 = 39.89055783, 32.7869366
    # Create cached fetcher if you want to cache the tiles
    # fetcher = CachedFetcher('tiles.zip')
    # Otherwise, use the default fetcher
    fetcher = None
    # Parameters for the map
    params = dict(g=5001, code='a', lod=19)
    # Generate the map
    img = generate_map(geo1, geo2, progress=True, fetcher=fetcher, **params)
    # Show the map
    img.show()
    # Save the map
    img.save('map.png')
