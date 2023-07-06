from ..utils import tile2quad, get_server_num


BING_DEFAULT_VERSION = '5001'


def provider_bing_base(pos, type, **kwargs):
    x, y, z = pos
    quadkey = tile2quad(x, y, z)
    subdomain = get_server_num(x, y, 4)
    if isinstance(subdomain, int):
        subdomain = f't{subdomain}'
    url = f'http://ecn.{subdomain}.tiles.virtualearth.net/tiles/{type}{quadkey}.jpeg'
    if 'g' not in kwargs:
        kwargs['g'] = BING_DEFAULT_VERSION
    queries = []
    for k, v in kwargs.items():
        queries.append(f'{k}={v}')
    if queries:
        url += '?' + '&'.join(queries)
    return url


def provider_bing_aerial(pos, **kwargs):
    return provider_bing_base(pos, type='a', **kwargs)


def provider_bing_road(pos, **kwargs):
    return provider_bing_base(pos, type='r', **kwargs)


def provider_bing_terrain(pos, **kwargs):
    return provider_bing_base(pos, type='t', **kwargs)


def provider_bing_hybrid(pos, **kwargs):
    return provider_bing_base(pos, type='h', **kwargs)


providers = {
    'bing_aerial': provider_bing_aerial,
    'bing_road': provider_bing_road,
    'bing_terrain': provider_bing_terrain,
    'bing_hybrid': provider_bing_hybrid,
}
