from bingtiles import *
from bingtiles.provider import providers

import argparse


def main():
    parser = argparse.ArgumentParser(description='Small utility for accessing Bing Static Maps API')
    parser.add_argument('command', choices=['tile', 'map'])
    parser.add_argument('lat', type=float)
    parser.add_argument('lon', type=float)
    parser.add_argument('lat2', type=float, nargs='?')
    parser.add_argument('lon2', type=float, nargs='?')
    parser.add_argument('-l', '--lod', type=int, default=17)
    parser.add_argument('-o', '--output', default=None)
    parser.add_argument('-p', '--progress', action='store_true')
    parser.add_argument('-z', '--cache-file', default=None)
    parser.add_argument('-t', '--tile-provider', choices=providers.keys(), default='bing_hybrid')
    args = parser.parse_args()
    provider = providers[args.tile_provider]
    fetcher = CachedFetcher(args.cache_file, provider)
    if args.command == 'tile':
        tile = geodetic2tile(args.lat, args.lon, args.lod)
        tile = tuple(map(math.floor, tile))
        img = fetcher(tile)
        if args.output is None:
            img.show()
        else:
            img.save(args.output)
    elif args.command == 'map':
        geo1 = (args.lat, args.lon)
        if args.lat2 is None:
            lat2 = args.lat
        else:
            lat2 = args.lat2
        if args.lon2 is None:
            lon2 = args.lon
        else:
            lon2 = args.lon2
        geo2 = (lat2, lon2)
        img = generate_map(geo1, geo2,
                           lod=args.lod, progress=args.progress, fetcher=fetcher)
        if args.output is None:
            img.show()
        else:
            img.save(args.output)
