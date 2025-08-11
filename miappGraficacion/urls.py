from django.urls import path
from . import views
from .views import MedicionListView
from .views import recibir_datos_arduino
urlpatterns = [
    path('', views.home, name='home'),
    path('seleccion/', views.seleccion_csv, name='seleccion_csv'),
    path('graficas/', views.graficas, name='graficas'), # vista que muestra las graficas
    path('lista/', views.lista_mediciones, name='lista_mediciones'),# Lista de mediciones
    path('importar/', views.import_csv, name='import_csv'), # Importar CSV a la base de datos
    path('subir_archivos', views.seleccion_csv, name='seleccion_csv'), # vista para subir archivos
    path('mediciones/', MedicionListView.as_view(), name='medicion-list'), #vista de consulta de mediciones
     path('api/medicion/', recibir_datos_arduino, name='recibir_datos_arduino'), # API para recibir datos de Arduino     
]
