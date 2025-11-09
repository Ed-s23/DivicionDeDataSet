from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from .division_dataset import main  # tu función de procesamiento
import os

def home(request):
    resultado = None
    if request.method == "POST" and request.FILES.get('dataset'):
        dataset_file = request.FILES['dataset']
        fs = FileSystemStorage(location='media/')  # carpeta donde se guardará temporalmente
        filename = fs.save(dataset_file.name, dataset_file)
        uploaded_file_path = fs.path(filename)

        # Llama a tu función principal pasando la ruta del archivo subido
        try:
            resultado = main(uploaded_file_path)
        except Exception as e:
            resultado = f"Error procesando el dataset: {e}"

        # Elimina el archivo después de procesarlo (opcional)
        if os.path.exists(uploaded_file_path):
            os.remove(uploaded_file_path)

    return render(request, 'home.html', {'resultado': resultado})
