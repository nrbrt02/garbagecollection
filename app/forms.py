from django import forms
from .models import Location, Residence, Client, Schedule, Collection, District, Sector, Cell, Village

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'inputEmail'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'inputPassword'}))

# class LocationsFrom(forms.ModelForm):
#     class Meta:
#         model = Location
#         fields = '__all__'
#         widgets={
#             'district': forms.Select(attrs={'class': 'form-control'}),
#             'sector': forms.Select(attrs={'class': 'form-control'}),
#             'cell': forms.Select(attrs={'class': 'form-control'}),
#             'village': forms.Select(attrs={'class': 'form-control'}),
#         }


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

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
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
            'week': forms.TextInput(attrs={'type': 'week', 'class': 'form-control'}),
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
        current_year, current_week_number = datetime.now().isocalendar()[:2]

        # Validate that the selected week is not in the past
        if year < current_year or (year == current_year and week_number < current_week_number):
            raise forms.ValidationError("The Scheduled week cannot be in the past.")

        return week


class CollectionForm(forms.ModelForm):
    class Meta:
        model = Collection
        fields = '__all__'

        widgets = {
            'schedule': forms.Select(attrs={'class': 'form-control'}),
            'client': forms.Select(attrs={'class': 'form-control'}),
            'approved_by': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            }