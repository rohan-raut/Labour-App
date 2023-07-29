from rest_framework import serializers
from api_services.models import Account, Skill, Labour, Booking, Payment, LaboursAllocated, PublicHolidays


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['skill', 'count', 'cost_per_hour_normal_days', 'cost_per_hour_public_holiday']


class LabourSerializer(serializers.ModelSerializer):
    class Meta:
        model = Labour
        fields = ['first_name', 'last_name', 'email', 'gender', 'phone', 'skills', 'passport_no']


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['booking_id', 'contractor_name', 'contractor_email', 'labour_skill', 'labour_count', 'labour_gender', 'start_date', 'end_date', 'start_time', 'end_time', 'location', 'status', 'amount']
        read_only_fields = ['booking_id']


class LaboursAllocatedSerializer(serializers.ModelSerializer):
    class Meta:
        model = LaboursAllocated
        fields = ['allocation_id', 'booking_id', 'labour_email']
        read_only_fields = ['allocation_id']


class PublicHolidaysSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicHolidays
        fields = ['event', 'date']
        

class AccountSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = Account
        fields = ['email', 'username', 'first_name', 'last_name', 'phone', 'user_role', 'is_verified', 'password', 'password2']
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