from ..utils import quad2tile


def provider_esri_base(quadkey, type='World_Imagery'):
    x, y, z = quad2tile(quadkey)
    url = f'https://server.arcgisonline.com/ArcGIS/rest/services/{type}/MapServer/tile/{x}/{y}/{z}'
    return url


def provider_esri_aerial(quadkey):
    return provider_esri_base(quadkey, type='World_Imagery')


def provider_esri_road(quadkey):
    return provider_esri_base(quadkey, type='World_Street_Map')


def provider_esri_terrain(quadkey):
    return provider_esri_base(quadkey, type='World_Terrain_Base')


def provider_esri_topo(quadkey):
    return provider_esri_base(quadkey, type='World_Topo_Map')


providers = {
    'esri_aerial': provider_esri_aerial,
    'esri_road': provider_esri_road,
    'esri_terrain': provider_esri_terrain,
    'esri_topo': provider_esri_topo,
}
