"""
CRM Corven — WhatsApp providers package.
"""

from app.modules.whatsapp.providers.base import WhatsAppProvider
from app.modules.whatsapp.providers.evolution import EvolutionProvider
from app.modules.whatsapp.providers.meta import MetaProvider


def get_provider(provider_name: str) -> WhatsAppProvider:
    """Factory to get the appropriate WhatsApp provider."""
    providers = {
        "evolution": EvolutionProvider,
        "meta": MetaProvider,
    }
    provider_class = providers.get(provider_name)
    if provider_class is None:
        raise ValueError(f"Unknown WhatsApp provider: {provider_name}")
    return provider_class()
