from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarDealer,CarMake,CarModel
from .restapis import get_dealers_from_cf, get_dealer_by_id_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    context ={}
    return render(request,'djangoapp/about.html', context)


# Create a `contact` view to return a static contact page
def contact(request):
    context ={}
    return render(request,'djangoapp/contact.html', context)


# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'djangoapp/user_login.html', context)
    else:
        return render(request, 'djangoapp/user_login.html', context)


# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        url = "https://83647813.us-south.apigw.appdomain.cloud/dealershipapi/dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        return HttpResponse(dealer_names)

# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...
def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        url = "https://83647813.us-south.apigw.appdomain.cloud/dealershipapi/review/?dealerId="+str(dealer_id)
        # Get dealers from the URL
        reviews = get_dealer_by_id_from_cf(url, dealer_id)
        # Concat all dealer's short name
        review_names = ' '.join([review.name for review in reviews])
        review_sentiments = ' '.join([review.sentiment for review in reviews])
        review_info = "Name:" + review_names +" sentiment:"+ review_sentiments
        final_review = ''.join(review_info)
        return HttpResponse(final_review)
        # Return a list of dealer short name
    
       
# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    if request.method =="POST":

        url = "https://83647813.us-south.apigw.appdomain.cloud/dealershipapi/review/?dealerId="+str(dealer_id)
        response = request.POST.get('json_payload')
        

        print(request.POST.get('body') )
        #if request.user.is_authenticated:
        review = {}
        review["time"] = datetime.utcnow().isoformat()
        review["name"] = "Andres"
        review["dealership"] = 11
        review["review"] = "This is a great car dealer"
        review["purchase"] = False
        json_payload = {}
        json_payload["review"] = review
        response = post_request(request.get(url),request.json_payload,dealerId= dealer_id)
    return HttpResponse(response)
    



