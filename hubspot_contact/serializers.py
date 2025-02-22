from rest_framework import serializers
from .models import Contact

class ContactSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)  # Only write, not read

    class Meta:
        model = Contact
        # fields = '__all__'  # Use all fields from the model
        fields = ["contact_id","first_name", "last_name", "email", "phone", 
                  "skills", "availability", "password", "approval_status"]

    def create(self, validated_data):
        # password = validated_data.pop('password', None)
        contact = super().create(validated_data)

        # Hash the password before saving (if using plain text passwords, remove the hashing)
        # if password:
        #     contact.set_password(password)  # If using Django model's set_password method for hashing
        contact.save()
        return contact
