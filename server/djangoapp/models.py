from django.db import models
from django.utils.timezone import now


# Create your models here.

# <HINT> Create a Car Make model `class CarMake(models.Model)`:
class CarMake(models.Model):
# - Name
    name = models.TextField()
# - Description
    description = models.TextField()

# - Any other fields you would like to include in car make model
# - __str__ method to print a car make object
def __str__(self):
        return 'This car is a {self.name} with the following description {self.description}'.format(self=self)


# <HINT> Create a Car Model model `class CarModel(models.Model):`:
class CarModel(models.Model):
# - Many-To-One relationship to Car Make model (One Car Make has many Car Models, using ForeignKey field)
    car= models.ForeignKey(CarMake, on_delete=models.CASCADE)
# - Name
    name = models.TextField()
# - Dealer id, used to refer a dealer created in cloudant database
    dealerId= models.IntegerField()
# - Type (CharField with a choices argument to provide limited choices such as Sedan, SUV, WAGON, etc.)
    SEDAN = 'sedan'
    SUV = 'suv'
    WAGON = 'wagon'
    CONVERTIBLE = 'convertible'
    CAR_CHOICES = [
        (SEDAN, 'sedan'),
        (SUV, 'suv'),
        (WAGON, 'Wagon'),
        (CONVERTIBLE, 'Convertible')
    ]
    type = models.CharField(max_length=12, choices=CAR_CHOICES, default=SEDAN)
# - Year (DateField)
    year = models.DateField(default=now)
# - Any other fields you would like to include in car model
# - __str__ method to print a car make object
    def __str__(self):
        return 'Name:{self.name}, dealerId:{self.dealerId},Type:{self.type}, Year:{self.year}'.format(self=self)

# <HINT> Create a plain Python class `CarDealer` to hold dealer data


# <HINT> Create a plain Python class `DealerReview` to hold review data
