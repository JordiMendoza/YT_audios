from flask import Flask, jsonify, request, send_file
import yt_dlp
import os
import shutil

app = Flask(__name__)

@app.route('/download/audio', methods=['POST'])
def download_audio():
    data = request.get_json()
    url = data.get('url')
    custom_name = data.get('name', 'audio')

    if not url:
        return jsonify({'error': 'Falta la URL'}), 400

    try:
        ydl_opts = {
            'outtmpl': f'downloads/{custom_name}.%(ext)s',
            'format': 'bestaudio[ext=m4a]/bestaudio',
            'quiet': True,
        }

        if not os.path.exists('downloads'):
            os.makedirs('downloads')

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

            filename = f'downloads/{custom_name}.m4a'

            if os.path.exists(filename):
                return send_file(filename, as_attachment=True)

            return jsonify({'error': 'No se pudo descargar el audio'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 🔥 Endpddddoint para eliminar todo el contenido de /downloads
@app.route('/delete/downloads', methods=['DELETE'])
def delete_downloads():
    try:
        folder = 'downloads'

        if not os.path.exists(folder):
            return jsonify({'message': 'La carpeta ya está vacía o no existe.'}), 200

        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)

        return jsonify({'message': 'Todos los archivos en "downloads/" fueron eliminados.'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
