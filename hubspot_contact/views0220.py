import csv
import json
from .models import Contact
from .serializers import ContactSerializer
from .services.hubspot import create_contact
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework import generics
from rest_framework.decorators import api_view
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.contrib.auth.hashers import check_password
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .services.hubspot import (
    get_all_contacts,
    create_contact,
    get_contact_by_email,
    get_contact_by_id,
    update_contact,
    delete_contact,
)
# @csrf_exempt
@api_view(['PATCH'])
def update_approval_status(request, contact_id):
    try:
        contact = Contact.objects.get(contact_id=contact_id)  # Use contact_id here, not pk
    except Contact.DoesNotExist:
        return Response({"error": "Contact not found"}, status=status.HTTP_404_NOT_FOUND)

    contact.approval_status = request.data.get('approval_status', contact.approval_status)
    contact.save()
    serializer = ContactSerializer(contact)
    return Response(serializer.data, status=status.HTTP_200_OK)
@csrf_exempt  # Temporarily disable CSRF for testing (remove later if using authentication)
def verify_password(request, email):
    try:
        print(f"Received request body: {request.body}")  # Debugging
        # print(request.content_type)

        # Handle JSON and form-data requests
        if request.content_type == "application/json":
            data = json.loads(request.body)
            provided_password = data.get("password")
        else:
            provided_password = request.POST.get("password")
        if not provided_password:
            return JsonResponse({"error": "Password required"}, status=400)
        
        try:
            contact = Contact.objects.get(email=email)
        except Contact.DoesNotExist:
            return JsonResponse({"error": "Contact not found"}, status=404)

        # Check password (⚠️ Plain text check; use hashing for real authentication)
        if not check_password(provided_password, contact.password):
            return JsonResponse({"error": "Invalid password"}, status=403)

        return JsonResponse({"name": contact.first_name, "approval_status": contact.approval_status}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    
class HubSpotContactListView(APIView):
    def get(self, request):
        try:
            contacts = get_all_contacts()
            return Response(contacts, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ContactdbViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

class ContacthubspotViewSet(APIView):
    def get(self, request):
        try:
            contacts = get_all_contacts()
            return Response(contacts, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ContactCreateView(APIView): # APIView - base class fro Django REST framework views
    # queryset = Contact.objects.all() # Defines all Contact objects, APIView does not use this
    # serializer_class = ContactSerializer # serializing/deserializing data
    def post(self, request): # receives POST data from the client (request.data)
        serializer = ContactSerializer(data=request.data) # serialize the incoming data
        if serializer.is_valid(): # Check if the input data matches the ContactSerializer rules
            contact_data = serializer.validated_data
            # Extract password separately
            password = contact_data.pop("password", None)  # Remove password before sending to HubSpot
            hubspot_contact = create_contact(**contact_data)   # Calls an external Hubspot API to create a contact
            
            if hubspot_contact and "id" in hubspot_contact: # Check if Hubspot contact is created successfully ("id" exists)
               contact = serializer.save(contact_id=hubspot_contact["id"]) # Save the contact in the local database with HubSpot ID
               # Save password securely in the local database
                # contact.password = password
               contact.set_password(password)  # Hash the password
               contact.save() # SAve the record with password
                
               return Response(serializer.data, status=status.HTTP_201_CREATED) #  contact created         
            return Response({"error": "Failed to create contact in HubSpot"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ContactDetailView(APIView):
    def get(self, request, contact_id):
        try:
            contact = get_object_or_404(Contact, contact_id=contact_id)
            serializer = ContactSerializer(contact)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            try:
                contact = get_contact_by_id(contact_id)
                return Response(contact, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": f"Error retrieving contact: {str(e)}"}, status=status.HTTP_404_NOT_FOUND)

class ContactEmailView(APIView):
    def get(self, request, email):
        
        print(f"Fetching contact for email: {email}")  # Debugging log
        try:
            contact = get_object_or_404(Contact, email=email)
            serializer = ContactSerializer(contact)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            try:
                contact = get_contact_by_email(email)
                return Response(contact, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": f"Error retrieving contact: {str(e)}"}, status=status.HTTP_404_NOT_FOUND)

class ContactUpdateView(APIView):
    def patch(self, request, contact_id):
        # print(request)
        contact = get_object_or_404(Contact, contact_id=contact_id)
        id = request.data.get('id')

        # if not provided_password or provided_password != contact.password:
        if not id or id != contact_id:
            return Response({"error": "Invalid password"}, status=status.HTTP_403_FORBIDDEN)

        serializer = ContactSerializer(contact, data=request.data, partial=True)
        if serializer.is_valid():
            properties = serializer.validated_data
            key_mapping = {
                'first_name': 'firstname',
                'last_name': 'lastname',                
            }
            new_properties = {
                key_mapping.get(k, k): v for k, v in properties.items()
            }
            new_properties.pop('skills') #skills is not a property in hubspot
            update_contact(contact_id, new_properties)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ContactDeleteView(APIView):
    def delete(self, request, contact_id):
        contact = get_object_or_404(Contact, contact_id=contact_id)
        status_code = delete_contact(contact_id)
        if status_code == 204:
            contact.delete()
            return Response({"message": "Contact deleted"}, status=status.HTTP_204_NO_CONTENT)
        return Response({"error": "Failed to delete contact from HubSpot"}, status=status.HTTP_400_BAD_REQUEST)

class CSVUploadView(APIView):
    def post(self, request):
        csv_file = request.FILES.get("csv_file")
        if not csv_file or not csv_file.name.endswith(".csv"):
            return Response({"error": "Invalid file format"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            decoded_file = csv_file.read().decode("utf-8").splitlines()
            reader = csv.reader(decoded_file)
            next(reader)
            contacts = []
            for row in reader:
                contacts.append({
                    "contact_id": row[0],
                    "email": row[1],
                    "first_name": row[2],
                    "last_name": row[3],
                    "phone": row[4],
                    "skills": row[5],
                    "availability": row[6],
                })
            return Response({"contacts": contacts}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CSVDownloadView(APIView):
    def get(self, request):
        contacts = Contact.objects.all()
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="contacts.csv"'
        writer = csv.writer(response)
        writer.writerow(["Contact ID", "First Name", "Last Name", "Email", "Phone", "Skills", "Availability"])
        for contact in contacts:
            writer.writerow([contact.contact_id, contact.first_name, contact.last_name, contact.email, contact.phone, contact.skills, contact.availability])
        return response
