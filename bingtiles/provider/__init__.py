from .bing import *
from .esri import *
from .google import *

from .bing import providers as bing_providers
from .esri import providers as esri_providers
from .google import providers as google_providers

providers = {
    **bing_providers,
    **esri_providers,
    **google_providers,
}

default_provider = 'bing_hybrid'
