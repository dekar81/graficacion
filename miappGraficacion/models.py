from django.db import models

class Medicion(models.Model):
    nombre_fecha_hora = models.CharField(max_length=100)  # Campo tipo cadena
    sensor1 = models.FloatField()         # Campo float 1
    sensor2 = models.FloatField()             # Campo float 2
    sensor3 = models.FloatField()             # Campo float 3
    sensor4 = models.FloatField()           # Campo float 4
    sensor5 = models.FloatField()                # Campo float 5
    
    def __str__(self):
        return f"{self.nombre}  - {self.sensor1}, {self.sensor2}, {self.sensor3}, {self.sensor4}, {self.sensor5}"