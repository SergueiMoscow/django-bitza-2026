"""
Разовый скрипт: переносит существующие файлы документов клиентов в S3 (Selectel),
под теми же ключами, что уже хранятся в rent_document.image_file — чтобы не трогать БД.

Файлы ищутся по basename среди локальных копий (django-bitza/documents/,
django-bitza/documents/documents/) — на этой машине есть не все файлы, для отсутствующих
пишется отчёт.

Запуск: poetry run python manage.py shell < migrate_documents_to_s3.py
"""
import os
from pathlib import Path

from django.core.files.base import File

from rent.models import Document
from rent.storage_backends import DocumentStorage

OLD_DOCUMENTS_ROOTS = [
    Path('/home/sergey/Projects/Bitza/django-bitza/documents'),
    Path('/home/sergey/Projects/Bitza/django-bitza/documents/documents'),
]

REPORT_PATH = Path('/home/sergey/Projects/Bitza/MISSING_CLIENT_DOCUMENTS.md')

local_files_by_basename = {}
for root in OLD_DOCUMENTS_ROOTS:
    if not root.exists():
        continue
    for f in root.iterdir():
        if f.is_file():
            local_files_by_basename[f.name] = f

storage = DocumentStorage()

uploaded = []
missing = []

for doc in Document.objects.select_related('contact').order_by('id'):
    key = doc.image_file.name
    basename = os.path.basename(key)
    local_path = local_files_by_basename.get(basename)
    contact = doc.contact
    contact_name = f'{contact.surname or ""} {contact.name or ""}'.strip() if contact else '—'

    if local_path is None:
        missing.append((doc.id, key, contact_name, doc.description or ''))
        continue

    with open(local_path, 'rb') as fh:
        # save() сохранит РОВНО под этим key, т.к. в бакете его ещё нет (file_overwrite=False
        # только защищает от случайной перезаписи уже существующего файла).
        saved_name = storage.save(key, File(fh))
    uploaded.append((doc.id, key, saved_name))
    if saved_name != key:
        print(f'ВНИМАНИЕ: doc {doc.id} сохранён под другим именем: {key} -> {saved_name} '
              f'(похоже, в бакете уже что-то есть по этому пути)')

print(f'\nЗагружено: {len(uploaded)}')
print(f'Не найдено локально: {len(missing)}')

with open(REPORT_PATH, 'w') as f:
    f.write('# Недостающие документы клиентов\n\n')
    f.write(
        f'Эти {len(missing)} записей в БД (`rent_document`) ссылаются на файлы, которых нет '
        f'на этой машине — не перенесены в S3. Если найдёшь оригиналы (на проде, в бэкапе, '
        f'где-то ещё) — пришли, перенесём. Если файлы безвозвратно потеряны — удалим сами '
        f'записи (или оставим как есть, если история важнее файла).\n\n'
    )
    f.write('| id | путь в БД (image_file) | клиент | описание |\n')
    f.write('|----|----|----|----|\n')
    for doc_id, key, contact_name, description in missing:
        f.write(f'| {doc_id} | `{key}` | {contact_name} | {description} |\n')

print(f'Отчёт по недостающим: {REPORT_PATH}')
