import os
import csv
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MisProyectosDjango.settings')
django.setup()

from miappGraficacion.models import Producto

def importar_datos():
    with open('datos.csv', mode='r', encoding='utf-8') as archivo:
        lector = csv.DictReader(archivo)
        for fila in lector:
            Producto.objects.create(
                nombre=fila['nombre'],
                precio=float(fila['precio']),
                descripcion=fila['descripcion']
            )
    print("Datos importados exitosamente!")

if __name__ == '__main__':
    importar_datos()