from django.shortcuts import render, redirect
from .forms import LoginForm, LocationsForm, ResidenceForm, ClientForm, ScheduleForm, CollectionForm, EditResidenceForm, CreateAccountForm, EditAccountForm, ClientSelfForm, FeedbackForm, OverflowForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from functools import wraps 
import datetime
from datetime import datetime, timedelta
from django.contrib.auth.hashers import make_password
from twilio.rest import Client
from django.db import IntegrityError
from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import User, Location, Residence, Clients, Schedule, Collection, Feedback, Overflow, District, Sector, Cell, Village
from django.db.models.functions import Cast
from django.db.models import DateField
from collections import defaultdict

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
    feedbacks = Feedback.objects.filter(post_status = True)
    context = {'feedbacks': feedbacks, 'range': range(5)}
    return render(request, 'index.html', context)

def sendFeedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            email = form.cleaned_data['email']
            client = Clients.objects.filter(email=email).first()
            if client:
                feedback.client = client
                feedback.save()
                messages.success(request, "Thank you for your feedback")
            else:
                messages.error(request, "Invalid email. Consider registering for our services for free.\nYou can not send as a feedback without an experience of our sevices")
        else:
            messages.error(request, f"{form.errors}")
    else:
        form = FeedbackForm()

    context = {'form': form}
    return render(request, "feedback.html", context)


def reportOverflow(request):
    if request.method == 'POST':
        form = OverflowForm(request.POST, request.FILES)
        if form.is_valid():
            overflow = form.save(commit=False)
            email = form.cleaned_data['email']
            client = Clients.objects.filter(email=email).first()
            if client:
                overflow.client = client
                overflow.location = client.residence.location
                overflow.save()
                messages.success(request, "Thank you for your For your report\nWe get in contact soon")
            else:
                messages.error(request, "Invalid email. Consider registering for our services for free.\nYou can not send as a clain without an experience of our sevices")
        else:
            messages.error(request, f"{form.errors}")
    else:
        form = OverflowForm()

    context = {'form': form}
    return render(request, "overflow.html", context)


def selfRegistration(request):
    if request.method == 'POST':
        form = ClientSelfForm(request.POST)
        if form.is_valid():
            client = form.save()
            send_mail(
                "Welcome to Garbage Collection",
                f"Your Email was registered at the garbage collection website.\nWelcome to our community as we keep our homes clean.\nThank you!",
                settings.EMAIL_HOST_USER,
                [client.email]
            )
            messages.success(request, "You have been registered successfully. futher contact will be made")
        else:
            messages.error(request, f"{form.errors}")
    else:
        form = ClientSelfForm()
    
    context = {'form': form}
    return render(request, "self-reg.html", context)

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
                elif user.role == "MCOLLECTOR":
                    return redirect('admin-home')
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

@role_required(['ADMIN', 'MCOLLECTOR'])
def adminhome(request):
    clients1 = Clients.objects.all()
    formatted_dates = []
    client_count_per_month = defaultdict(int)
    for client in clients1:
        formatted_date = client.created_at.strftime('%B-%Y')
        formatted_dates.append(formatted_date)
        client_count_per_month[formatted_date] += 1

    client_count_list = list(client_count_per_month.values())


    collections = Collection.objects.all().order_by('-created_at')[:5]
    upcoming_schedules = get_upcoming_schedules()
    residences = Residence.objects.all().count()
    clients = Clients.objects.all().count()
    users = User.objects.filter(role="MCOLLECTOR").count()
    locations = Location.objects.all().count()
    schedules = Schedule.objects.all().count()
    collection = Collection.objects.all().count()

    glist = ["Clients", "Locations", "Residences", "Schedules", "Collections"]
    numbers = [clients, locations, residences, schedules, collection]

    context = {'shcedules': upcoming_schedules, 'collections': collections, 'locations': locations, 'residences': residences, 'clients': clients, 'users': users, 'glist': glist, 'numbers': numbers, 'formatted_dates': formatted_dates, 'client_count_list': client_count_list}
    return render(request, 'adminn/index.html', context)




@role_required(['ADMIN', 'MCOLLECTOR'])
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

@role_required(['ADMIN', 'MCOLLECTOR'])
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


@role_required(['ADMIN', 'MCOLLECTOR'])
def changeResidence(request, pk):
    residence = Residence.objects.get(id=pk)
    residences = Residence.objects.all()

    if residence.status:
        residence.status = False
        messages.success(request, f"{residence}Residence Active Status Removed successfuly")
    else:
        residence.status = True
        messages.success(request, f"{residence}Residence Active Status Activeted successfuly")

    residence.save()
    return redirect("residence")


@role_required(['ADMIN', 'MCOLLECTOR'])
def editResidence(request, pk):
    residences = Residence.objects.all()
    resident = Residence.objects.get(id=pk)
    if request.method == 'POST':
        form = EditResidenceForm(request.POST, instance=resident)
        if form.is_valid():
            form.instance.location = resident.location
            residence = form.save()
            messages.success(request, f"{residence} Residence Updated")
            return redirect('residence')
        else:
            messages.error(request, f"{form.errors}")
    else:
        form = EditResidenceForm(instance=resident)

    context = {'form': form, 'residences': residences}
    return render(request, 'adminn/edit-residence.html', context)


@role_required(['ADMIN', 'MCOLLECTOR'])
def clients(request):
    clients = Clients.objects.all()
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save()
            send_mail("Welcome garbege Collection", f"your Email was registred at the garabage collection website\n welcome to our community as we keep our homes clean\nThank you", settings.EMAIL_HOST_USER, [client.email])
            messages.success(request, f"New Client {client} Added")
            form = ClientForm()
        else:
            messages.error(request, f"{form.errors}")
    else:
        form = ClientForm()

    context = {'form': form, 'clients': clients}
    return render(request, 'adminn/clients.html', context)

def searchClient(request, email):
    clients = Clients.objects.get(email=email)
    
@role_required(['ADMIN', 'MCOLLECTOR'])
def editClient(request, pk):
    client = Clients.objects.get(id=pk)
    clients = Clients.objects.all()
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            client = form.save()
            messages.success(request, f"Client {client} Updated")
            form = ClientForm()
        else:
            messages.error(request, f"{form.errors}")
    else:
        form = ClientForm(instance=client)

    context = {'form': form, 'clients': clients}
    return render(request, 'adminn/edit-clients.html', context)


@role_required(['ADMIN', 'MCOLLECTOR'])
def changeClient(request, pk):
    client = Clients.objects.get(id=pk)

    if client.is_active:
        client.is_active = False
        messages.success(request, f"{client} Active Status Removed successfuly")
    else:
        client.is_active = True
        messages.success(request, f"{client} Active Status Activeted successfuly")

    client.save()
    return redirect("clients")


@role_required(['ADMIN', 'MCOLLECTOR'])
def schedule(request):
    schedules = Schedule.objects.all()
    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save()
            messages.success(request, f"{schedule} Collection Scheduled")
            form = ScheduleForm()
        else:
            messages.error(request, f"{form.errors}")
    else:
        form = ScheduleForm()

    context = {'form': form, 'schedules': schedules}
    return render(request, 'adminn/schedule.html', context)


@role_required(['ADMIN'])
def editSchedule(request, pk):
    schedules = Schedule.objects.all()
    schedule = Schedule.objects.get(id=pk)
    if schedule.status:
        return redirect('403')
    if request.method == 'POST':
        form = ScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            schedule = form.save()
            messages.success(request, f"{schedule} Collection Updated")
            return redirect('schedule')
            form = ScheduleForm()
        else:
            messages.error(request, f"{form.errors}")
    else:
        form = ScheduleForm(instance=schedule)

    context = {'form': form, 'schedules': schedules}
    return render(request, 'adminn/edit-schedule.html', context)


@role_required(['ADMIN'])
def changeSchedule(request, pk):
    schedule = Schedule.objects.get(id=pk)

    if schedule.status:
        schedule.status = False
        messages.success(request, f"{schedule} Status set to incomplite successfuly")
    else:
        schedule.status = True
        messages.success(request, f"{schedule} Status set to complited successfuly")

    schedule.save()
    return redirect("schedule")


def load_schedule(request):
    client_id = request.GET.get('client')
    client = Clients.objects.get(id = client_id)
    residence = client.residence
    # print(residence.location_id)
    schedules = Schedule.objects.filter(location_id=residence.location_id).filter(status=False)
    return render(request, "adminn/schedule_options.html", {'schedules': schedules})


@role_required(['ADMIN', 'MCOLLECTOR'])
def collection(request):
    collections = Collection.objects.all().order_by('-created_at')
    try:
        if request.method == 'POST':
            form = CollectionForm(request.POST)
            if form.is_valid():
                # try:
                # except IntegrityError:
                
                collection = Collection.objects.create(
                    client=form.cleaned_data['client'],
                    schedule=form.cleaned_data['schedule'],
                    status=form.cleaned_data['status'],
                    approved_by=request.user  # Set the logged-in user as the approver
                )

                collection.save()
                send_invoice_email(collection)
                # sendSms(f"This Is to Confirm that you have been checked for {collection.schedule} is complited", '+25'+collection.client.phone)
                messages.success(request, f"{collection.schedule} Collection Complited Successfuly")
                form = CollectionForm()
            else:
                messages.error(request, f"{form.errors}")
        else:
            form = CollectionForm()

    except IntegrityError:
            messages.error(request, "This Client already has a collection Record for this Schedule")
    
    context = {'form': form, 'collections': collections}
    return render(request, 'adminn/collection.html', context)

@role_required(['ADMIN', 'MCOLLECTOR'])
def changeCollection(request, pk):
    collection = Collection.objects.get(id=pk)

    if collection.status:
        collection.status = False
        messages.success(request, f"{collection} Collection status set to incomplite successfuly")
    else:
        collection.status = True
        messages.success(request, f"{collection} Collections status set to complited successfuly")

    collection.save()
    return redirect("collection")


@role_required(['ADMIN', 'MCOLLECTOR'])
def overflow(request):
    overflows = Overflow.objects.all()
    context = {'overflows': overflows}
    return render(request, 'adminn/overflow.html', context)

@role_required(['ADMIN', 'MCOLLECTOR'])
def statusOverflow(request, pk):
    overflow = Overflow.objects.get(id=pk)

    if overflow.status:
        overflow.status = False
        messages.success(request, f"Overflow set to unsloved successfuly")
    else:
        overflow.status = True
        messages.success(request, f"Overflow set to Solved successfuly")

    overflow.save()
    return redirect("overflow")

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
def accounts(request):
    users = User.objects.all()
    if request.method == "POST":
        form = CreateAccountForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data.get('password')
            user = form.save(commit=False)
            user.password = make_password(password)
            user.save()
            messages.success(request, "Account created successfuly. Now login")
            return redirect('accounts')
        else:
            messages.error(request, f"{form.errors}")

    else:
        form = CreateAccountForm()
    context = { 'form': form, 'users': users}
    return render(request, 'adminn/accounts.html', context)


@role_required(['ADMIN'])
def editAccounts(request, pk):
    users = User.objects.all()
    user = User.objects.get(id=pk)

    if request.method == "POST":
        form = EditAccountForm(request.POST, instance=user)

        if form.is_valid():
            user = form.save(commit=False)

            # Fetch the password from the form
            password = form.cleaned_data.get('password')

            if password:
                # If a password is provided, hash it
                user.password = make_password(password)
            else:
                # If no password is provided, keep the current password
                user.password = user.__class__.objects.get(pk=user.pk).password  # Retain original password

            # Save the user object with all other updates
            user.save()
            messages.success(request, 'Account has been updated successfully!')
            return redirect('accounts')
        else:
            messages.error(request, f"Error: {form.errors}")

    else:
        form = EditAccountForm(instance=user)

    context = { 'form': form, 'users': users }
    return render(request, 'adminn/edit-accounts.html', context)


@role_required(['ADMIN'])
def statusfeedbacks(request, pk):
    feedback = Feedback.objects.get(id=pk)
    if feedback.post_status:
        feedback.post_status = False
    else:
        feedback.post_status = True

    feedback.save()
    messages.success(request, f"Feedback Status Changed Successfuly")
    return redirect('feedbacks')


@login_required
def invoice(request, pk):
    collection = Collection.objects.get(id=pk)
    return render(request, 'invoice.html', {'collection': collection})

@role_required(['MCOLLECTOR'])
def mcollectorhome(request):
    return render(request, 'mcollector/index.html')


def sendSms(theBody, theTo):

    account_sid = os.getenv('DJANGO_ACCOUNT_SID')
    auth_token = os.getenv('DJANGO_AUTH_TOKEN')
    client = Client(account_sid, auth_token)

    message = client.messages.create(
    from_= os.getenv('DJANGO_SMS_FROM_NUMBER'),
    body= theBody,
    to= theTo
    )

    print(message.sid)

def send_invoice_email(collection):
    subject = 'Garbage Collection Invoice'
    from_email = settings.EMAIL_HOST_USER
    to = [collection.client.email]

    html_content = render_to_string('invoice.html', {'collection': collection})
    text_content = strip_tags(html_content)

    email = EmailMultiAlternatives(subject, text_content, from_email, to)
    email.attach_alternative(html_content, "text/html")  # Attach HTML content

    email.send()

def get_upcoming_schedules():
    all_schedules = Schedule.objects.all()
    
    upcoming_schedules = []
    for schedule in all_schedules:
        try:
            year, week_number = schedule.week.split('-W')
            
            schedule_start_date = datetime.strptime(f'{year}-W{week_number}-1', "%Y-W%W-%w")
            
            if schedule_start_date >= datetime.now():
                upcoming_schedules.append((schedule_start_date, schedule))
        except ValueError:
            continue


    upcoming_schedules.sort(key=lambda x: x[0])

    return [schedule for _, schedule in upcoming_schedules[:5]]