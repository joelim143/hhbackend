import requests
import json
from django.conf import settings

#Ref: https://developers.hubspot.com/beta-docs/guides/api/crm/objects/contacts?uuid=1745ee94-820f-4590-9f97-4976d7418cb0

HUBSPOT_BASE_URL = "https://api.hubapi.com"

def get_headers():
    """Returns headers for HubSpot API requests."""
    return {
        "Authorization": f"Bearer {settings.HUBSPOT_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

def get_all_contacts():
    url = "https://api.hubapi.com/crm/v3/objects/contacts"
    headers = {
        "Authorization": f"Bearer {settings.HUBSPOT_ACCESS_TOKEN}"
    }
    params = {
        "properties": "email,firstname,lastname,phone",  # Specify the fields to retrieve
        "limit": 100  # Adjust limit as needed
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()  # Raise an error for bad responses

    data = response.json()
    # Ensure 'id' is included in the returned results
    return data.get("results", [])

def create_contact(email, first_name, last_name, phone, skills, availability):
    """Creates a contact in HubSpot."""
    url = f"{HUBSPOT_BASE_URL}/crm/v3/objects/contacts"
    contact_data = {
        "properties": {
            "email": email,
            "firstname": first_name,
            "lastname": last_name,
            "phone": phone
        }
    }
    
    response = requests.post(url, headers=get_headers(), json=contact_data)
    response.raise_for_status()  # Raises an error for response codes 4xx/5xx
    return response.json()

def get_contact_by_email(email):
    """Retrieves a contact by email from HubSpot."""
    url = f"{HUBSPOT_BASE_URL}/crm/v3/objects/contacts/search"
    print(email)
    data = {
        "filterGroups": [
            {
                "filters": [
                    {
                        "propertyName": "email",
                        "operator": "EQ",
                        "value": email
                    }
                ]
            }
        ],
        "properties": ["email", "firstname", "lastname", "phone"] #include desired fields
    }
    response = requests.post(url, headers=get_headers(), json=data)
    response.raise_for_status()
    return response.json()


def get_contact_by_id(contact_id):
    """Retrieves a contact by email from HubSpot."""
    url = f"{HUBSPOT_BASE_URL}/crm/v3/objects/contacts/{contact_id}"

    response = requests.get(url, headers=get_headers())
    response.raise_for_status()
    return response.json()

def update_contact(contact_id, properties):
    """Updates a contact in HubSpot."""
    url = f"{HUBSPOT_BASE_URL}/crm/v3/objects/contacts/{contact_id}"
    contact_data = {"properties": properties}
    headers=get_headers()
    # print(headers)
    response = requests.patch(url, headers=headers, json=contact_data)
    response.raise_for_status()
    return response.json()

def delete_contact(contact_id):
    """Deletes a contact from HubSpot."""
    url = f"{HUBSPOT_BASE_URL}/crm/v3/objects/contacts/{contact_id}"
    
    response = requests.delete(url, headers=get_headers())
    response.raise_for_status()
    return response.status_code  # Should return 204 for successful deletion