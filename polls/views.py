from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Email
from .forms import EmailForm
from .utils import avaliar_email
import re

def index(request):
    context = {}
    emails = Email.objects.order_by("id")
    return render(request, "polls/index.html", {"emails": emails})

def sendEmail(request):
    form = EmailForm(request.POST, request.FILES)
    if form.is_valid():
        email = form.save(commit=False)
        arquivo_path = email.arquivo_email.path if email.arquivo_email else None

        produtivo, justificativa, nota = avaliar_email(email.texto_email, arquivo_path)
        try:

            email.tipo_classificacao = produtivo
            email.resposta_email = justificativa
            email.classificacao = nota
            email.save()

            messages.success(request, "✅ E-mail cadastrado e avaliado pela IA com sucesso!")
        except Exception as e:
            messages.error(request, f"⚠️ Erro ao enviar para o OpenAI: {e}")
            email.delete()
    else:
        messages.error(request, "❌ Ocorreu um erro ao salvar. Verifique os dados e tente novamente.")
    emails = Email.objects.order_by("id")
    return render(request, "polls/index.html", {"emails": emails})    