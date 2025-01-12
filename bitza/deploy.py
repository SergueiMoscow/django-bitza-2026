import os
import subprocess


def run_deploy_script_():
    try:
        # Запуск deploy.sh как отдельного процесса
        subprocess.Popen(
            ['./deploy.sh'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid
        )
        return True, "Deploy script started successfully."
    except Exception as e:
        return False, str(e)


def run_deploy_script():
   try:
       with open('deploy.log', 'a') as log_file:
           subprocess.Popen(
               ['./deploy.sh'],
               stdout=log_file,
               stderr=log_file,
               preexec_fn=os.setsid  # Для Unix-систем
           )
       return True, "Deploy script started successfully."
   except Exception as e:
       return False, str(e)
