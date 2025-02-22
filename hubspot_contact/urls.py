from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import (
    HubSpotContactListView,
    MySQLContactListView,  
    ContactDetailView, 
    ContactUpdateView, 
    ContactDeleteView,
    CSVUploadView, 
    CSVDownloadView, 
    ContactdbViewSet, 
    ContacthubspotViewSet,
    ContactEmailView, 
    ContactCreateView, 
    verify_password,
    update_approval_status
)

# DRF Router for ViewSets
router = DefaultRouter()
router.register(r'contacts-db', ContactdbViewSet, basename='contactdb')

#app_name = "hubspot_contact"

urlpatterns = [
    # Include DRF ViewSet URLs (this handles routes like /contacts/)
    path("", include(router.urls)),

    # HubSpot Contact API Endpoints
    path('contacts/list/', HubSpotContactListView.as_view(), name='hubspot-contact-list'),

    path('hubspot_contacts/', MySQLContactListView.as_view(), name='mysql-contact-list'),

    # Contact Create View
    path('contacts/create/', ContactCreateView.as_view(), name='create-contact'),

    # Contact Detail View (using contact_id)
    path('contacts/<str:contact_id>/', ContactDetailView.as_view(), name='contact-detail'),

    # Contact Update View (using contact_id)
    path('contacts/<str:contact_id>/update/', ContactUpdateView.as_view(), name='update-contact'),

    # Contact Delete View (using contact_id)
    path('hubspot_contacts/<str:contact_id>/delete/', ContactDeleteView.as_view(), name='delete-contact'),

    # Contact Email View (using email)
    path('contacts/email/<str:email>/', ContactEmailView.as_view(), name='contact-email'),

    # Verify Password Endpoint (using email)
    path('contacts/<str:email>/verify_password/', verify_password, name='verify_password'),

    # Update Approval Status (using contact_id)
    path('hubspot_contacts/<str:contact_id>/approval_status/', update_approval_status, name='update-approval-status'),

    # CSV upload/download
    path('contacts/csv/upload/', CSVUploadView.as_view(), name='csv-upload'),
    path('contacts/csv/download/', CSVDownloadView.as_view(), name='csv-download'),

    # Optionally, this can be a route for getting all contacts from HubSpot.
    path('hubspot_contacts/', HubSpotContactListView.as_view(), name='hubspot-contact-list'),
]
