from django import forms
from .models import Location, Residence, Clients, Schedule, Collection, District, Sector, Cell, Village, User, Overflow, Feedback
import datetime
class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'inputEmail'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'inputPassword'}))

class LocationsForm(forms.Form):
    
    district = forms.ModelChoiceField(queryset=District.objects.all(),
        widget=forms.Select(attrs={'hx-get': 'load-sectors/', 'hx-target': '#id_sector', 'class': 'form-control'})
    )
    sector = forms.ModelChoiceField(queryset=Sector.objects.none(),
        widget=forms.Select(attrs={'hx-get': 'load-cells/', 'hx-target': '#id_cell', 'class': 'form-control'})
    )
    cell = forms.ModelChoiceField(queryset=Cell.objects.none(),
        widget=forms.Select(attrs={'hx-get': 'load-villages/', 'hx-target': '#id_village', 'class': 'form-control'})
    )
    village = forms.ModelChoiceField(queryset=Village.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "district" in self.data:
            district_id = int(self.data.get("district"))
            self.fields['sector'].queryset = Sector.objects.filter(district_id = district_id)
            if "sector" in self.data:
                sector_id = int(self.data.get("sector"))
                self.fields['cell'].queryset = Cell.objects.filter(sector_id = sector_id)
                if "cell" in self.data:
                    cell_id = int(self.data.get("cell"))
                    self.fields['village'].queryset = Village.objects.filter(cell_id = cell_id)



class ResidenceForm(forms.ModelForm):
    class Meta:
        model = Residence
        fields = '__all__'
        widgets={
            'location': forms.Select(attrs={'class': 'form-control'}),
            'streetName': forms.TextInput(attrs={'class': 'form-control'}),
            'gateNumber': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),

        }


class EditResidenceForm(forms.ModelForm):
    class Meta:
        model = Residence
        fields = '__all__'
        exclude = ['location']  # Exclude location from validation
        widgets = {
            'streetName': forms.TextInput(attrs={'class': 'form-control'}),
            'gateNumber': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super(EditResidenceForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields['location'] = forms.ModelChoiceField(
                queryset=Location.objects.all(),
                widget=forms.Select(attrs={'class': 'form-control', 'disabled': 'disabled'}),
                initial=self.instance.location
            )
            self.fields['location'].required = False


class ClientForm(forms.ModelForm):
    class Meta:
        model = Clients
        fields = '__all__'
        widgets = {
            'names': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'residence': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),

        }

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = '__all__'
        exclude = ['status']
        widgets = {
            'week': forms.DateInput(attrs={'class': 'form-control', 'type': 'week'}),
            'day': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.Select(attrs={'class': 'form-control'}),
            'driver': forms.TextInput(attrs={'class': 'form-control'}),
            'plate': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),

        }
    def clean_week(self):
        week = self.cleaned_data['week']

        # Extract year and week from the string (format: YYYY-WW)
        year, week_number = map(int, week.split('-W'))
        
        # Get the current year and week number
        current_year, current_week_number = datetime.datetime.now().isocalendar()[:2]

        # Validate that the selected week is not in the past
        if year < current_year or (year == current_year and week_number < current_week_number):
            raise forms.ValidationError("The Scheduled week cannot be in the past.")

        return week


# class CollectionForm(forms.ModelForm):
#     class Meta:
#         model = Collection
#         fields = '__all__'
#         exclude = ['approved_by']


#         widgets = {
#             'schedule': forms.Select(attrs={'class': 'form-control'}),
#             'client': forms.Select(attrs={'class': 'form-control'}),
#             'approved_by': forms.Select(attrs={'class': 'form-control'}),
#             'status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
#             }

class CollectionForm(forms.Form):
    client = forms.ModelChoiceField(queryset=Clients.objects.all(),
        widget=forms.Select(attrs={'hx-get': 'load-schedule/', 'hx-target': '#id_schedule', 'class': 'form-control'}))
    schedule = forms.ModelChoiceField(queryset=Schedule.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'}))
    status =  forms.BooleanField(initial=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "client" in self.data:
            client_id = int(self.data.get("client"))
            client = Clients.objects.get(id = client_id)
            residence = client.residence
            self.fields['schedule'].queryset = Schedule.objects.filter(location_id=residence.location_id).filter(status=False)



class CreateAccountForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'
        exclude = ['is_superuser', 'last_login', 'is_staff', 'date_joined', 'groups', 'user_permissions']
        widgets = {
            'username':forms.TextInput(attrs={'class': 'form-control'}),
            'first_name':forms.TextInput(attrs={'class': 'form-control'}),
            'last_name':forms.TextInput(attrs={'class': 'form-control'}),
            'email':forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number':forms.TextInput(attrs={'class': 'form-control'}),
            'role':forms.Select(attrs={'class': 'form-control'}),
            'password':forms.PasswordInput(attrs={'class': 'form-control'}),
            'last_name':forms.TextInput(attrs={'class': 'form-control'}),
         }

class EditAccountForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'
        exclude = ['is_superuser', 'last_login', 'is_staff', 'date_joined', 'groups', 'user_permissions']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(EditAccountForm, self).__init__(*args, **kwargs)
        self.fields['password'].required = False

class ClientSelfForm(forms.ModelForm):
        class Meta:
            model = Clients
            fields = '__all__'
            exclude = ['is_active']
            widgets = {
                'names': forms.TextInput(attrs={'class': 'form-control'}),
                'phone': forms.TextInput(attrs={'class': 'form-control'}),
                'email': forms.EmailInput(attrs={'class': 'form-control'}),
                'residence': forms.Select(attrs={'class': 'form-control'}),
                # 'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),

            }


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = '__all__'
        exclude = ['post_status', 'client']
        widgets = {
                'email': forms.EmailInput(attrs={'class': 'form-control'}),
                'message': forms.Textarea(attrs={'class': 'form-control'}),
                'rating': forms.Select(attrs={'class': 'form-control'}, choices=[(i, i) for i in range(1, 6)]),  # Ratings from 1 to 5

        }


class OverflowForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}))
    # location = forms.ModelChoiceField(queryset=Location.objects.all(),widget=forms.Select(attrs={'class': 'form-control'}),empty_label="Select a location")
    image = forms.FileField(widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))
    class Meta:
        model = Overflow
        fields = ['email', 'image']


