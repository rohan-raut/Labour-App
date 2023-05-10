from rest_framework import serializers
from api_services.models import Account, Skill, Labour, Booking, Payment


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['skill', 'count', 'cost_per_hour']


class LabourSerializer(serializers.ModelSerializer):
    class Meta:
        model = Labour
        fields = ['first_name', 'last_name', 'email', 'phone', 'skills', 'passport_no']


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['booking_id', 'contractor_name', 'contractor_email', 'labour_skill', 'labour_count', 'start_date', 'end_date', 'start_time', 'end_time', 'location', 'status']
        read_only_fields = ['booking_id']



class AccountSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = Account
        fields = ['email', 'username', 'first_name', 'last_name', 'phone', 'user_role', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def save(self):
        account = Account(
            email = self.validated_data['email'],
            username = self.validated_data['username'],
            first_name = self.validated_data['first_name'],
            last_name = self.validated_data['last_name'],
            user_role = self.validated_data['user_role'],
            phone = self.validated_data['phone'],
        )

        password = self.validated_data['password']
        password2 = self.validated_data['password2']

        if password != password2:
            raise serializers.ValidationError({'password': 'Passwords must match.'})
        account.set_password(password)
        account.save()
        return account



class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['email', 'username', 'first_name', 'last_name', 'phone', 'user_role', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }