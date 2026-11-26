from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, Sala, Reserva

class CadastroUsuarioForm(UserCreationForm):
    nome_completo = forms.CharField(label="Nome", max_length=150)
    email = forms.EmailField(label="E-mail")
    nusp = forms.CharField(label="NUSP", max_length=20)
    funcao = forms.ChoiceField(label="Função", choices=Usuario.FUNCAO_CHOICES)

    class Meta:
        model = Usuario
        fields = ('email', 'nusp', 'funcao')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['nusp']  # Usa o NUSP ou Nome como login único
        user.first_name = self.cleaned_data['nome_completo']
        if commit:
            user.save()
        return user


class SalaForm(forms.ModelForm):
    class Meta:
        model = Sala
        fields = ['nome', 'departamento', 'capacidade']


class ReservaForm(forms.ModelForm):
    HORARIOS_PADRAO = [
        ('08:00', '08:00'),
        ('09:00', '09:00'),
        ('10:00', '10:00'),
        ('11:00', '11:00'),
        ('13:00', '13:00'),
        ('14:00', '14:00'),
        ('15:00', '15:00'),
        ('16:00', '16:00'),
        ('17:00', '17:00'),
        ('18:00', '18:00'),
        ('19:00', '19:00'),
        ('20:00', '20:00'),
    ]

    tipo_reserva = forms.ChoiceField(
        label="Tipo de reserva",
        choices=Reserva.TIPO_RESERVA_CHOICES,
        initial='PONTUAL',
    )
    data = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    hora_inicio = forms.ChoiceField(label="Horário de início", choices=HORARIOS_PADRAO)
    hora_fim = forms.ChoiceField(label="Horário de término", choices=HORARIOS_PADRAO)

    class Meta:
        model = Reserva
        fields = ['sala', 'tipo_reserva', 'data', 'hora_inicio', 'hora_fim', 'atividade']

    def clean(self):
        cleaned_data = super().clean()
        inicio = cleaned_data.get('hora_inicio')
        fim = cleaned_data.get('hora_fim')
        if inicio and fim and fim <= inicio:
            self.add_error('hora_fim', "O horário de término deve ser maior que o de início.")
        return cleaned_data