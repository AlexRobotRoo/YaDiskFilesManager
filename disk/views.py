import requests
from django.shortcuts import render
from django.http import HttpResponse
from typing import List, Dict
from urllib.parse import quote_plus, unquote_plus
import io
import zipfile

# Получение списка файлов с ЯД
def get_files(public_key: str) -> List[Dict]:
    url = f"https://cloud-api.yandex.net/v1/disk/public/resources?public_key={public_key}"
    response = requests.get(url)
    
    if response.status_code == 200:
        items = response.json()['_embedded']['items']
        return items
    else:
        return []

# Отображение списка файлов и ссылок для скачивания каждого файла
def show_files(request):
    public_key = request.GET.get('public_key')

    files = []
    if public_key:
        files = get_files(public_key)

        for file in files:
            file_path = file['path']
            direct_download_url = get_direct_download_url(public_key, file_path)
            if direct_download_url:
                file['download_url'] = direct_download_url
            else:
                file['download_url'] = None

    return render(request, 'disk/list_files.html', {'files': files, 'public_key': public_key})

# Получаем ссылку на скачивание файла от Yandex Disk API
def get_direct_download_url(public_key, file_path):
    api_url = f"https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key={public_key}&path={quote_plus(file_path)}"
    response = requests.get(api_url)

    if response.status_code == 200:
        return response.json().get('href')
    return None

# Функция для скачивания конкретного файла
def download_file(request, public_key, path):
    direct_download_url = get_direct_download_url(public_key, path)

    if direct_download_url:
        return HttpResponseRedirect(direct_download_url)

    return HttpResponse("Не удалось получить ссылку на скачивание", status=404)


# Функция для скачивания нескольких файлов одновременно
def download_selected_files(request):
    public_key = request.POST.get('public_key')
    selected_files = request.POST.getlist('selected_files')

    if not selected_files:
        return HttpResponse("Файлы для скачивания не выбраны.", status=400)

    zip_buffer = io.BytesIO() # Создаем файл архива, в который будут помещаться все выбранные для скачивания файлы
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for file_path in selected_files:
            direct_download_url = get_direct_download_url(public_key, file_path)
            if direct_download_url:
                file_response = requests.get(direct_download_url) # Получаем файл по ссылке
                if file_response.status_code == 200:
                    file_name = file_path.split('/')[-1]
                    zip_file.writestr(file_name, file_response.content) # Добавляем файл в архив

    zip_buffer.seek(0)# Устанавливаем курсор в начало буфера BytesIO

    response = HttpResponse(zip_buffer, content_type='application/zip') # Создаем response и прикрепляем к нему архив с выбранными файлами
    response['Content-Disposition'] = 'attachment; filename="selected_files.zip"'

    return response