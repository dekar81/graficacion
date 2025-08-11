from django import forms

class CSVUploadForm(forms.Form):
    archivo_csv = forms.FileField(
        label='Selecciona un archivo CSV',
        help_text='El archivo debe tener encabezados en la primera fila',
        widget=forms.FileInput(attrs={'accept': '.csv'})
    )