from django.shortcuts import render, redirect
from .forms import LoginForm, LocationsForm, ResidenceForm, ClientForm, ScheduleForm, CollectionForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from functools import wraps 
from django.db import IntegrityError
from .models import User, Location, Residence, Client, Schedule, Collection, Feedback, Overflow, District, Sector, Cell, Village
# Create your views here.

def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            return redirect('403') 
        return _wrapped_view
    return decorator


def home(request):
    return render(request, 'index.html')


def forbidenpage(request):
    return render(request, '401.html')


def loginuser(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            login_input = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')


            if '@' in login_input:
                try:
                    # Get the user by email
                    user = User.objects.get(email=login_input)
                    username = user.username
                except User.DoesNotExist:
                    messages.error(request, "Invalid email or password.")
                    return render(request, 'login.html', {'form': form})
            else:
                username = login_input  # Treat as username

            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                if user.role == "ADMIN":
                    return redirect('admin-home')
                elif user.role == "Money Collector":
                    return redirect('money-collector-home')
                else:
                    return redirect('403')
            else:
                messages.error(request, "Invalid email or password.")
        else:
            messages.er# This logs out the userror(request, "Invalid form submission.")
    else:
        form = LoginForm()  
    return render(request, 'login.html', {'form': form})

@login_required
def logoutuser(request):
    logout(request)  # This logs out the user
    return redirect('home')

@role_required(['ADMIN'])
def adminhome(request):
    return render(request, 'adminn/index.html')




@role_required(['ADMIN'])
def locations(request):
    locations = Location.objects.all()
    if request.method == 'POST':
        form = LocationsForm(request.POST)
        if form.is_valid():
            try:
                district = form.cleaned_data['district']
                sector = form.cleaned_data['sector']
                cell = form.cleaned_data['cell']
                village = form.cleaned_data['village']

                district_obj, created = District.objects.get_or_create(name=district)
                sector_obj, created = Sector.objects.get_or_create(name=sector)
                cell_obj, created = Cell.objects.get_or_create(name=cell)
                village_obj, created = Village.objects.get_or_create(name=village)

                location = Location.objects.create(
                    district=district_obj,
                    sector=sector_obj,
                    cell=cell_obj,
                    village=village_obj
                )
                messages.success(request, f"New Location {location} Added")
                form = LocationsForm()
            except IntegrityError:
                # Catch the unique constraint violation and show a friendly error
                messages.error(request, "A location with this district, sector, cell, and village already exists. Please try a different combination.")
        else:
            messages.error(request, f"{form.errors}")
    else:
        form = LocationsForm()
    
    context = {'form': form, 'locations': locations}
    return render(request, 'adminn/locations.html', context)

def load_sectors(request):
    district_id = request.GET.get('district')
    sectors = Sector.objects.filter(district_id = district_id)
    return render(request, "adminn/sectors_options.html", {'sectors': sectors})

def load_cells(request):
    sector_id = request.GET.get('sector')
    cells = Cell.objects.filter(sector_id = sector_id)
    return render(request, "adminn/cells_options.html", {'cells': cells})
    

def load_villages(request):
    cell_id = request.GET.get('cell')
    villages = Village.objects.filter(cell_id = cell_id)
    return render(request, "adminn/villages_options.html", {'villages': villages})

@role_required(['ADMIN'])
def residence(request):
    residences = Residence.objects.all()
    if request.method == 'POST':
        form = ResidenceForm(request.POST)
        if form.is_valid():
            residence = form.save()
            messages.success(request, f"New Residence {residence} Added")
            form = ResidenceForm()
        else:
            messages.error(request, f"{form.errors}")
    else:
        form = ResidenceForm()

    context = {'form': form, 'residences': residences}
    return render(request, 'adminn/residence.html', context)


@login_required
def changeResidence(request, pk):
    residence = Residence.objects.get(id=pk)
    residences = Residence.objects.all()

    if residence.status:
        residence.status = False
        messages.success(request, f"({residence}Residence Active Status Removed successfuly")
    else:
        residence.status = True
        messages.success(request, f"({residence}Residence Active Status Activeted successfuly")

    residence.save()
    return redirect("residence")


@role_required(['ADMIN'])
def editResidence(request, pk):
    residences = Residence.objects.all()
    resident = Residence.objects.get(id=pk)
    if request.method == 'POST':
        form = ResidenceForm(request.POST, instance=resident)
        if form.is_valid():
            residence = form.save()
            messages.success(request, f"New Residence Updated")
            return redirect('residence')
        else:
            messages.error(request, f"{form.errors}")
    else:
        form = ResidenceForm(instance=resident)

    context = {'form': form, 'residences': residences}
    return render(request, 'adminn/edit-residence.html', context)


@role_required(['ADMIN'])
def clients(request):
    clients = Client.objects.all()
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save()
            messages.success(request, f"New Client {client} Added")
            form = ClientForm()
        else:
            messages.error(request, f"{form.errors}")
    else:
        form = ClientForm()

    context = {'form': form, 'clients': clients}
    return render(request, 'adminn/clients.html', context)


@role_required(['ADMIN'])
def schedule(request):
    if request.method == 'POST':
        form = ScheduleForm(request.POST)
    else:
        form = ScheduleForm()

    context = {'form': form}
    return render(request, 'adminn/schedule.html', context)


@role_required(['ADMIN'])
def collection(request):
    if request.method == 'POST':
        form = CollectionForm(request.POST)
    else:
        form = CollectionForm()

    context = {'form': form}
    return render(request, 'adminn/collection.html', context)

@role_required(['ADMIN'])
def overflow(request):
    return render(request, 'adminn/overflow.html')

@role_required(['ADMIN'])
def feedbacks(request):
    feedbacks = Feedback.objects.all()
    context = {'feedbacks': feedbacks}
    return render(request, 'adminn/feedbacks.html', context)


@role_required(['ADMIN'])
def unpostfeedbacks(request, pk):
    feedbacks = Feedback.objects.all()
    context = {'feedbacks': feedbacks}
    feedback = Feedback.objects.get(id=pk)
    feedback.post_status = False
    feedback.save()
    messages.success(request, f"Feedback Posted Successfuly")
    return render(request, 'adminn/feedbacks.html', context)


@role_required(['ADMIN'])
def postfeedbacks(request, pk):
    feedback = Feedback.objects.get(id=pk)
    feedback.post_status = True
    feedback.save()
    messages.success(request, f"Feedback UnPosted Successfuly")
    feedbacks = Feedback.objects.all()
    context = {'feedbacks': feedbacks}
    return render(request, 'adminn/feedbacks.html', context)


@role_required(['Money Collector'])
def mcollectorhome(request):
    return render(request, 'mcollector/index.html')


def empty(request):
    return render(request, 'adminn/empty.html')






