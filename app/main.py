from flask import Flask, send_from_directory, jsonify, request, Response
import subprocess
import os
import re

app = Flask(__name__, static_folder='web')
BASE_DOWNLOAD_FOLDER = '/app/downloads'
AUDIO_DOWNLOAD_PATH = os.getenv('AUDIO_DOWNLOAD_PATH', BASE_DOWNLOAD_FOLDER)

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

                subprocess.run(["touch", latest_file_path])
                    


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