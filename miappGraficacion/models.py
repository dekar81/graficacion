from django.db import models

class Medicion(models.Model):
    nombre_fecha_hora = models.CharField(max_length=100)
    sensor1 = models.FloatField()
    sensor2 = models.FloatField()
    sensor3 = models.FloatField()
    sensor4 = models.FloatField()
    sensor5 = models.FloatField()
    sensor6 = models.FloatField()
    sensor7 = models.FloatField()
    sensor8 = models.FloatField()
    
    def __str__(self):
        # También necesitamos actualizar este método para incluir los nuevos campos
        return f"{self.nombre_fecha_hora} - {self.sensor1}, {self.sensor2}, {self.sensor3}, {self.sensor4}, {self.sensor5}, {self.sensor6}, {self.sensor7}, {self.sensor8}"
