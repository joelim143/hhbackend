from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseBadRequest, JsonResponse, HttpResponse
from .services.hubspot import create_contact, get_contact_by_email, update_contact, delete_contact, get_contact_by_id
from django.conf import settings
from .models import Contact
from .forms import ContactForm
from .hubspot_utils import get_hubspot_client
from .services.hubspot import get_all_contacts
from django.contrib import messages
from django.urls import reverse
import csv
from hubspot_contact.services.hubspot import (
    get_all_contacts,
    create_contact,
    get_contact_by_email,
    get_contact_by_id,
    update_contact,
    delete_contact,
)
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Contact
from .serializers import ContactSerializer
class ContactList(APIView):
    def get(self, request):
        contacts = Contact.objects.all()
        serializer = ContactSerializer(contacts, many=True)
        return Response(serializer.data)

def list_contacts_view(request):
    try:
        # Fetch all contacts from HubSpot (you'll need to implement get_all_contacts)
        contacts = get_all_contacts()
        print("Contacts retrieved:", contacts)  # Debugging: Log the contacts data
    except Exception as e:
        contacts = []
        error_message = f"Error fetching contacts: {str(e)}"
        return render(request, "hubspot_contact/list_contacts.html", {"contacts": [], "error": error_message})

    return render(request, "hubspot_contact/list_contacts.html", {"contacts": contacts})

def home(request):
    return render(request, 'hubspot_contact/base.html')  # Render base.html with CRUD options

def create_contact_view(request):
    if request.method == 'POST':  # If the request method is POST, the user has submitted the form
        # Retrieve form data sent in the POST request
        email = request.POST.get("email")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        phone = request.POST.get("phone")

        # Validate that all required fields are provided
        if not email or not first_name or not last_name:
            return JsonResponse({"success": False, "error": "Missing required fields"}, status=400)
        
        # Validate email format
        if "@" not in email or "." not in email:
            return JsonResponse({'error': 'Invalid email format'}, status=400)

        # Create the contact in HubSpot
        hubspot_contact = create_contact(email, first_name, last_name, phone)

        # Check if HubSpot returned a valid response with a contact ID
        if hubspot_contact and "id" in hubspot_contact:
            contact_id = hubspot_contact["id"]

            # Save the contact in the MySQL database
            contact = Contact(
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                contact_id=contact_id,  # Save HubSpot contact ID
            )
            contact.save()

            # Pass the contact data into the template for display
            return render(request, "hubspot_contact/contact_created.html", {"contact": hubspot_contact})
        else:
            # If HubSpot didn't return a valid contact, return an error
            return JsonResponse({"success": False, "error": "Failed to create contact in HubSpot"}, status=400)

    # If the request method is not POST, render the create_contact.html template
    return render(request, "hubspot_contact/create_contact.html")

def get_contact_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')  # Get the email from the POST request body

        if not email:
            return render(request, "hubspot_contact/get_contact.html", {"error": "Email is required"})
        
        if not email:
            return JsonResponse({"error": "Email is required"}, status=400)

        # Try to fetch contact using the email
        try:
            contact = get_contact_by_email(email)  # Retrieve contact from HubSpot
             # Print or log the contact response for debugging
            print("HubSpot API Response:", contact)

            # Ensure 'phone' exists in the contact data returned
            # if 'properties' in contact:
            if 'results' in contact:
                contact_data = contact['results'][0]['properties']
                # Pass the contact details in a format that's easy to access in the template
                context = {
                    'contact': {
                        'email': contact_data.get('email'),
                        'first_name': contact_data.get('firstname'),
                        'last_name': contact_data.get('lastname'),
                        'phone': contact_data.get('phone', 'No phone number available')
                    }
                }
                return render(request, "hubspot_contact/get_contact.html", context)
            else:
                return JsonResponse({"error": "Contact not found in HubSpot"}, status=404)
        except Exception as e:
            print("Error occurred:", str(e))
            return JsonResponse({"success": False, "error": str(e)}, status=400)

            # Render the search form if it's not a POST request
            #return render(request, "hubspot_contact/get_contact.html")


def update_contact_view(request, contact_id):
    print("Contact ID received:", contact_id)  # Debug statement    

    if not contact_id:
        return JsonResponse({"error": "Contact ID is required"}, status=400)
    
    if request.method == 'POST':
        try:
            # Retrieve updated values from the form
            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            phone = request.POST.get("phone")
            email = request.POST.get("email")

            print(f"POST Data - First Name: {first_name}, Last Name: {last_name}, Phone: {phone}, Email: {email}")

            # Validate the input fields
            if not first_name or not last_name or not email:
                print("Validation error: Missing required fields.")
                return JsonResponse({"error": "First Name, Last Name, and Email are required"}, status=400)

            # Validate the email format
            if "@" not in email or "." not in email:
                print("Validation error: Invalid email format.")
                return JsonResponse({"error": "Invalid email address"}, status=400)

            # Properties to update in HubSpot
            properties = {
                "firstname": first_name,
                "lastname": last_name,
                "phone": phone,
                "email": email,
            }

            print(f"Properties to update: {properties}")

            # Update the contact in HubSpot
            hubspot_contact = update_contact(contact_id, properties)  # Calls your HubSpot update service
            print("HubSpot contact updated successfully.")

            # Update the contact in the database
            contact = Contact.objects.get(contact_id=contact_id)
            contact.first_name = first_name
            contact.last_name = last_name
            contact.phone = phone
            contact.email = email
            contact.save()
            print("Database contact updated successfully.")

            # Pass the contact data into the template for display
            return render(request, "hubspot_contact/contact_updated.html", {"contact": contact})

            #return JsonResponse({"success": True, "contact": contact.email})
        except Contact.DoesNotExist:
            print("Error: Contact not found in the database.")
            return JsonResponse({"error": "Contact not found in the database"}, status=404)
        except Exception as e:
            print(f"Error: {str(e)}")
            return JsonResponse({"success": False, "error": str(e)}, status=400)

    # Handle GET request (fetching the existing data)
    try:
        contact = Contact.objects.get(contact_id=contact_id)
        context = {
            "contact_id": contact_id,
            "firstname": contact.first_name,
            "lastname": contact.last_name,
            "phone": contact.phone,
            "email": contact.email,
        }
        return render(request, "hubspot_contact/update_contact.html", context)
    except Contact.DoesNotExist:
        return JsonResponse({"error": "Contact not found in the database"}, status=404)


def delete_contact_view(request, contact_id):
    if request.method != "POST":  # Restrict to POST requests for better security
        return JsonResponse(
            {"success": False, "error": "Invalid request method. Use POST."},
            status=405  # Method Not Allowed
        )

    try:
        # Delete from HubSpot
        status_code = delete_contact(contact_id)  # Assuming this function deletes from HubSpot
        if status_code == 204:  # 204 No Content = Successfully deleted
            
            # Proceed to delete from the SQL database
            try:
                contact = Contact.objects.get(contact_id=contact_id)
                contact.delete()  # Delete the contact from the database
                # Redirect back to the contact list with a success message
                return redirect(reverse('hubspot_contact:list_contacts') + '?success=Contact successfully deleted.')
            except Contact.DoesNotExist:
                return redirect(reverse('hubspot_contact:list_contacts') + '?error=Contact does not exist in the SQL database.')
        else:
            # Handle HubSpot deletion failure
            return redirect(reverse('hubspot_contact:list_contacts') + f'?error=Failed to delete contact from HubSpot. Status code: {status_code}.')
    except Exception as e:
        return redirect(reverse('hubspot_contact:list_contacts') + f'?error=An unexpected error occurred: {str(e)}')

def upload_csv_view(request):
    results = []
    error = None

    if request.method == 'POST':
        # Check if the file is in the request
        csv_file = request.FILES.get('csv_file')

        if not csv_file:
            return render(request, "hubspot_contact/upload_csv.html", {"error": "No file uploaded."})

        # Check file type (optional)
        if not csv_file.name.endswith('.csv'):
            return render(request, "hubspot_contact/upload_csv.html", {"error": "Invalid file type. Please upload a CSV file."})

        try:
            # Decode the file to read it as text
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.reader(decoded_file)

            # Skip the header row if necessary
            header = next(reader)

            # Process each row
            for row in reader:
                # Assuming the CSV has columns: contact_id, email, first_name, last_name, phone
                results.append({
                    "contact_id": row[0],  # Assuming contact_id is the first column
                    "email": row[1],  # Assuming email is the second column
                    "first_name": row[2],  # Assuming first name is the third column
                    "last_name": row[3],  # Assuming last name is the fourth column
                    "phone": row[4],  # Assuming phone is the fifth column
                })

        except Exception as e:
            error = f"Error processing file: {str(e)}"
    
    return render(request, "hubspot_contact/upload_csv.html", {"results": results, "error": error})
    
def download_csv_view(request):
    # Query all contacts or adjust based on your needs
    contacts = Contact.objects.all()

    # Create a response object and set the content type to CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="contacts.csv"'

    writer = csv.writer(response)

    # Write the header row
    writer.writerow(['Contact ID', 'First Name', 'Last Name', 'Email', 'Phone'])  # Adjust based on your fields

    # Write each contact's data
    for contact in contacts:
        writer.writerow([contact.contact_id, contact.first_name, contact.last_name, contact.email, contact.phone])  # Adjust to your fields

    return response
