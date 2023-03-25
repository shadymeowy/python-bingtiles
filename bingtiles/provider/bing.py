from ..utils import quad2tile, get_server_num


def provider_bing_base(quadkey, type, **kwargs):
    x, y, z = quad2tile(quadkey)
    subdomain = get_server_num(x, y, 4)
    if isinstance(subdomain, int):
        subdomain = f't{subdomain}'
    url = f'http://ecn.{subdomain}.tiles.virtualearth.net/tiles/{type}{quadkey}.jpeg'
    kwargs['g'] = 5001
    queries = []
    for k, v in kwargs.items():
        queries.append(f'{k}={v}')
    if queries:
        url += '?' + '&'.join(queries)
    return url


def provider_bing_aerial(quadkey, **kwargs):
    return provider_bing_base(quadkey, type='a', **kwargs)


def provider_bing_road(quadkey, **kwargs):
    return provider_bing_base(quadkey, type='r', **kwargs)


def provider_bing_terrain(quadkey, **kwargs):
    return provider_bing_base(quadkey, type='t', **kwargs)


def provider_bing_hybrid(quadkey, **kwargs):
    return provider_bing_base(quadkey, type='h', **kwargs)


providers = {
    'bing_aerial': provider_bing_aerial,
    'bing_road': provider_bing_road,
    'bing_terrain': provider_bing_terrain,
    'bing_hybrid': provider_bing_hybrid,
}
