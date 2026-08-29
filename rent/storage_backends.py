import certifi
from django.conf import settings
from storages.backends.s3 import S3Storage


class DocumentStorage(S3Storage):
    """
    Приватное S3-хранилище (Selectel) для копий документов клиентов.
    Объекты не публичные — url() отдаёт подписанную ссылку с ограниченным сроком жизни
    (querystring_auth=True, значение по умолчанию в django-storages), просмотр по прямой
    ссылке без подписи невозможен.
    """
    bucket_name = settings.S3_BUCKET
    endpoint_url = settings.S3_ENDPOINT_URL
    access_key = settings.S3_ACCESS_KEY
    secret_key = settings.S3_SECRET_KEY
    region_name = settings.S3_REGION
    default_acl = 'private'
    querystring_auth = True
    querystring_expire = 3600
    file_overwrite = False
    addressing_style = 'path'
    # location не задаём — upload_to='documents' на самом поле уже определяет префикс.
    # У botocore устаревший встроенный CA-бандл, не знающий актуальный корень Selectel —
    # явно используем certifi вместо системного/встроенного.
    verify = certifi.where()
