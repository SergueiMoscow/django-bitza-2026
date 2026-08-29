from django.http import HttpResponse

from bitza.deploy import run_deploy_script


def deploy(request):
    if request.headers['deploy_token']:
        run_deploy_script()
        return HttpResponse('Script run')
    return HttpResponse('Ok')
