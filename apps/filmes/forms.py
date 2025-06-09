from django import forms
from .models import Filme

class FilmeRegistroForm(forms.ModelForm):
    class Meta:
        model = Filme
        fields = [
            'titulo', 'sinopse', 'duracao_minutos', 'diretor', 'classificacao',
            'site_oficial', 'trailer_oficial_url', 'data_lancamento', 'genero', 'poster'
        ]
        widgets = {
            'data_lancamento': forms.DateInput(attrs={'type': 'date'}),
            'poster': forms.FileInput(attrs={'class': 'form-control-file'}),
            'sinopse': forms.Textarea(attrs={'rows': 4}),
            'site_oficial': forms.URLInput(),
            'trailer_oficial_url': forms.URLInput(),
        }