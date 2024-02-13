from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from api_services.models import Account, Skill, Labour, Booking, Payment, LaboursAllocated, PublicHoliday, Notification
from api_services.serializers import AccountSerializer, SkillSerializer, LabourSerializer, BookingSerializer, LaboursAllocatedSerializer, PublicHolidaySerializer, NotificationSerializer
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
import googlemaps
import datetime
from datetime import datetime
from google.oauth2 import id_token
from google.auth.transport import requests
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

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


# Payment Gateway integration
@csrf_exempt
def payment_callback(request):
    tranID = request.POST.get('tranID')
    orderid = request.POST.get('orderid')
    status = request.POST.get('status')
    domain = request.POST.get('domain')
    amount = request.POST.get('amount')
    currency = request.POST.get('currency')
    paydate = request.POST.get('paydate')
    appcode = request.POST.get('appcode')
    skey = request.POST.get('skey')

    booking_obj = Booking.objects.get(booking_id=orderid)
    booking_obj.status = 'Completed'
    booking_obj.payment_status = 'Completed'
    booking_obj.save()

    payment_obj = Payment(booking_id=booking_obj, transaction_id=tranID, payment_date_time=paydate, payment_status=status, merchant_id=domain, country=currency, amount=amount)
    payment_obj.save()


    return HttpResponseRedirect("https://hayame.my/dashboard/contractor-bookings")


# Get and Post Views
    
@api_view(['POST'])
def google_signin_view(request):
    token = request.data['token']
    data = {}
    
    try:
        # Specify the CLIENT_ID of the app that accesses the backend:
        CLIENT_ID = "311936151809-eupfq5t4fcg43bu87kne2jnkssovhh27.apps.googleusercontent.com"
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)

        # ID token is valid. Get the user's Google Account ID from the decoded token.
        
        email = idinfo['email']
        
        user = None
        try:
            user = Account.objects.get(email=email)
        except:
            pass

        if(user == None):
            first_name = idinfo['given_name']
            last_name = idinfo['family_name']
            password = Account.objects.make_random_password(length=100)
            new_user = Account.objects.create_user(email=email, username=email, first_name=first_name, last_name=last_name, phone=None, password=password)
            new_user.is_verified = True
            new_user.save()

        user = Account.objects.get(email=email)
        data['response'] = "Login Successful"
        data['token'] = Token.objects.get(user=user).key
        data['is_logged_in'] = True
        
    except ValueError:
        # Invalid token
        print("Cannot login")     

    return Response(data)
    

@api_view(['POST'])
def login_view(request):
    username = request.data['username']
    password = request.data['password']
    user = authenticate(request, username=username, password=password)
    data = {}
    if user is not None:
        if user.is_verified == False:
            data['response'] = "Please verify your email before login."
            data['is_logged_in'] = False
        else:
            data['response'] = "Login Successful"
            data['token'] = Token.objects.get(user=user).key
            data['is_logged_in'] = True
    else:
        data['response'] = "Wrong Credentials. Please try again."
        data['is_logged_in'] = False
    return Response(data)        


@api_view(['POST'])
def registration_view(request):
    if request.method == 'POST':
        serializer = AccountSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            account = serializer.save()

            data['response'] = 'Successfully Registered. Verify your email before login.'
            data['success'] = True
            data['email'] = account.email
            data['first_name'] = account.first_name
            data['last_name'] = account.last_name
            data['user_role'] = "Contractor"
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
            data['response'] = "Account with this email already exists. Try to Login."
            data['success'] = False
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


@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def user_info(request):
    if request.method == "GET":
        data = {}
        data['user_id'] = request.user.user_id
        data['first_name'] = request.user.first_name
        data['last_name'] = request.user.last_name
        data['email'] = request.user.email
        data['user_role'] = request.user.user_role
        data['phone'] = request.user.phone
        data['is_verified'] = request.user.is_verified
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

    if request.user.user_role != "Admin":
        return Response({'response': 'You cannot access this information'})

    if request.method == 'GET':
        snippets = Labour.objects.all()
        filterset = LabourFilter(request.GET, queryset=snippets)
        if filterset.is_valid():
            snippets = filterset.qs
        serializer = LabourSerializer(snippets, many=True)   
        return Response(serializer.data)

    elif request.method == 'POST':
        first_name = request.data['first_name']
        last_name = request.data['last_name']
        email = request.data['email']
        gender = request.data['gender']
        phone = request.data['phone']
        skills = request.data['skills']
        passport_no = request.data['passport_no']

        skill_list = skills.split(',')
        for skill in skill_list:
            skill_obj = Skill.objects.get(skill=skill)
            skill_obj.count = skill_obj.count + 1
            skill_obj.save()
            labour_obj = Labour(first_name=first_name, last_name=last_name, email=email, gender=gender, phone=phone, passport_no=passport_no, skill=skill_obj)
            labour_obj.save()

        return Response({'response': 'Labour Added Successfully'})


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def booking_preview(request):
    job_location = request.data['job_location']
    labour_skill = request.data['labour_skill']
    labour_count = int(request.data['labour_count'])
    labour_gender = request.data['labour_gender']
    start_date = str(request.data['start_date'])
    end_date = str(request.data['end_date'])
    start_time = request.data['start_time']
    end_time = request.data['end_time']

    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    skill_obj = Skill.objects.get(skill=labour_skill)
    total_days = (end_date - start_date).days + 1

    public_holidays = 0
    public_holidays_obj = PublicHoliday.objects.all()
    for obj in public_holidays_obj:
        if(obj.date >= start_date and obj.date <= end_date):
            public_holidays += 1

    total_days -= public_holidays

    hour = start_time[0] + start_time[1]
    minutes = start_time[3] + start_time[4]
    start_time = datetime(2023, 6, 3, int(hour), int(minutes), 00)
    hour = end_time[0] + end_time[1]
    minutes = end_time[3] + end_time[4]
    end_time = datetime(2023, 6, 3, int(hour), int(minutes), 00)
    time_diff = end_time - start_time
    total_minutes_one_day = time_diff.total_seconds() / 60
    total_hours_one_day = total_minutes_one_day / 60

    cost_per_min_normal_day_less_than_four = skill_obj.cost_per_hour_normal_days_less_than_four / 60
    cost_per_min_normal_day_less_than_eight = skill_obj.cost_per_hour_normal_days_less_than_eight / 60
    cost_per_min_normal_day_less_than_twelve = skill_obj.cost_per_hour_normal_days_less_than_twelve / 60
    cost_per_min_public_holiday_less_than_four = skill_obj.cost_per_hour_public_holiday_less_than_four / 60
    cost_per_min_public_holiday_less_than_eight = skill_obj.cost_per_hour_public_holiday_less_than_eight / 60
    cost_per_min_public_holiday_less_than_twelve = skill_obj.cost_per_hour_public_holiday_less_than_twelve / 60

    gmaps = googlemaps.Client(key='AIzaSyDECJ4Zx4x_Iz5iRSTCvewjuDcaCNmz6l8')
    try:
        my_dist = gmaps.distance_matrix(origins='Persiaran Bukit Raja, Kawasan 17 Bandar Baru Klang, 41150 Klang, Selangor', destinations=job_location, mode="driving", units="metric")['rows'][0]['elements'][0]['distance']['value']
        my_dist = my_dist/1000
    except:
        return Response({
            'success': False,
            'response': 'Invalid Job Location'
        })

    cars = int((labour_count + 3) / 4)
    transportation_cost = my_dist * 1.5 * cars
    transportation_cost = round(transportation_cost)

    total_cost = 0
    data = {}

    if(total_hours_one_day <= 4):
        total_cost = total_days * total_minutes_one_day * cost_per_min_normal_day_less_than_four * labour_count
        total_cost = transportation_cost + total_cost + (public_holidays * total_minutes_one_day * cost_per_min_public_holiday_less_than_four * labour_count)
        data['cost_per_hour_normal_days'] = cost_per_min_normal_day_less_than_four * 60
        data['cost_per_hour_public_holiday'] = cost_per_min_public_holiday_less_than_four * 60
    elif(total_hours_one_day <= 8):
        total_cost = total_days * total_minutes_one_day * cost_per_min_normal_day_less_than_eight * labour_count
        total_cost = transportation_cost + total_cost + (public_holidays * total_minutes_one_day * cost_per_min_public_holiday_less_than_eight * labour_count)
        data['cost_per_hour_normal_days'] = cost_per_min_normal_day_less_than_eight * 60
        data['cost_per_hour_public_holiday'] = cost_per_min_public_holiday_less_than_eight * 60
    else:
        total_cost = total_days * total_minutes_one_day * cost_per_min_normal_day_less_than_twelve * labour_count
        total_cost = transportation_cost + total_cost + (public_holidays * total_minutes_one_day * cost_per_min_public_holiday_less_than_twelve * labour_count)
        data['cost_per_hour_normal_days'] = cost_per_min_normal_day_less_than_twelve * 60
        data['cost_per_hour_public_holiday'] = cost_per_min_public_holiday_less_than_twelve * 60

    # total_cost = (total_days * total_minutes_one_day * cost_per_min_normal_day * labour_count) + (public_holidays * total_minutes_one_day * cost_per_min_public_holiday * labour_count) + transportation_cost

    data['job_location'] = job_location
    data['labour_skill'] = labour_skill
    data['labour_count'] = labour_count
    data['labour_gender'] = labour_gender
    data['start_date'] = start_date
    data['end_date'] = end_date
    data['start_time'] = request.data['start_time']
    data['end_time'] = request.data['end_time']
    data['hours'] = int((total_minutes_one_day * (public_holidays + total_days) * labour_count) / 60)
    data['mins'] = int((total_minutes_one_day * (public_holidays + total_days) * labour_count) % 60)
    data['public_holidays'] = public_holidays
    data['transportation_cost'] = transportation_cost
    data['distance'] = my_dist
    data['cars'] = cars
    data['total_cost'] = total_cost
    data['success'] = True

    contractor_name = request.user.first_name + ' ' + request.user.last_name
    contractor_email = request.user.email
    
    booking_obj = Booking(contractor_name=contractor_name, contractor_email=contractor_email, labour_skill=labour_skill, labour_count=labour_count, labour_gender=labour_gender, start_date=start_date, end_date=end_date, start_time=start_time, end_time=end_time, location=job_location, status='Pending', amount=total_cost, payment_status='Pending')
    booking_obj.save()

    data['booking_id'] = booking_obj.booking_id

    return Response(data)
     

@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
def booking_view(request):

    if request.method == 'GET':
        if request.user.user_role == 'Admin':
            snippets = Booking.objects.all()
        else:
            snippets = Booking.objects.filter(contractor_email=request.user.email)

        if request.user.user_role == "Contractor":
            snippets = Booking.objects.filter(contractor_email=request.user.email)

        filterset = BookingFilter(request.GET, queryset=snippets)
        if filterset.is_valid():
            snippets = filterset.qs
        serializer = BookingSerializer(snippets, many=True)   
        return Response(serializer.data)

    elif request.method == 'POST':
        contractor_name = request.user.first_name + ' ' + request.user.last_name
        contractor_email = request.user.email
        labour_skill = request.data['labour_skill']
        labour_count = request.data['labour_count']
        labour_gender = request.data['labour_gender']
        start_date = request.data['start_date']
        end_date = request.data['end_date']
        start_time = request.data['start_time']
        end_time = request.data['end_time']
        location = request.data['location']
        status = 'Pending'
        amount = request.data['amount']

        booking_obj = Booking(contractor_name=contractor_name, contractor_email=contractor_email, labour_skill=labour_skill, labour_count=labour_count, labour_gender=labour_gender, start_date=start_date, end_date=end_date, start_time=start_time, end_time=end_time, location=location, status=status, amount=amount, payment_status='Pending')
        booking_obj.save()

        # Sending emails to admins
        subject = "Hayame: New Booking"
        body = '''You have got a new booking.
        Booking Details:
        Contractor Name: {contractor_name}
        Skill Required: {labour_skill}
        Labour Count: {labour_count}
        Labour Gender: {labour_gender}
        Start Date: {start_date}
        End Date: {end_date}
        Location: {location}'''.format(contractor_name=contractor_name, labour_skill=labour_skill, labour_count=labour_count, labour_gender=labour_gender, start_date=start_date, end_date=end_date, location=location)
        
        all_admins = Account.objects.filter(user_role='Admin')
        for admin in all_admins:
            send_notification(admin.email, subject, body)

            # Add in Notification Table
            notification_obj = Notification(user_id=admin, booking=booking_obj, is_read=False, date_and_time=datetime.now())
            notification_obj.save()

        # Sending email to contractor
        subject = "Hayame: Booking Confirmed"
        body = '''Hello {contractor_name},
        Your Booking is confirmed. You can keep checking your status at this link:
        https://hayame.my/dashboard/contractor-bookings'''.format(contractor_name=contractor_name)
        send_notification(contractor_email, subject, body)


        data = {}
        data['success'] = True
        data['response'] = 'Booking Done'
        return Response(data)
    

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def public_holidays_view(request):

    if request.user.user_role != "Admin":
        return Response({'response': 'You cannot access this information'})
    
    if request.method == 'GET':
        snippets = PublicHoliday.objects.all()
        serializer = PublicHolidaySerializer(snippets, many=True)   
        return Response(serializer.data)
    

@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
def labour_allocation_view(request):

    if request.user.user_role != "Admin":
        return Response({'response': 'You cannot access this information'})

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
        labour_ids = request.data['labour_ids']
        for id in labour_ids:
            labour_obj = Labour.objects.get(labour_id=id)
            obj = LaboursAllocated(booking_id=booking_obj, labour_id=labour_obj)
            obj.save()
            contractor_obj = Account.objects.get(email=booking_obj.contractor_email)
            subject = "Hayame: New Work Allocated"
            body = "Details of the new work:" + "\nContractor Name: " + str(booking_obj.contractor_name) + "\nContractor Phone: " + str(contractor_obj.phone) + "\nStart Date: " + str(booking_obj.start_date) + "\nEnd Date: " + str(booking_obj.end_date) + "\nStart Time: " + str(booking_obj.start_time) + "\nEnd Time: " + str(booking_obj.end_time) + "\nLocation: " + str(booking_obj.location) 
            # send_notification(labour_obj.email, subject, body)

        data = {}
        data['response'] = "Data saved successfully."
        return Response(data)

  
@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def change_password_view(request):
    # fields: email, old_password, password, password2
    # still not used in application
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
        data['success'] = True
        data["response"] = "Password reset link sent on your email."
        data["token"] = token
        subject = "Hayame: Password Reset Link."
        body = "Hello " + user.first_name + ",\nThis is your password reset link.\nLink: http://hayame.my/reset-password?user=" + token
        send_notification(receiver_email=email, subject=subject, body=body)
    else:
        data['success'] = False
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

    if request.user.user_role != "Admin":
        return Response({'response': 'You are not an Admin'})

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
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    data = {}
    labours_allocated = LaboursAllocated.objects.all()
    for labour_allocate in labours_allocated:
        booking_obj = labour_allocate.booking_id
        labour_obj = labour_allocate.labour_id
        start_time = str(booking_obj.start_time)
        end_time = str(booking_obj.end_time)
        hours = int(end_time[0] + end_time[1]) - int(start_time[0] + start_time[1])
        mins = int(end_time[3] + end_time[4]) - int(start_time[3] + start_time[4])
        if(mins != 0):
            hours = str(hours) + ".5"
        days = (booking_obj.end_date - booking_obj.start_date).days + 1
        obj = {}
        obj['labour_email'] = labour_obj.email
        obj['booking_id'] = booking_obj.booking_id
        obj['location'] = booking_obj.location
        obj['contractor_name'] = booking_obj.contractor_name
        obj['contractor_email'] = booking_obj.contractor_email
        obj['labour_skill'] = booking_obj.labour_skill
        obj['labour_count'] = booking_obj.labour_count
        obj['hours'] = hours * days
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
    
    
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def notification_view(request):
    data = []
    user_id = request.user.user_id
    notifications = Notification.objects.filter(user_id=user_id)

    for notification in notifications:
        naive = notification.date_and_time.replace(tzinfo=None)
        diff = datetime.now() - naive
        diff = diff.total_seconds()
        weeks = int(diff/(60*60*24*7))
        days = int(diff/(60*60*24)) 
        hours = int(diff/(60*60))
        mins = int(diff/60)

        age = ""
        if(weeks != 0):
            age = str(weeks) + "w ago"
        elif(days != 0):
            age = str(days) + "d ago"
        elif(hours != 0):
            age = str(hours) + "h ago"
        else:
            age = str(mins) + "mins ago"

        data.append({
            'contractor_name': notification.booking.contractor_name,
            'contractor_email': notification.booking.contractor_email,
            'labour_skill': notification.booking.labour_skill,
            'booking_id': notification.booking.booking_id,
            'date_and_time': notification.date_and_time,
            'age': age,
            'is_read' : notification.is_read
        })

    data.sort(key=lambda x: x['date_and_time'], reverse=True)

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
        labours = Labour.objects.filter(email=pk)
    except Labour.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT': 
        for labour in labours:
            skill_obj = Skill.objects.get(skill=labour.skill)
            skill_obj.count = skill_obj.count - 1
            labour.delete()

        first_name = request.data['first_name']
        last_name = request.data['last_name']
        email = request.data['email']
        gender = request.data['gender']
        phone = request.data['phone']
        skills = request.data['skills']
        passport_no = request.data['passport_no']

        skill_list = skills.split(',')

        for skill in skill_list:
            skill_obj = Skill.objects.get(skill=skill)
            skill_obj.count = skill_obj.count + 1
            skill_obj.save()
            labour_obj = Labour(first_name=first_name, last_name=last_name, email=email, gender=gender, phone=phone, passport_no=passport_no, skill=skill_obj)
            labour_obj.save()

        return Response({'response': 'Labour Details Updated'})
    


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
    

@api_view(['PUT'])
@permission_classes((IsAuthenticated,))
def update_notification_view(request):

    data = {}
    notificatoins = Notification.objects.filter(user_id=request.user.user_id)
    for notification in notificatoins:
        notification.is_read = True
        notification.save()

    data['success'] = 'Updated Successfully'
    return Response(data)



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