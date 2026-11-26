from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

class Usuario(AbstractUser):
    FUNCAO_CHOICES = [
        ('ALUNO', 'Aluno'),
        ('PROFESSOR', 'Professor'),
        ('FUNCIONARIO', 'Funcionário / Administrador'),
    ]
    nome_completo = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    nusp = models.CharField(max_length=20, unique=True, verbose_name="NUSP")
    funcao = models.CharField(max_length=15, choices=FUNCAO_CHOICES, default='ALUNO')

    def __str__(self):
        return f"{self.nome_completo} ({self.get_funcao_display()} - {self.nusp})"

    @property
    def is_funcionario(self):
        return self.funcao == 'FUNCIONARIO' or self.is_superuser

    @property
    def is_professor(self):
        return self.funcao == 'PROFESSOR'




class Sala(models.Model):
    nome = models.CharField(max_length=50, unique=True)  # Ex: A2, A3, A5
    departamento = models.CharField(max_length=100)       # Ex: Mecatrônica / Engenharia
    capacidade = models.IntegerField(default=40)

    def __str__(self):
        return f"{self.nome} - {self.departamento}"


class Reserva(models.Model):
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente de Aprovação'),
        ('APROVADA', 'Aprovada'),
        ('RECUSADA', 'Recusada / Substituída por Prioridade'),
        ('CANCELADA', 'Cancelada pelo Usuário'),
        ('BLOQUEADA', 'Bloqueada pelo Funcionário'),
    ]

    TIPO_RESERVA_CHOICES = [
        ('PONTUAL', 'Pontual'),
        ('SEMESTRAL', 'Semestral'),
    ]

    tipo_reserva = models.CharField(
        max_length=15,
        choices=TIPO_RESERVA_CHOICES,
        default='PONTUAL',
    )

    sala = models.ForeignKey(Sala, on_delete=models.CASCADE, related_name='reservas')
    solicitante = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='minhas_reservas')
    data = models.DateField()
    hora_inicio = models.TimeField()  # Ex: 08:00, 10:00, 11:00, 14:00...
    hora_fim = models.TimeField()
    atividade = models.CharField(max_length=100)  # Ex: Aula 1, Extensão, Evento, Grupo C
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDENTE')
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['data', 'hora_inicio']

    def __str__(self):
        return f"{self.sala.nome} | {self.data} às {self.hora_inicio} ({self.status})"

    def save(self, *args, **kwargs):
        funcao_solicitante = (
            getattr(self.solicitante, 'funcao', None)
            if self.solicitante_id
            else None
        )
        super().save(*args, **kwargs)

    def clean(self):
        if self.hora_inicio and self.hora_fim and self.hora_fim <= self.hora_inicio:
            raise ValidationError("O horário de término deve ser posterior ao horário de início.")

    