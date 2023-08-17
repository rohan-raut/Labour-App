from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from api_services.models import Account, Skill, Labour, Booking, Payment, LaboursAllocated, PublicHolidays
from api_services.serializers import AccountSerializer, SkillSerializer, LabourSerializer, BookingSerializer, LaboursAllocatedSerializer, PublicHolidaysSerializer
from rest_framework.authtoken.models import Token
from api_services.filters import SkillFilter, BookingFilter, LabourFilter, LaboursAllocatedFilter
from django.contrib.auth import authenticate
import smtplib
import ssl
import email
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

global sender_email, sender_name, password

sender_email = "hayamedotmy@gmail.com"
sender_name = "Hayame Admin"
password = "dnndjbtorrxpyowx"

def send_notification(receiver_email, subject, body):
    try:
        smtpObj = smtplib.SMTP(host='smtp.gmail.com', port=587)
        smtpObj.starttls()
        smtpObj.login(sender_email, password)
        message = MIMEMultipart()
        message["From"] = sender_name
        message["To"] = receiver_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))
        text = message.as_string()
        smtpObj.sendmail(sender_email, receiver_email, text)
        return True
    except smtplib.SMTPException:
        return False


# Get and Post Views

@api_view(['POST'])
def registration_view(request):
    if request.method == 'POST':
        serializer = AccountSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            account = serializer.save()

            data['response'] = 'Successfully registered a new user.'
            data['email'] = account.email
            data['first_name'] = account.first_name
            data['last_name'] = account.last_name
            data['user_role'] = account.user_role
            data['phone'] = account.phone
            data['is_verified'] = account.is_verified
            token = Token.objects.get(user=account).key
            data['token'] = token

            # send verification email
            receiver_email = account.email
            subject = "Hayame: Email Verification"
            body = "Hello " + account.first_name + ",\nPlease click on the given link to verify your email address.\nLink: http://hayame.my/verify-user?user=" + token
            notification = send_notification(receiver_email, subject, body)

        else:
            data = serializer.errors
        return Response(data)


@api_view(['GET'])
def verify_user_view(request, pk):
    # pk is token of user
    data = {}
    user = Token.objects.get(key=pk).user
    user.is_verified = True
    user.save()
    data['response'] = "Successfully verified the user."
    return Response(data) 


@api_view(['POST',])
@permission_classes((IsAuthenticated,))
def user_info(request):
    if request.method == "POST":
        username = request.data['username']
        password = request.data['password']  

        user = authenticate(request, email=username, password=password)
        data = {}
        if user is not None:
            serializer = AccountSerializer(user)
            return Response(serializer.data)
        else:
            data['response'] = 'Wrong credentials.'
            return Response(data)
    

@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
def skill_list(request):

    if request.method == 'GET':
        snippets = Skill.objects.all()
        filterset = SkillFilter(request.GET, queryset=snippets)
        if filterset.is_valid():
            snippets = filterset.qs
        serializer = SkillSerializer(snippets, many=True)   
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = SkillSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
def labour_list(request):

    if request.method == 'GET':
        snippets = Labour.objects.all()
        filterset = LabourFilter(request.GET, queryset=snippets)
        if filterset.is_valid():
            snippets = filterset.qs
        serializer = LabourSerializer(snippets, many=True)   
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = LabourSerializer(data=request.data)
        if serializer.is_valid():
            labour = serializer.save()

            # populate the labour table based on skills
            skillList = (labour.skills).split(',')
            for skill in skillList:
                skill_obj = Skill.objects.get(skill=skill)
                skill_obj.count = skill_obj.count + 1
                skill_obj.save()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
def booking_view(request):

    if request.method == 'GET':
        snippets = Booking.objects.all()
        filterset = BookingFilter(request.GET, queryset=snippets)
        if filterset.is_valid():
            snippets = filterset.qs
        serializer = BookingSerializer(snippets, many=True)   
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = BookingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def public_holidays_view(request):
    if request.method == 'GET':
        snippets = PublicHolidays.objects.all()
        serializer = PublicHolidaysSerializer(snippets, many=True)   
        return Response(serializer.data)
    

@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
def labour_allocation_view(request):

    if request.method == 'GET':
        snippets = LaboursAllocated.objects.all()
        filterset = LaboursAllocatedFilter(request.GET, queryset=snippets)
        if filterset.is_valid():
            snippets = filterset.qs
        serializer = LaboursAllocatedSerializer(snippets, many=True)   
        return Response(serializer.data)

    elif request.method == 'POST':
        booking_obj = Booking.objects.get(booking_id=request.data['booking_id'])
        booking_obj.status = "Complete"
        booking_obj.save()
        labour_emails = request.data['labour_email']
        labour_emails = labour_emails.split(',')
        for email in labour_emails:
            obj = LaboursAllocated(booking_id=booking_obj, labour_email=email)
            obj.save()

        data = {}
        data['response'] = "Data saved successfully."
        return Response(data)

  
@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def change_password_view(request):
    # fields: email, old_password, password, password2
    email = request.data['email']
    old_password = request.data['old_password']
    password = request.data['password']
    password2 = request.data['password2']

    data = {}

    if(password == password2):
        user = authenticate(request, email=email, password=old_password)
        if user is not None:
            user.set_password(password)
            user.save()
            data['response'] = "New Password Set."
        else:
            data['response'] = "Wrong Password."
    else:
        data['response'] = "Passwords should match."
    
    return Response(data)


@api_view(['POST'])
def forgot_password_view(request):
    # fields: email
    email = request.data['email']
    user = Account.objects.filter(email=email).exists()

    data = {}
    if(user == True):
        user = Account.objects.get(email=email)
        token = Token.objects.get(user=user).key
        data["response"] = "Password reset link sent on your email."
        data["token"] = token
        subject = "Hayame: Password Reset Link."
        body = "Hello " + user.first_name + ",\nThis is your password reset link.\nLink: http://hayame.my/reset-password?user=" + token
        send_notification(receiver_email=email, subject=subject, body=body)
    else:
        data["response"] = "User with the given email does not exists. Please try to Register."
    
    return Response(data)


@api_view(['POST'])
def reset_password_view(request, pk):
    # pk is user's token
    # fields: password, change_password
    password = request.data['password']
    confirm_password = request.data['confirm_password']
    
    data = {}
    if(password != confirm_password):
        data['response'] = "Password does not match."
    else:
        user = Token.objects.get(key=pk).user
        user.set_password(password)
        user.save()
        data['response'] = "Password changed successfully."

    return Response(data)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def send_email_view(request):
    # fields: receiver_email, subject, body

    receiver_email = request.data['receiver_email']
    subject = request.data['subject']
    body = request.data['body']
    data = {}

    if(send_notification(receiver_email, subject, body) == True):
        data['response'] = "Successfully sent email"
    else:
        data['response'] = "Error: unable to send email"
    
    return Response(data)

        

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def report_view(request):
    months = ['Jan', 'Feb', 'Mar', 'April', 'May', 'Jun', 'July', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']
    data = {}
    labours_allocated = LaboursAllocated.objects.all()
    for labour_allocate in labours_allocated:
        booking_obj = labour_allocate.booking_id
        obj = {}
        obj['labour_email'] = labour_allocate.labour_email
        obj['booking_id'] = booking_obj.booking_id
        obj['location'] = booking_obj.location
        obj['contractor_name'] = booking_obj.contractor_name
        obj['contractor_email'] = booking_obj.contractor_email
        obj['labour_skill'] = booking_obj.labour_skill
        obj['labour_count'] = booking_obj.labour_count
        obj['start_time'] = booking_obj.start_time
        obj['end_time'] = booking_obj.end_time
        obj['start_date'] = booking_obj.start_date
        obj['end_date'] = booking_obj.end_date
        obj['amount'] = (booking_obj.amount / booking_obj.labour_count)
        mon = booking_obj.end_date.month - 1
        year = booking_obj.end_date.year
        key = (months[mon] + ' ' + str(year))
        if key not in data:
            data[key] = []
        data[key].append(obj)

    return Response(data)
    
    
    

# Update Views

@api_view(['PUT',])
@permission_classes((IsAuthenticated,))
def update_user_info(request, pk):

    try:
        user = Account.objects.get(email=pk)
    except Account.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "PUT":
        user.first_name = request.data['first_name']
        user.last_name = request.data['last_name']
        user.phone = request.data['phone']
        user.user_role = request.data['user_role']
        user.save()
        
        if user is not None:
            serializer = AccountSerializer(user)
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)
    

@api_view(['PUT'])
@permission_classes((IsAuthenticated,))
def update_skill_list(request, pk):

    try:
        skill = Skill.objects.get(skill=pk)
    except Skill.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT': 
        serializer = SkillSerializer(skill, data=request.data)   
        data = {}
        if serializer.is_valid():
            serializer.save()
            data["success"] = "Update Successful."
            return Response(data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['PUT'])
@permission_classes((IsAuthenticated,))
def update_labour_list(request, pk):

    try:
        labour = Labour.objects.get(email=pk)
    except Labour.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT': 
        serializer = LabourSerializer(labour, data=request.data)   
        data = {}
        if serializer.is_valid():
            skillList = (labour.skills).split(',')
            for skill in skillList:
                skill_obj = Skill.objects.get(skill=skill)
                skill_obj.count = skill_obj.count - 1
                skill_obj.save()

            labour = serializer.save()
            skillList = (labour.skills).split(',')
            for skill in skillList:
                skill_obj = Skill.objects.get(skill=skill)
                skill_obj.count = skill_obj.count + 1
                skill_obj.save()

            data["success"] = "Update Successful."
            return Response(data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


@api_view(['PUT'])
@permission_classes((IsAuthenticated,))
def update_booking_view(request, pk):

    try:
        booking = Booking.objects.get(pk=pk)
    except Booking.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT': 
        serializer = BookingSerializer(booking, data=request.data)   
        data = {}
        if serializer.is_valid():
            serializer.save()
            data["success"] = "Update Successful."
            return Response(data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# Delete Views

@api_view(['DELETE'])
@permission_classes((IsAuthenticated,))
def delete_skill_list(request, pk):

    try:
        skill = Skill.objects.get(skill=pk)
    except Skill.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE': 
        operation = skill.delete()   
        data = {}
        if operation:
            data['success'] = "Delete Successful."
        else:
            data['failure'] = "Delete Failed."
        return Response(data=data)
    

@api_view(['DELETE'])
@permission_classes((IsAuthenticated,))
def delete_labour_list(request, pk):

    try:
        labour = Labour.objects.get(email=pk)
    except Labour.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE': 
        operation = labour.delete()   
        skillList = (labour.skills).split(',')
        for skill in skillList:
            skill_obj = Skill.objects.get(skill=skill)
            skill_obj.count = skill_obj.count - 1
            skill_obj.save()

        data = {}
        if operation:
            data['success'] = "Delete Successful."
        else:
            data['failure'] = "Delete Failed."
        return Response(data=data)
    


@api_view(['DELETE'])
@permission_classes((IsAuthenticated,))
def delete_booking_view(request, pk):

    try:
        booking = Booking.objects.get(pk=pk)
    except Booking.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE': 
        operation = booking.delete()   
        data = {}
        if operation:
            data['success'] = "Delete Successful."
        else:
            data['failure'] = "Delete Failed."
        return Response(data=data)