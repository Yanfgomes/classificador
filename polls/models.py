from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
# Create your models here.

class Email(models.Model):
    id = models.IntegerField(primary_key=True, auto_created=True)
    data = models.DateTimeField(auto_now_add=True)
    texto_email = models.TextField()
    arquivo_email = models.FileField(upload_to='emails/', blank=True, null=True)  # vai salvar em MEDIA_ROOT/emails/
    resposta_email = models.TextField(blank=True, null=True)
    tipo_classificacao = models.TextField(blank=True, null=True)
    classificacao = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )

    def __str__(self):
        return f"E-mail {self.id} - Classificação: {self.classificacao}"