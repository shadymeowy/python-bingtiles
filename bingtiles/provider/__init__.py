from .bing import *
from .esri import *

from .bing import providers as bing_providers
from .esri import providers as esri_providers

providers = {
    **bing_providers,
    **esri_providers,
}

default_provider = 'bing_hybrid'