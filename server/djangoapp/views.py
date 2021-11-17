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
import ast
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
    context = {}
    if request.method == "GET":
        url = "https://83647813.us-south.apigw.appdomain.cloud/dealershipapi/dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        context['dealership_list']= dealerships
        # Concat all dealer's short name
        dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        return render(request, 'djangoapp/index.html', context)

# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...
def get_dealer_details(request, dealer_id):
    context = {}
    if request.method == "GET":
        url = "https://83647813.us-south.apigw.appdomain.cloud/dealershipapi/review/?dealerId="+str(dealer_id)
        # Get reviews from the URL
        reviews = get_dealer_by_id_from_cf(url, dealer_id)
        # Concat all the reviewers names and sentiments
        review_names = ' '.join([str(review.car_year) for review in reviews])
        review_sentiments = ' '.join([review.sentiment for review in reviews])
        review_info = "Name:" + review_names +" sentiment:"+ review_sentiments
        print(review_info)
        context ['reviews_list'] =reviews
        context['dealer_id'] = dealer_id
        return render(request, 'djangoapp/dealer_details.html', context)
       
    
       
# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    context = {}
    if request.method =="GET":
        cars = CarModel.objects.filter(dealerId = dealer_id)
        context["cars"] = cars
        context["dealer_id"] = dealer_id
        return render(request,'djangoapp/add_review.html', context)

    if request.method =="POST":

        url = "https://83647813.us-south.apigw.appdomain.cloud/dealershipapi/review/?dealerId="+str(dealer_id)
        #body_unicode = request.body.decode('utf-8')
        print(request.body)
        #url = body['url']
        
       
        #if request.user.is_authenticated:
        review = {}
        review["time"] = datetime.utcnow().isoformat()
        review["name"] = body['name']
        review["dealership"] = 11
        review["review"] = "This is a great car dealer"
        review["id"] = body['id']
        review["purchase"] = body['purchase']
        review["purchase_date"] = body['purchase_date']
        review["car_make"] =body['car_make']
        review["car_model"] = body['car_model']
        review["car_year"] = car.year.strftime("%Y")
        json_payload = {}
        json_payload["review"] = review
        response = post_request(url,json_payload,dealerId= dealer_id)
        return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
        #else:
            #return render(request, 'djangoapp/registration.html', context)
