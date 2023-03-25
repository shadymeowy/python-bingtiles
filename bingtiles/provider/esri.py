from ..utils import quad2tile


def provider_esri_base(pos, type='World_Imagery'):
    x, y, z = pos
    url = f'https://server.arcgisonline.com/ArcGIS/rest/services/{type}/MapServer/tile/{x}/{y}/{z}'
    return url


def provider_esri_aerial(pos):
    return provider_esri_base(pos, type='World_Imagery')


def provider_esri_road(pos):
    return provider_esri_base(pos, type='World_Street_Map')


def provider_esri_terrain(pos):
    return provider_esri_base(pos, type='World_Terrain_Base')


def provider_esri_topo(pos):
    return provider_esri_base(pos, type='World_Topo_Map')


providers = {
    'esri_aerial': provider_esri_aerial,
    'esri_road': provider_esri_road,
    'esri_terrain': provider_esri_terrain,
    'esri_topo': provider_esri_topo,
}
