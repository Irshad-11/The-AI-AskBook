from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User , Post

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password1",
            "password2",
        ]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already registered.")
        return email



class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username")




class PostForm(forms.ModelForm):
    tags = forms.CharField(
        required=False,
        help_text="Space separated tags (e.g. django ai prompts)",
        widget=forms.TextInput(attrs={
            "class": "w-full bg-slate-900 border border-slate-800 rounded-lg px-4 py-2"
        })
    )

    class Meta:
        model = Post
        fields = [
            "title",
            "summary",
            "prompt_text",
            "description_md",
            "difficulty_level",
            "is_public",
            "ai_model",
        ]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "w-full bg-slate-900 border border-slate-800 rounded-lg px-4 py-2"
            }),
            "summary": forms.Textarea(attrs={
                "rows": 3,
                "class": "w-full bg-slate-900 border border-slate-800 rounded-lg px-4 py-2"
            }),
            "prompt_text": forms.Textarea(attrs={
                "rows": 4,
                "class": "w-full bg-slate-900 border border-slate-800 rounded-lg px-4 py-2"
            }),
            "description_md": forms.Textarea(attrs={
                "rows": 10,
                "class": "w-full bg-slate-900 border border-slate-800 rounded-lg px-4 py-2 font-mono"
            }),
            "difficulty_level": forms.Select(attrs={
                "class": "bg-slate-900 border border-slate-800 rounded-lg px-3 py-2"
            }),
            "is_public": forms.CheckboxInput(attrs={
                "class": "rounded bg-slate-900 border-slate-700"
            }),
            "ai_model": forms.TextInput(attrs={
                "class": "rounded bg-slate-900 border-slate-700"
            }),
        }



class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "avatar",
            "bio",
            "works_at",
            "institute_at",
            "location",
        ]
        widgets = {
            "bio": forms.Textarea(attrs={
                "rows": 4,
                "class": "w-full bg-slate-900 border border-slate-800 rounded-lg px-4 py-2"
            }),
            "works_at": forms.TextInput(attrs={
                "class": "w-full bg-slate-900 border border-slate-800 rounded-lg px-4 py-2"
            }),
            "institute_at": forms.TextInput(attrs={
                "class": "w-full bg-slate-900 border border-slate-800 rounded-lg px-4 py-2"
            }),
            "location": forms.TextInput(attrs={
                "class": "w-full bg-slate-900 border border-slate-800 rounded-lg px-4 py-2"
            }),
        }