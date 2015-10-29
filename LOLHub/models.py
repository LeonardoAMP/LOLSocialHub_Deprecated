from django.db import models

# Create your models here.
class Summoners(models.Model):
	Nombre = models.CharField(max_length=20)
	Activo = models.BooleanField(default=True)
	Id = models.IntegerField(primary_key=True)
	SummonerIcon = models.CharField(max_length=20,null=True)
	Tier = models.CharField(max_length=20,null=True)
	Division = models.CharField(max_length=20, null=True)	
	Lv = models.IntegerField(null=True)
	LP = models.CharField(max_length=4,null=True)
	Score = models.IntegerField(null=True)

class Streamers(models.Model):
	Nombre = models.CharField(max_length=20)
	Activo = models.BooleanField(default=True)