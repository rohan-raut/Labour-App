from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from api_services.models import Account, Labour, Booking, Payment
from api_services.serializers import AccountSerializer, LabourSerializer, BookingSerializer
from rest_framework.authtoken.models import Token
from api_services.filters import LabourFilter, BookingFilter
from django.contrib.auth import authenticate


@api_view(['POST',])
def registration_view(request):
    if request.method == 'POST':
        serializer = AccountSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            account = serializer.save()
            
            # populate the labour table based on skills
            labour_obj = Labour.objects.get(skill=account.skills)
            labour_obj.count = labour_obj.count + 1
            labour_obj.save()

            data['response'] = 'Successfully registered a new user.'
            data['email'] = account.email
            data['first_name'] = account.first_name
            data['last_name'] = account.last_name
            data['user_role'] = account.user_role
            data['phone'] = account.phone
            data['skills'] = account.skills
            token = Token.objects.get(user=account).key
            data['token'] = token
        else:
            data = serializer.errors
        return Response(data)
    


@api_view(['POST',])
@permission_classes((IsAuthenticated,))
def user_info(request):
    username = request.POST['username']
    password = request.POST['password']
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
def labour_count_list(request):

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
            serializer.save()
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