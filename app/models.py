from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser, Permission, BaseUserManager
from django.contrib.auth.hashers import make_password
from django.db.models import UniqueConstraint
import datetime

street_regex = RegexValidator(
    regex=r'^K[KNG] \d{3} St$',
    message="Write a valid Street Name \n i.e: KK 000 St or KG 000 St or KN 000 St"
)

phone_regex = RegexValidator(
    regex=r'^07[8923]\d{7}$',
    message="Phone number must be entered in the format: '07XXXXXXXX'. Up to 10 digits allowed."
)

plate_regex = RegexValidator(
    regex=r'^[A-Z]{3} [0-9]{3} [A-Z]$',
    message="Plate number needd to be formated like AAA 000 A"
)

def set_default_user():
    return User.objects.get(id=1)


# Create your models here.
class User(AbstractUser):
    class Role(models.TextChoices):
        MCOLLECTOR = "MCOLLECTOR", "Money Collector"
        ADMIN = "ADMIN", "Admin"
    
    # base_role = Role.ADMIN

    role = models.CharField(max_length=50, choices=Role.choices)
    phone_number = models.CharField(validators=[phone_regex], max_length=13, unique=True, null=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='users',
        blank=True,
        help_text='The groups this user belongs to.'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='users',
        blank=True,
        help_text='Specific permissions for this user.'
    )

    # def save(self, *args, **kwargs):
    #     if self.pk is None or not self.password.startswith('pbkdf2_'):
    #         self.password = make_password(self.password)
    #     super().save(*args, **kwargs)


class District(models.Model):
    name = models.CharField(max_length=40)

    def __str__(self):
        return self.name

class Sector(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    name = models.CharField(max_length=40)

    def __str__(self):
        return self.name

class Cell(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE)
    name = models.CharField(max_length=40)

    def __str__(self):
        return self.name

class Village(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE)
    cell = models.ForeignKey(Cell, on_delete=models.CASCADE)
    name = models.CharField(max_length=40)

    def __str__(self):
        return self.name



class Location(models.Model):
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True)
    sector = models.ForeignKey(Sector, on_delete=models.SET_NULL, null=True, blank=True)
    cell = models.ForeignKey(Cell, on_delete=models.SET_NULL, null=True, blank=True)
    village = models.ForeignKey(Village, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [UniqueConstraint(fields=['district', 'sector', 'cell', 'village'], name='unique_location_combination')]
        ordering = ["created_at"]
    
    def __str__(self):
        return f"{self.district} - {self.sector} - {self.cell} - {self.village}"

class Residence(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    streetName = models.CharField(validators=[street_regex], max_length=9)
    gateNumber = models.CharField(max_length=10, null=True, blank=True)
    status = models.BooleanField(default = 1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [UniqueConstraint(fields=['location', 'streetName', 'gateNumber'], name='unique_residence_combination')]
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.location} - {self.streetName}"
class Clients(models.Model):
    names = models.CharField(max_length=254)
    phone = models.CharField(validators=[phone_regex], max_length=13, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    residence = models.ForeignKey(Residence, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default = 1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.names} - {self.phone} - {self.residence}"

class Schedule(models.Model):
    week = models.CharField(max_length=8)
    day = models.CharField(max_length=20, choices=[('MONDAY', 'Monday'),('TUESDAY', 'Tuesday'),('WEDNESDAY', 'Wednesday'),('THURSDAY', 'Thursday'),('FRIDAY', 'Friday'),('SATURDAY', 'Saturday'),('SUNDAY', 'Sunday'), ],)
    location = models.ForeignKey(Location, on_delete=models.PROTECT)
    driver = models.CharField(max_length=254)
    plate = models.CharField(validators=[plate_regex], max_length=9)
    status = models.BooleanField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)


    def get_week_dates(self):
        year, week = self.week.split('-W')
        
        first_day_of_week = datetime.datetime.strptime(f'{year}-W{week}-1', "%Y-W%W-%w")
        
        start_date = first_day_of_week
        end_date = start_date + datetime.timedelta(days=6)

        
        return f"{start_date.strftime('%d/%m')} - {end_date.strftime('%d/%m')} {start_date.year}"

    def __str__(self):
        return f"{self.get_week_dates()} - {self.location} - {self.driver} - {self.plate}"

class Collection(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.PROTECT)
    client = models.ForeignKey(Clients, on_delete=models.PROTECT)
    approved_by = models.ForeignKey(User, on_delete=models.SET(set_default_user))
    status = models.BooleanField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [UniqueConstraint(fields=['schedule', 'client'], name='unique_collection_combination')]

    def __str__(self):
        return f"{self.schedule} - {self.client} - {self.status}"

class Overflow(models.Model):
    location = models.ForeignKey(Location, on_delete=models.PROTECT)
    date = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='overflow/', null=True, blank=True)
    status = models.BooleanField(default=0)
    client = models.ForeignKey(Clients, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.location} - {self.date} - {self.status}"

from django.db import models

class Feedback(models.Model):
    email = models.EmailField(max_length=100)
    message = models.TextField()
    client = models.ForeignKey(Clients, on_delete=models.CASCADE, null=True, blank=True)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # Rating between 1 and 5
    post_status = models.BooleanField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.email} - Rating: {self.rating}"

