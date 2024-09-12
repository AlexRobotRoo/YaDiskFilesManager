import requests
from django.shortcuts import render
from django.http import HttpResponse
from typing import List, Dict

# Получение списка файлов с ЯД
def get_files(public_key: str) -> List[Dict]:
    url = f"https://cloud-api.yandex.net/v1/disk/public/resources?public_key={public_key}"
    response = requests.get(url)
    
    if response.status_code == 200:
        items = response.json()['_embedded']['items']
        return items
    else:
        return []

# Отображение списка файлов
def show_files(request):
    public_key = request.GET.get('public_key')
    files = []
    
    if public_key:
        files = get_files(public_key)

    return render(request, 'disk/list_files.html', {'files': files})