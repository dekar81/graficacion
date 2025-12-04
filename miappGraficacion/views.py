# librerias necesarias
import random
import seaborn as sns
import pandas as pd
import numpy as np
import csv
import os
import matplotlib
matplotlib.use('Agg')  # Configura el backend ANTES de pyplot
import matplotlib.pyplot as plt
from io import BytesIO
import base64

from django.shortcuts import render, redirect, HttpResponse
from django.conf import settings
from django.urls import reverse
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.generic import ListView
from django.views.decorators.csrf import csrf_exempt

# Rest Framework
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Locales
from .models import Medicion
from .forms import CSVUploadForm
from .serializers import MedicionSerializer


# Pagina de inicio de prueba con enlaces
def home(request):
    menu_items = [
        {
            'nombre': 'Subir Archivos CSV',
            'url': 'seleccion_csv',
            'icono': 'bi-upload',
            'descripcion': 'Sube archivos CSV para procesar y visualizar datos'
        },
        {
            'nombre': 'Ver Gráficas',
            'url': 'graficas',
            'icono': 'bi-graph-up',
            'descripcion': 'Visualiza los datos en gráficos interactivos'
        },
        {
            'nombre': 'Lista de Mediciones',
            'url': 'lista_mediciones',
            'icono': 'bi-table',
            'descripcion': 'Explora todas las mediciones registradas'
        },
        {
            'nombre': 'Importar CSV a BD',
            'url': 'import_csv',
            'icono': 'bi-database-add',
            'descripcion': 'Carga datos CSV a la base de datos'
        },
        {
            'nombre': 'Consulta de Mediciones',
            'url': 'medicion-list',
            'icono': 'bi-search',
            'descripcion': 'Consulta avanzada de mediciones'
        }
    ]
    return render(request, 'miappGraficacion/home.html', {'menu_items': menu_items})


# agregar valores a la base de datos, se puede usar para pruebas
def import_csv(request):
    if request.method == 'GET':
        file_path = 'miappGraficacion/static/miappGraficacion/data/dekar.csv' 
        
        try:
            with open(file_path, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    Medicion.objects.create(
                        nombre_fecha_hora=row['nombre_fecha_hora'],
                        sensor1=float(row['dato1']),
                        sensor2=float(row['dato2']),
                        sensor3=float(row['dato3']),
                        sensor4=float(row['dato4']),
                        sensor5=float(row['dato5']),
                        sensor6=float(row['dato6']),
                        sensor7=float(row['dato7']),
                        sensor8=float(row['dato8'])
                    )
            
            return HttpResponse("Datos importados exitosamente")
        except FileNotFoundError:
            return HttpResponse("Archivo no encontrado", status=404)
        except Exception as e:
            return HttpResponse(f"Error: {str(e)}", status=500)


# Selecciona datos en la base de datos
class MedicionListView(ListView):
    model = Medicion
    template_name = 'miappGraficacion/medicion_list.html'
    context_object_name = 'mediciones'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtro por nombre de sensor
        nombre_sensor = self.request.GET.get('nombre_sensor')
        if nombre_sensor:
            queryset = queryset.filter(nombre_fecha_hora__icontains=nombre_sensor)
        
        # Filtros numéricos para cada sensor
        sensor_filters = {}
        for sensor in ['sensor1', 'sensor2', 'sensor3', 'sensor4', 'sensor5', 'sensor6', 'sensor7', 'sensor8']:
            min_val = self.request.GET.get(f'{sensor}_min')
            max_val = self.request.GET.get(f'{sensor}_max')
            
            if min_val:
                try:
                    sensor_filters[f'{sensor}__gte'] = float(min_val)
                except ValueError:
                    pass
            if max_val:
                try:
                    sensor_filters[f'{sensor}__lte'] = float(max_val)
                except ValueError:
                    pass
        
        if sensor_filters:
            queryset = queryset.filter(**sensor_filters)
        
        return queryset.order_by('nombre_fecha_hora')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Mantener los parámetros de filtro en el contexto
        context['nombre_sensor'] = self.request.GET.get('nombre_sensor', '')
        
        # Agregar los valores mínimos/máximos actuales para cada sensor
        for sensor in ['sensor1', 'sensor2', 'sensor3', 'sensor4', 'sensor5', 'sensor6', 'sensor7', 'sensor8']:
            context[f'{sensor}_min'] = self.request.GET.get(f'{sensor}_min', '')
            context[f'{sensor}_max'] = self.request.GET.get(f'{sensor}_max', '')
        
        return context
# Fin de funcion para seleccionar datos en la base de datos


# Muestra todos los datos que tiene la BD
def lista_mediciones(request):
    # Esta vista muestra una lista de todas las mediciones almacenadas en la base de datos  
    # Obtener todos los registros
    mediciones = Medicion.objects.all()
    return render(request, 'miappGraficacion/lista.html', {'mediciones': mediciones})
# Fin de funcion para mostrar todos los datos en la BD


# funcion para subir archivos CSV
def seleccion_csv(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Guardar el archivo en la carpeta de datos
            archivo = request.FILES['archivo_csv']
            ruta_destino = os.path.join(settings.BASE_DIR, 'miappGraficacion', 'static', 'miappGraficacion', 'data', archivo.name)
            
            with open(ruta_destino, 'wb+') as destino:
                for chunk in archivo.chunks():
                    destino.write(chunk)
            
            return redirect(reverse('graficas') + f'?archivo={archivo.name}')
    else:
        form = CSVUploadForm()
    
    # Listar archivos CSV existentes
    ruta_data = os.path.join(settings.BASE_DIR, 'miappGraficacion', 'static', 'miappGraficacion', 'data')
    archivos_existentes = []
    if os.path.exists(ruta_data):
        archivos_existentes = [f for f in os.listdir(ruta_data) if f.endswith('.csv')]
    
    return render(request, 'miappGraficacion/subir_csv.html', {
        'form': form,
        'archivos_existentes': archivos_existentes
    })
# fin de la funcion para subir archivos CSV


# Vista para graficas
def graficas(request):
    if request.method == 'GET' and 'archivo' in request.GET:
        archivo_seleccionado = request.GET['archivo']
        csv_path = os.path.join(os.path.dirname(__file__), 'static', 'miappGraficacion', 'data', archivo_seleccionado)
        
        # Verificar si el archivo existe
        if not os.path.exists(csv_path):
            return redirect('seleccion_csv')
        
        # Leer datos del CSV
        datos = {}
        with open(csv_path, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            campos = csv_reader.fieldnames
            
            for campo in campos:
                datos[campo] = []
            
            for row in csv_reader:
                for campo in campos:
                    try:
                        datos[campo].append(float(row[campo]))
                    except ValueError:
                        datos[campo].append(row[campo])
        
        graficas_base64 = {}
        df = pd.DataFrame(datos)
        num_filas = len(datos[campos[0]]) if campos else 0

        # Detección de valores altos (≥14)
        valores_alto = {}
        for campo in campos[1:]:  # Excluir la primera columna (eje X)
            if pd.api.types.is_numeric_dtype(df[campo]):
                valores_altos = [v for v in datos[campo] if isinstance(v, (int, float)) and v >= 14]
                if valores_altos:
                    valores_alto[campo] = {
                        'valores': valores_altos,
                        'maximo': max(valores_altos),
                        'minimo': min(valores_altos),
                        'cantidad': len(valores_altos)
                    }

        # =========================================================================
        # 1. GRÁFICA COMPARATIVA (CON MARCADORES PARA VALORES ALTOS)
        # =========================================================================
        if len(campos) > 1:
            plt.figure(figsize=(12, 6))
            
            # Paleta de colores
            colores = plt.cm.tab10.colors
            
            for i, campo in enumerate(campos[1:]):
                color = colores[i % len(colores)]
                
                # Línea principal
                plt.plot(datos[campos[0]], datos[campo], 
                         marker='o', markersize=4, 
                         linewidth=1, color=color,
                         alpha=0.7, label=campo)
                
                # Marcar valores ≥14
                if campo in valores_alto:
                    x_vals = []
                    y_vals = []
                    for x, y in zip(datos[campos[0]], datos[campo]):
                        if isinstance(y, (int, float)) and y >= 14:
                            x_vals.append(x)
                            y_vals.append(y)
                    
                    plt.scatter(x_vals, y_vals, s=100,
                               edgecolors='red', linewidths=1.5,
                               facecolors=color, alpha=0.8,
                               zorder=3, label=f'{campo} ≥14' if i == 0 else "")
            
            plt.title(f'Comparativa de Datos - {archivo_seleccionado}\n(Círculos rojos indican valores ≥14)')
            plt.xlabel(campos[0])
            plt.ylabel('Valores')
            
            # Mejorar leyenda
            handles, labels = plt.gca().get_legend_handles_labels()
            by_label = dict(zip(labels, handles))
            plt.legend(by_label.values(), by_label.keys(), loc='best')
            
            plt.grid(True, alpha=0.3)
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            buffer.seek(0)
            graficas_base64['comparativa'] = base64.b64encode(buffer.getvalue()).decode('utf-8')
            plt.close()

        # =========================================================================
        # 2. GRÁFICA DE BARRAS (DESTACAR VALORES ALTOS)
        # =========================================================================
        if len(campos) <= 6 and len(campos) > 1:
            plt.figure(figsize=(12, 6))
            width = 0.8 / (len(campos)-1)
            
            for i, campo in enumerate(campos[1:]):
                bars = plt.bar([x + i*width for x in range(len(datos[campos[0]]))], 
                              datos[campo], width=width, label=campo, alpha=0.7)
                
                if campo in valores_alto:
                    for j, val in enumerate(datos[campo]):
                        if val >= 14:
                            bars[j].set_edgecolor('red')
                            bars[j].set_linewidth(2)
                            bars[j].set_hatch('//')
                            bars[j].set_alpha(1.0)
            
            plt.title(f'Datos por {campos[0]} - {archivo_seleccionado}\n(Barras rayadas/rojas indican valores ≥14)')
            plt.xlabel(campos[0])
            plt.ylabel('Valores')
            plt.xticks([x + width*(len(campos)-2)/2 for x in range(len(datos[campos[0]]))], 
                      datos[campos[0]], rotation=45)
            plt.legend()
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=100)
            buffer.seek(0)
            graficas_base64['barras'] = base64.b64encode(buffer.getvalue()).decode('utf-8')
            plt.close()

        # =========================================================================
        # 3. GRÁFICAS INDIVIDUALES (CON MARCADORES PARA VALORES ALTOS)
        # =========================================================================
        if num_filas >= 50 and len(campos) > 1:
            for campo in campos[1:]:
                try:
                    plt.figure(figsize=(12, 6))
                    
                    # Línea principal
                    plt.plot(datos[campos[0]], datos[campo], 
                            marker='o' if num_filas < 100 else None,
                            markersize=4 if num_filas < 100 else 0,
                            linewidth=1, color='blue', alpha=0.7)
                    
                    # Marcar valores ≥14
                    if campo in valores_alto:
                        x_vals = []
                        y_vals = []
                        for x, y in zip(datos[campos[0]], datos[campo]):
                            if isinstance(y, (int, float)) and y >= 14:
                                x_vals.append(x)
                                y_vals.append(y)
                        
                        plt.scatter(x_vals, y_vals, s=100,
                                   edgecolors='red', linewidths=1.5,
                                   facecolors='blue', alpha=0.8,
                                   zorder=3)
                    
                    plt.title(f'Valores de {campo}\n{archivo_seleccionado}\n(Círculos rojos indican valores ≥14)')
                    plt.xlabel(campos[0])
                    plt.ylabel(campo)
                    plt.grid(True, alpha=0.3)
                    
                    if num_filas > 30:
                        plt.xticks(rotation=45)
                        locator = plt.MaxNLocator(nbins=10)
                        plt.gca().xaxis.set_major_locator(locator)
                    
                    buffer = BytesIO()
                    plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
                    buffer.seek(0)
                    graficas_base64[f'linea_{campo}'] = base64.b64encode(buffer.getvalue()).decode('utf-8')
                    plt.close()
                except Exception as e:
                    print(f"Error al graficar columna {campo}: {e}")

        # =========================================================================
        # 4. GRÁFICAS DE CALOR (HEATMAPS) - VERSIÓN MEJORADA
        # =========================================================================
        try:
            if len(campos) > 1 and num_filas > 0:
                numeric_cols = [campo for campo in campos if pd.api.types.is_numeric_dtype(df[campo])]
                
                if len(numeric_cols) > 1:
                    # Preparar datos para heatmap
                    heatmap_data = df[numeric_cols].corr()
                    
                    plt.figure(figsize=(10, 8))
                    sns.heatmap(heatmap_data, annot=True, cmap='coolwarm', center=0,
                               square=True, linewidths=1, cbar_kws={"shrink": 0.8})
                    
                    plt.title(f'Matriz de Correlación - {archivo_seleccionado}')
                    plt.tight_layout()
                    
                    buffer = BytesIO()
                    plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
                    buffer.seek(0)
                    graficas_base64['heatmap'] = base64.b64encode(buffer.getvalue()).decode('utf-8')
                    plt.close()
                    
                    # Heatmap de valores (si no son demasiados datos)
                    if num_filas <= 100 and len(numeric_cols) <= 10:
                        plt.figure(figsize=(12, 8))
                        sns.heatmap(df[numeric_cols].head(50).T, cmap='viridis', 
                                   annot=True if len(numeric_cols) <= 5 else False,
                                   linewidths=0.5)
                        plt.title(f'Valores de Sensores (Primeros 50 registros) - {archivo_seleccionado}')
                        plt.xlabel('Registro')
                        plt.ylabel('Sensor')
                        plt.tight_layout()
                        
                        buffer = BytesIO()
                        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
                        buffer.seek(0)
                        graficas_base64['heatmap_valores'] = base64.b64encode(buffer.getvalue()).decode('utf-8')
                        plt.close()
        except Exception as e:
            print(f"Error al generar heatmaps: {e}")

        # =========================================================================
        # PREPARAR DATOS PARA TEMPLATE
        # =========================================================================
        tabla_datos = []
        if datos and campos:
            sample_size = min(100, num_filas)
            if num_filas > 100:
                indices = random.sample(range(num_filas), sample_size)
            else:
                indices = range(num_filas)
            
            for i in indices:
                fila = {campo: datos[campo][i] for campo in campos}
                tabla_datos.append(fila)
        
        # Estadísticas resumen
        estadisticas = {}
        for campo in campos[1:]:
            if campo in numeric_cols:
                estadisticas[campo] = {
                    'min': min(datos[campo]),
                    'max': max(datos[campo]),
                    'promedio': sum(datos[campo]) / len(datos[campo]),
                    'valores_altos': len([v for v in datos[campo] if v >= 14]) if campo in valores_alto else 0
                }
        
        context = {
            'archivo': archivo_seleccionado,
            'campos': campos,
            'datos': datos,
            'tabla_datos': tabla_datos,
            'graficas': graficas_base64,
            'numeric_cols': numeric_cols,
            'num_filas': num_filas,
            'valores_alto': valores_alto,
            'hay_valores_altos': bool(valores_alto),
            'estadisticas': estadisticas
        }
        return render(request, 'miappGraficacion/graficas.html', context)
    
    return redirect('seleccion_csv')
# Fin de la vista de graficas


# vista para manejar datos enviados por arduino
@api_view(['POST'])
@csrf_exempt  # ⚠️ Desactiva CSRF (necesario para Arduino)
def recibir_datos_arduino(request):
    if request.method == 'POST':
        # Verificación opcional por dirección IP (si conoces tu IP pública fija)
        client_ip = request.META.get('REMOTE_ADDR')
        # Si quieres registrar las IPs que acceden (opcional)
        print(f"Petición recibida desde IP: {client_ip}")

        serializer = MedicionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
