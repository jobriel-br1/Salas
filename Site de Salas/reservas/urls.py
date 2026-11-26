from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', auth_views.LoginView.as_view(template_name='reservas/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('cadastro/', views.cadastro, name='cadastro'),
    
    path('alocacao-salas/', views.lista_salas, name='lista_salas'),
    path('sala/<int:sala_id>/calendario/', views.calendario_sala, name='calendario_sala'),
    path('reservar/', views.solicitar_reserva, name='solicitar_reserva'),
    path('minhas-reservas/', views.minhas_reservas, name='minhas_reservas'),
    path('reservas/<int:reserva_id>/cancelar/', views.cancelar_reserva, name='cancelar_reserva'),
    path('reservas/<int:reserva_id>/excluir/', views.excluir_reserva, name='excluir_reserva'),
    path('gerenciar/bloquear/', views.bloquear_horario, name='bloquear_horario'),
    path('gerenciar/reservas/<int:reserva_id>/cancelar/', views.cancelar_reserva_funcionario, name='cancelar_reserva_funcionario'),
    path('gerenciar/reservas/<int:reserva_id>/remover/', views.remover_reserva_funcionario, name='remover_reserva_funcionario'),
    
    # Funcionários / Administradores
    path('salas/nova/', views.cadastrar_sala, name='cadastrar_sala'),
    path('solicitacoes/', views.avaliar_solicitacoes, name='avaliar_solicitacoes'),
    path('sala/<int:sala_id>/bloquear/', views.bloquear_horario, name='bloquear_horario'),
    path('gestao/reservas/', views.gerenciar_reservas, name='gerenciar_reservas'),
    path('gestao/reservas/<int:reserva_id>/<str:acao>/', views.decidir_reserva, name='decidir_reserva'),
]