# forms.py
from django import forms
from .models import Cinema, Sala

class CinemaRegistroForm(forms.ModelForm):
    class Meta:
        model = Cinema
        fields = [
            'nome', 'localizacao', 'telefone'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'localizacao': forms.TextInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+244 XXX XXX XXX'}),
        }

class SalaRegistroForm(forms.ModelForm):
    class Meta:
        model = Sala
        fields = ['cinema', 'nome', 'capacidade']
        widgets = {
            'cinema': forms.HiddenInput(),
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'capacidade': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }