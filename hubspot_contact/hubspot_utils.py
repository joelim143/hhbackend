# hubspot_utils.py
from hubspot import HubSpot
from django.conf import settings

def get_hubspot_client():
    client = HubSpot(api_key=settings.HUBSPOT_API_KEY)
    return client
