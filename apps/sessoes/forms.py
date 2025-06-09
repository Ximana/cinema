# forms.py
from django import forms
from .models import Sessao
from apps.cinemas.models import Cinema, Sala
from apps.filmes.models import Filme
from django.utils import timezone

class SessaoForm(forms.ModelForm):
    class Meta:
        model = Sessao
        fields = ['sala', 'horario', 'preco_base', 'tipo', 'idioma']
        widgets = {
            'horario': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control'
                }
            ),
            'sala': forms.Select(attrs={'class': 'form-select'}),
            'preco_base': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                    'min': '0'
                }
            ),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'idioma': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'sala': 'Sala',
            'horario': 'Data e Horário',
            'preco_base': 'Preço Base (Kz)',
            'tipo': 'Tipo de Sessão',
            'idioma': 'Idioma',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Organizar salas por cinema
        self.fields['sala'].queryset = Sala.objects.select_related('cinema').order_by('cinema__nome', 'nome')
        
    def clean_horario(self):
        horario = self.cleaned_data.get('horario')
        if horario:
            # Usar timezone.now() em vez de datetime.now()
            if horario < timezone.now():
                raise forms.ValidationError("A sessão não pode ser agendada para uma data/hora passada.")
        return horario

    def clean_preco_base(self):
        preco = self.cleaned_data.get('preco_base')
        if preco and preco <= 0:
            raise forms.ValidationError("O preço deve ser maior que zero.")
        return preco