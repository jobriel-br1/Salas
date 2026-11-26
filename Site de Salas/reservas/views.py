from datetime import datetime, timedelta, time, date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Sala, Reserva, Usuario
from .forms import CadastroUsuarioForm, SalaForm, ReservaForm
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST
from django.db import transaction

def index(request):
    return render(request, 'reservas/index.html')

@login_required
@require_POST
def bloquear_horario(request):
    if not _eh_funcionario(request.user):
        raise PermissionDenied("Apenas funcionários podem bloquear horários.")

    sala_id = request.POST.get('sala')
    data_str = request.POST.get('data')
    inicio_str = request.POST.get('hora_inicio')
    fim_str = request.POST.get('hora_fim')
    motivo = (request.POST.get('atividade') or 'Bloqueio administrativo').strip()
    recusar_conflitos = request.POST.get('recusar_conflitos') == 'on'

    sala = get_object_or_404(Sala, id=sala_id)

    try:
        data_obj = datetime.strptime(data_str, '%Y-%m-%d').date()
        hora_inicio_obj = datetime.strptime(inicio_str, '%H:%M').time()
        hora_fim_obj = datetime.strptime(fim_str, '%H:%M').time()
    except (ValueError, TypeError):
        messages.error(request, "Data ou horário inválido para bloqueio.")
        return redirect('gerenciar_reservas')

    if hora_fim_obj <= hora_inicio_obj:
        messages.error(request, "O horário de término deve ser maior que o de início.")
        return redirect('gerenciar_reservas')

    with transaction.atomic():
        bloqueio = Reserva.objects.create(
            sala=sala,
            solicitante=request.user,
            data=data_obj,
            hora_inicio=hora_inicio_obj,
            hora_fim=hora_fim_obj,
            atividade=motivo,
            status='BLOQUEADA',
        )

        recusadas = 0
        if recusar_conflitos:
            pendentes = Reserva.objects.filter(
                sala=sala,
                data=data_obj,
                status='PENDENTE',
            ).exclude(id=bloqueio.id)

            for outra in pendentes:
                if _ha_sobreposicao(
                    hora_inicio_obj,
                    hora_fim_obj,
                    outra.hora_inicio,
                    outra.hora_fim,
                ):
                    outra.status = 'RECUSADA'
                    outra.save(update_fields=['status'])
                    rejeitadas += 1

    msg = (
        f"Horário bloqueado na sala {sala.nome} em {data_obj.strftime('%d/%m/%Y')} "
        f"({hora_inicio_obj.strftime('%H:%M')} às {hora_fim_obj.strftime('%H:%M')})."
    )
    if recusadas:
        msg += f" {recusadas} pendência(s) conflitante(s) foram recusadas."
    messages.success(request, msg)
    return redirect('gerenciar_reservas')


@login_required
@require_POST
def cancelar_reserva_funcionario(request, reserva_id):
    if not _eh_funcionario(request.user):
        raise PermissionDenied("Apenas funcionários podem cancelar reservas.")

    reserva = get_object_or_404(Reserva, id=reserva_id)
    reserva.status = 'CANCELADA'
    reserva.save(update_fields=['status'])
    messages.warning(request, "Reserva cancelada pelo funcionário.")
    return redirect('gerenciar_reservas')


@login_required
@require_POST
def remover_reserva_funcionario(request, reserva_id):
    if not _eh_funcionario(request.user):
        raise PermissionDenied("Apenas funcionários podem remover reservas.")

    reserva = get_object_or_404(Reserva, id=reserva_id)
    reserva.delete()
    messages.success(request, "Evento removido do sistema.")

    voltar_para = request.META.get('HTTP_REFERER')
    if voltar_para:
        return redirect(voltar_para)
    return redirect('gerenciar_reservas')

@login_required
@require_POST
def excluir_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id, solicitante=request.user)
    if reserva.status != 'RECUSADA':
        messages.error(request, "Só podes excluir reservas recusadas.")
        return redirect('minhas_reservas')

    reserva.delete()
    messages.success(request, "Reserva recusada excluída com sucesso.")
    return redirect('minhas_reservas')

from django.db import transaction

def _ha_sobreposicao(inicio_a, fim_a, inicio_b, fim_b):
    return inicio_a < fim_b and fim_a > inicio_b

@login_required
@require_POST
def decidir_reserva(request, reserva_id, acao):
    if not _eh_funcionario(request.user):
        raise PermissionDenied("Apenas funcionários podem aprovar ou rejeitar reservas.")

    with transaction.atomic():
        reserva = get_object_or_404(
            Reserva.objects.select_related('sala', 'solicitante'),
            id=reserva_id,
        )

        if acao == 'aprovar':
            reserva.status = 'APROVADA'
            reserva.save(update_fields=['status'])

            conflitantes = Reserva.objects.filter(
                sala=reserva.sala,
                data=reserva.data,
                status='PENDENTE',
            ).exclude(id=reserva.id)

            rejeitadas = 0
            for outra in conflitantes:
                if _ha_sobreposicao(
                    reserva.hora_inicio,
                    reserva.hora_fim,
                    outra.hora_inicio,
                    outra.hora_fim,
                ):
                    outra.status = 'RECUSADA'
                    outra.save(update_fields=['status'])
                    rejeitadas += 1

            msg = (
                f"Reserva ({reserva.atividade}) na sala {reserva.sala.nome} "
                f"em {reserva.data.strftime('%d/%m/%Y')} aprovada."
            )
            if rejeitadas:
                msg += f" {rejeitadas} reserva(s) conflitante(s) foram rejeitadas automaticamente."
            messages.success(request, msg)

        elif acao == 'rejeitar':
            reserva.status = 'RECUSADA'
            reserva.save(update_fields=['status'])
            messages.warning(
                request,
                f"Reserva ({reserva.atividade}) na sala {reserva.sala.nome} "
                f"em {reserva.data.strftime('%d/%m/%Y')} rejeitada.",
            )
        else:
            messages.error(request, "Ação inválida.")

    return redirect('gerenciar_reservas')

def _eh_funcionario(user) -> bool:
    if not user.is_authenticated:
        return False
    if getattr(user, 'is_funcionario', False):
        return True
    return getattr(user, 'funcao', None) == 'FUNCIONARIO'


@login_required
def gerenciar_reservas(request):
    if not _eh_funcionario(request.user):
        raise PermissionDenied("Apenas funcionários podem acessar esta página.")

    reservas_pendentes = (
        Reserva.objects.filter(status='PENDENTE')
        .select_related('sala', 'solicitante')
        .order_by('data', 'hora_inicio', 'criado_em')
    )

    return render(
        request,
        'reservas/gerenciar_reservas.html',
        {'reservas': reservas_pendentes},
    )





BLOCOS_HORARIO = [
    (time(7, 30), time(8, 20)),
    (time(8, 20), time(9, 10)),
    (time(9, 20), time(10, 10)),
    (time(10, 10), time(11, 0)),
    (time(11, 10), time(12, 0)),
    (time(12, 0), time(12, 50)),
    (time(13, 10), time(14, 0)),
    (time(14, 0), time(14, 50)),
    (time(15, 0), time(15, 50)),
    (time(15, 50), time(16, 40)),
    (time(16, 50), time(17, 40)),
    (time(17, 40), time(18, 30)),
]


@login_required
def calendario_sala(request, sala_id):
    sala = get_object_or_404(Sala, id=sala_id)

    semana_str = request.GET.get('semana', '')
    try:
        base_data = datetime.strptime(semana_str, '%Y-%m-%d').date() if semana_str else date.today()
    except ValueError:
        base_data = date.today()

    inicio_semana = base_data - timedelta(days=base_data.weekday())
    fim_semana = inicio_semana + timedelta(days=6)
    dias_semana = [inicio_semana + timedelta(days=i) for i in range(7)]

    reservas = (
        Reserva.objects.filter(
            sala=sala,
            data__range=(inicio_semana, fim_semana),
        )
        .exclude(status__in=['CANCELADA', 'RECUSADA'])
        .select_related('solicitante')
    )

    linhas = []
    for inicio_bloco, fim_bloco in BLOCOS_HORARIO:
        celulas = []
        for dia in dias_semana:
            reservas_no_bloco = [
                r for r in reservas
                if r.data == dia and r.hora_inicio <= inicio_bloco < r.hora_fim
            ]

            if reservas_no_bloco:
                if any(r.status == 'BLOQUEADA' for r in reservas_no_bloco):
                    estado, rotulo_estado = 'bloqueado', 'Bloqueado'
                elif any(r.status == 'APROVADA' for r in reservas_no_bloco):
                    estado, rotulo_estado = 'aprovada', 'Reservado (Aprovado)'
                else:
                    estado, rotulo_estado = 'pendente', 'Pendente'

                itens = []
                for r in reservas_no_bloco:
                    nome_solicitante = (
                        getattr(r.solicitante, 'nome_completo', '')
                        or r.solicitante.get_full_name()
                        or r.solicitante.username
                    )
                    itens.append({
                        'id': r.id,
                        'atividade': r.atividade,
                        'solicitante': nome_solicitante,
                        'status_display': r.get_status_display(),
                        'intervalo': f"{r.hora_inicio.strftime('%H:%M')} - {r.hora_fim.strftime('%H:%M')}",
                    })

                celulas.append({
                    'dia': dia,
                    'estado': estado,
                    'rotulo_estado': rotulo_estado,
                    'reservas': itens,
                })
            else:
                celulas.append({
                    'dia': dia,
                    'estado': 'vago',
                    'rotulo_estado': 'Vago',
                    'reservas': [],
                })

        linhas.append({
            'label': f"{inicio_bloco.strftime('%H:%M')} - {fim_bloco.strftime('%H:%M')}",
            'celulas': celulas,
        })

    context = {
        'salas': sala,
        'dias_semana': dias_semana,
        'linhas': linhas,
        'semana_anterior': (inicio_semana - timedelta(days=7)).isoformat(),
        'semana_seguinte': (inicio_semana + timedelta(days=7)).isoformat(),
        'inicio_semana': inicio_semana,
        'fim_semana': fim_semana,
    }
    return render(request, 'reservas/calendario_sala.html', context)



@login_required
def cadastrar_sala(request):
    if not request.user.is_funcionario:
        raise PermissionDenied("Apenas funcionários ou administradores podem criar salas.")

    if request.method == 'POST':
        form = SalaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_salas')
    else:
        form = SalaForm()

    return render(request, 'reservas/cadastrar_sala.html', {'form': form})

def cadastro(request):
    if request.method == 'POST':
        form = CadastroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('lista_salas')
    else:
        form = CadastroUsuarioForm()
    return render(request, 'reservas/cadastro.html', {'form': form})


@login_required
def lista_salas(request):
    salas = Sala.objects.all()
    return render(request, 'reservas/lista_salas.html', {'salas': salas})






def _fim_do_semestre(data_base: date) -> date:
    """Retorna o fim do semestre correspondente à data inicial."""
    if data_base.month <= 6:
        return date(data_base.year, 6, 30)
    return date(data_base.year, 12, 20)


def _converter_hora(valor) -> time:
    """Garante que hora_inicio e hora_fim sejam objetos datetime.time."""
    if isinstance(valor, time):
        return valor
    horas, minutos = map(int, str(valor).split(':')[:2])
    return time(horas, minutos)





@login_required
def solicitar_reserva(request):
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            dados = form.cleaned_data
            sala = dados['sala']
            tipo = dados['tipo_reserva']
            data_inicial = dados['data']
            hora_inicio = _converter_hora(dados['hora_inicio'])
            hora_fim = _converter_hora(dados['hora_fim'])
            atividade = dados['atividade']

            if tipo == 'SEMESTRAL':
                data_limite = _fim_do_semestre(data_inicial)
                datas_reserva = []
                data_atual = data_inicial
                while data_atual <= data_limite:
                    datas_reserva.append(data_atual)
                    data_atual += timedelta(days=7)
            else:
                datas_reserva = [data_inicial]

            reservas_existentes = Reserva.objects.filter(
                sala=sala,
                data__in=datas_reserva,
                status__in=['APROVADA', 'PENDENTE', 'BLOQUEADA'],
            ).select_related('solicitante')

            planos = []
            for d in datas_reserva:
                conflitos_dia = [
                    r for r in reservas_existentes
                    if r.data == d and _ha_sobreposicao(hora_inicio, hora_fim, r.hora_inicio, r.hora_fim)
                ]

                if any(r.status == 'BLOQUEADA' for r in conflitos_dia):
                    messages.error(
                        request,
                        f"O horário em {d.strftime('%d/%m/%Y')} está bloqueado pela administração."
                    )
                    return render(request, 'reservas/solicitar_reserva.html', {'form': form})

                if conflitos_dia:
                    messages.warning(
                        request,
                        f"Aviso: já existe uma reserva ativa ou pendente em {d.strftime('%d/%m/%Y')} neste horário. Sua solicitação será enviada para análise."
                    )

                planos.append((d, 'PENDENTE'))

            for d, status_nova in planos:
                Reserva.objects.create(
                    sala=sala,
                    solicitante=request.user,
                    data=d,
                    hora_inicio=hora_inicio,
                    hora_fim=hora_fim,
                    atividade=atividade,
                    tipo_reserva=tipo,
                    status=status_nova,
                )

            if len(planos) > 1:
                messages.success(
                    request,
                    f"Solicitação semestral enviada ({len(planos)} ocorrências até {planos[-1][0].strftime('%d/%m/%Y')}). Aguarde a aprovação de um funcionário."
                )
            else:
                messages.success(
                    request,
                    "Solicitação enviada! Aguarde a aprovação de um funcionário."
                )

            return redirect('minhas_reservas')
    else:
        initial = {}
        if request.GET.get('sala'):
            initial['sala'] = request.GET.get('sala')
        if request.GET.get('data'):
            initial['data'] = request.GET.get('data')
        if request.GET.get('hora'):
            initial['hora_inicio'] = request.GET.get('hora')
        form = ReservaForm(initial=initial)

    return render(request, 'reservas/solicitar_reserva.html', {'form': form})


@login_required
def minhas_reservas(request):
    reservas = (
        Reserva.objects.filter(solicitante=request.user)
        .exclude(status='CANCELADA')
        .select_related('sala')
        .order_by('data', 'hora_inicio')
    )
    return render(request, 'reservas/minhas_reservas.html', {'reservas': reservas})





@login_required
def cancelar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id, solicitante=request.user)
    if request.method == 'POST':
        reserva.status = 'CANCELADA'
        reserva.save()
        messages.success(request, "Reserva cancelada com sucesso.")
    return redirect('minhas_reservas')


# --- ÁREA RESTRITA AOS FUNCIONÁRIOS / ADMINISTRADORES ---

@login_required
def cadastrar_sala(request):
    if not request.user.is_funcionario:
        messages.error(request, "Apenas funcionários/administradores podem cadastrar salas.")
        return redirect('lista_salas')

    if request.method == 'POST':
        form = SalaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Sala cadastrada com sucesso!")
            return redirect('lista_salas')
    else:
        form = SalaForm()
    return render(request, 'reservas/cadastrar_sala.html', {'form': form})


@login_required
def avaliar_solicitacoes(request):
    if not request.user.is_funcionario:
        return redirect('lista_salas')

    pendentes = Reserva.objects.filter(status='PENDENTE')
    if request.method == 'POST':
        res_id = request.POST.get('reserva_id')
        acao = request.POST.get('acao')
        reserva = get_object_or_404(Reserva, id=res_id)
        if acao == 'aprovar':
            reserva.status = 'APROVADA'
        elif acao == 'recusar':
            reserva.status = 'RECUSADA'
        reserva.save()
        return redirect('avaliar_solicitacoes')

    return render(request, 'reservas/avaliar_solicitacoes.html', {'pendentes': pendentes})


@login_required
def bloquear_horario(request, sala_id):
    if not request.user.is_funcionario:
        return redirect('lista_salas')

    sala = get_object_or_404(Sala, id=sala_id)
    if request.method == 'POST':
        data = request.POST.get('data')
        hora = datetime.strptime(request.POST.get('hora'), '%H:%M').time()
        Reserva.objects.update_or_create(
            sala=sala,
            data=data,
            hora_inicio=hora,
            defaults={
                'solicitante': request.user,
                'atividade': 'Bloqueado',
                'status': 'BLOQUEADA'
            }
        )
        messages.success(request, f"Horário {hora.strftime('%H:%M')} bloqueado na sala {sala.nome}.")
    return redirect('calendario_sala', sala_id=sala.id)
