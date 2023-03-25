from bingtiles import generate_map, providers

if __name__ == '__main__':
    # Specify corner coordinates of the map
    geo1 = 39.89250693, 32.78414742
    geo2 = 39.89055783, 32.7869366
    # Specify the level of detail
    lod = 19
    # Create cached fetcher if you want to cache the tiles
    # fetcher = CachedFetcher('tiles')
    # Otherwise, use the default fetcher
    fetcher = None
    # Parameters for the map
    provider = providers['bing_aerial']
    params = dict(
        provider=provider,
        fetcher=fetcher,
        progress=True,
        parallel=True,
    )
    # Generate the map
    img = generate_map(geo1, geo2, lod, **params)
    # Close the fetcher if it is a cached fetcher
    # fetcher.close()
    # Show the map
    img.show()
    # Save the map
    img.save('map.png')
