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
    print(request.body)
    if request.method == "GET":
        url = "https://83647813.us-south.apigw.appdomain.cloud/dealershipapi/review/?dealerId="+str(dealer_id)
        url_ds = "https://83647813.us-south.apigw.appdomain.cloud/dealershipapi/dealership"
        # Get reviews from the URL
        reviews = get_dealer_by_id_from_cf(url, dealer_id)
        #Get dealerhip list and filter the current one out
        dealerships = get_dealers_from_cf(url_ds)
        for dealer in dealerships:
            if dealer.id == dealer_id:
                dealer_info = dealer.full_name
                
        
        # Concat all the reviewers names and sentiments
        review_names = ' '.join([str(review.car_year) for review in reviews])
        review_sentiments = ' '.join([review.sentiment for review in reviews])
        review_info = "Name:" + review_names +" sentiment:"+ review_sentiments
        
        context ['reviews_list'] =reviews
        context ['dealer'] = dealer_info
        context['dealer_id'] = dealer_id
        return render(request, 'djangoapp/dealer_details.html', context)
       
    
       
# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    context = {}
    if request.method =="GET":
        url_ds = "https://83647813.us-south.apigw.appdomain.cloud/dealershipapi/dealership"
        cars = CarModel.objects.filter(dealerId = dealer_id)
        dealerships = get_dealers_from_cf(url_ds)
        for dealer in dealerships:
            if dealer.id == dealer_id:
                dealer_name = dealer.full_name
        context["cars"] = cars
        context["dealer"] = dealer_name
        context["dealer_id"] = dealer_id
        return render(request,'djangoapp/add_review.html', context)

    if request.method =="POST":

        url = "https://83647813.us-south.apigw.appdomain.cloud/dealershipapi/review/?dealerId="+str(dealer_id)
        #body_unicode = request.body.decode('utf-8')
        cars = CarModel.objects.filter(dealerId = dealer_id)
        for car in cars:
            if car.id == int(request.POST['car']):
                review_car = car
        
        print (review_car.year.strftime("%Y"))
        #url = body['url']
        
        if 'purchasecheck' in request.POST:
            was_purchased = True
        else:
            was_purchased = False
        print (was_purchased)
        #if request.user.is_authenticated:
        review = {}
        review["time"] = datetime.utcnow().isoformat()
        review["name"] = request.POST['name']
        review["dealership"] = 13 
        review["review"] = request.POST['content']
        review["id"] = dealer_id
        review["purchase"] = was_purchased
        review["purchase_date"] = request.POST['purchasedate']
        review["car_make"] =review_car.car.name
        review["car_model"] = review_car.name
        review["car_year"] = review_car.year.strftime("%Y")
        json_payload = {}
        json_payload["review"] = review
        response = post_request(url,json_payload,dealerId= dealer_id)
        return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
        #else:
            #return render(request, 'djangoapp/registration.html', context)
