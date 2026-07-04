from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, ProviderProfile, Skill

class CustomerRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_customer = True
        if commit:
            user.save()
        return user

class ProviderRegistrationForm(UserCreationForm):
    experience = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))
    price_per_service = forms.DecimalField(max_digits=10, decimal_places=2)
    profile_photo = forms.ImageField(required=False)
    id_proof = forms.FileField()
    skills = forms.CharField(help_text="Comma-separated skills (e.g. Python Tutor, Django Developer)")
    contact_details = forms.CharField(help_text="Email or Phone shown only on confirmed booking")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_provider = True
        if commit:
            user.save()
            profile = ProviderProfile.objects.create(
                user=user,
                experience=self.cleaned_data['experience'],
                price_per_service=self.cleaned_data['price_per_service'],
                profile_photo=self.cleaned_data.get('profile_photo'),
                id_proof=self.cleaned_data['id_proof'],
                contact_details=self.cleaned_data['contact_details'],
                status='Pending'
            )
            # Process skills
            skills_str = self.cleaned_data.get('skills', '')
            skill_names = [s.strip() for s in skills_str.split(',') if s.strip()]
            for name in skill_names:
                Skill.objects.create(provider=profile, name=name)
        return user
