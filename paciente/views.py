from django.shortcuts import render, redirect
from medico.models import DadosMedico, Especialidades, DatasAbertas
from datetime import datetime
from .models import Consulta
from django.contrib.messages import constants
from django.contrib import messages, auth
from django.db import transaction


def home(request):
    if request.method == "GET":
        medico_filtrar = request.GET.get('medico')
        especialidades_filtrar = request.GET.getlist('especialidades')

        medicos = DadosMedico.objects.all()

        if medico_filtrar:
            medicos = medicos.filter(nome__icontains = medico_filtrar)

        especialidades = Especialidades.objects.all()

        if especialidades_filtrar:
            medicos = medicos.filter(especialidade_id__in=especialidades_filtrar)
            
        return render(request, 'home.html', {'medicos': medicos, 'especialidades': especialidades})
    

def escolher_horario(request, id_dados_medicos):
    if request.method == "GET":
        medico = DadosMedico.objects.get(id=id_dados_medicos)
        datas_abertas = DatasAbertas.objects.filter(user=medico.user).filter(data__gte=datetime.now()).filter(agendado=False)
        return render(request, 'escolher_horario.html', {'medico': medico, 'datas_abertas': datas_abertas})
    

def agendar_horario(request, id_data_aberta):
    if request.method == "GET":
        data_aberta = DatasAbertas.objects.get(id=id_data_aberta)

        # Criar a consulta dentro de uma transação atômica
        with transaction.atomic():
            horario_agendado = Consulta.objects.create(
                paciente=request.user,
                data_aberta=data_aberta
            )

            data_aberta.agendado = True
            data_aberta.save()

        messages.add_message(request, constants.SUCCESS, 'Horário agendado com sucesso.')

        return redirect('/pacientes/minhas_consultas/')
    

def minhas_consultas(request):
    if request.method == "GET":
        #TODO: desenvolver filtros
        minhas_consultas = Consulta.objects.filter(paciente=request.user).filter(data_aberta__data__gte=datetime.now())
        return render(request, 'minhas_consultas.html', {'minhas_consultas': minhas_consultas})
