from flask import Flask, send_from_directory, jsonify, request, Response
import subprocess
import os
import re
import paramiko
import time

app = Flask(__name__, static_folder='web')
BASE_DOWNLOAD_FOLDER = '/app/downloads'
AUDIO_DOWNLOAD_PATH = os.getenv('AUDIO_DOWNLOAD_PATH', BASE_DOWNLOAD_FOLDER)

# SSH TOUCH NEW VERSION - This part is for Synology Drive or other software that needs a touch to sync the file
SSH_ENABLED = os.getenv('SSH_ENABLED', 'false')
SSH_HOST = os.getenv('SSH_HOST')
SSH_USER = os.getenv('SSH_USER')
SSH_PASS = os.getenv('SSH_PASS')


os.makedirs(BASE_DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

@app.route('/download')
def download_media():
    spotify_link = request.args.get('spotify_link')
    if not spotify_link:
        return jsonify({"status": "error", "output": "No link provided"}), 400


    download_folder = os.path.join(AUDIO_DOWNLOAD_PATH)
    os.makedirs(AUDIO_DOWNLOAD_PATH, exist_ok=True)

    # Définir la commande en fonction du type de lien
    if "spotify" in spotify_link:
        command = [
            'spotdl',
            '--output', f"{download_folder}/{{artist}} - {{title}}.{{output-ext}}",
            spotify_link
        ]
    else:
        command = [
            'yt-dlp', '-x', '--audio-format', 'mp3',
            '-o', f"{download_folder}/%(uploader)s - %(title)s.%(ext)s",
            spotify_link
        ]


    return Response(generate(command, download_folder), mimetype='text/event-stream')


def touch_via_ssh(file_path):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connexion SSH au NAS
        ssh.connect(SSH_HOST, port=22, username=SSH_USER, password=SSH_PASS)

        # Générer la date actuelle au format touch (YYYYMMDDHHMM.SS)
        current_time = time.strftime("%Y%m%d%H%M.%S", time.localtime())

        # Exécuter la commande touch directement sur le NAS
        cmd = f'touch -c -t {current_time} "{file_path}"'
        stdin, stdout, stderr = ssh.exec_command(cmd)

        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()
        ssh.close()

        if error:
            print(f"❌ Erreur SSH: {error}")
        else:
            print(f"✅ Commande SSH exécutée avec succès: {cmd}")

    except Exception as e:
        print(f"❌ Erreur de connexion SSH: {e}")

def get_version():
    try:
        with open("VERSION", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "unknown"

def generate(command, download_folder):
    album_name = None  # Pour récupérer le nom de l'album ou de la playlist
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        for line in process.stdout:
            yield f"data: {line.strip()}\n\n"

            # Recherche du nom d'album/playlist dans la sortie de spotdl
            match = re.search(r'Found \d+ songs in (.+?) \(', line)
            if match:
                album_name = match.group(1).strip()
            
        process.stdout.close()
        process.wait()

        if process.returncode == 0:
            # Récupération des UID et GID depuis les variables d'environnement, avec des valeurs par défaut au besoin
            target_uid = int(os.environ.get("USER_ID", "1000"))
            target_gid = int(os.environ.get("GROUP_USER_ID", "1000"))

            downloaded_files = [f for f in os.listdir(download_folder) if os.path.isfile(os.path.join(download_folder, f))]
            if downloaded_files:
                latest_file = max(downloaded_files, key=lambda f: os.path.getctime(os.path.join(download_folder, f)))
                latest_file_path = os.path.join(download_folder, latest_file)
                os.chown(latest_file_path, target_uid, target_gid)

                # Si l'utilisateur a besoin qu'on fasse un touch sur le fichier pour le synchro avec Synology Drive ou autre.
                if SSH_ENABLED == 'true':
                    touch_via_ssh(latest_file_path)
                    


            # Pour admin, on ne fait pas de zip, ni de suppression automatique
            yield "data: Download completed. Files saved to server directory .\n\n"
        else:
            yield f"data: Error: Download exited with code {process.returncode}.\n\n"

    except Exception as e:
        yield f"data: Error: {str(e)}\n\n"

@app.route('/version')
def version():
    return jsonify({"version": get_version()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)