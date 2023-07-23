from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from api_services.models import Account, Skill, Labour, Booking, Payment
from api_services.serializers import AccountSerializer, SkillSerializer, LabourSerializer, BookingSerializer
from rest_framework.authtoken.models import Token
from api_services.filters import SkillFilter, BookingFilter, LabourFilter
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
            body = "Hello " + account.first_name + ",\nPlease click on the given link to verify your email address.\nLink: http://hayame.my/verify-user/" + token
            notification = send_notification(receiver_email, subject, body)

        else:
            data = serializer.errors
        return Response(data)


@api_view(['GET'])
def verify_user_view(request, pk):
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