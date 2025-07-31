from flask import Flask, jsonify, request, send_file
import yt_dlp
import os

app = Flask(__name__)

TEMP_FOLDER = '/tmp'  # Carpeta válida en Render

@app.route('/download/audio', methods=['POST'])
def download_audio():
    data = request.get_json()
    url = data.get('url')
    custom_name = data.get('name', 'audio')

    if not url:
        return jsonify({'error': 'Falta la URL'}), 400

    try:
        # Asegurar que la carpeta /tmp existe (Render la provee, pero es buena práctica)
        if not os.path.exists(TEMP_FOLDER):
            os.makedirs(TEMP_FOLDER)

        output_template = os.path.join(TEMP_FOLDER, f'{custom_name}.%(ext)s')

        ydl_opts = {
            'outtmpl': output_template,
            'format': 'bestaudio[ext=m4a]/bestaudio',
            'quiet': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        # Buscar el archivo resultante
        filename = os.path.join(TEMP_FOLDER, f'{custom_name}.m4a')
        if os.path.exists(filename):
            return send_file(filename, as_attachment=True)

        return jsonify({'error': 'No se pudo descargar el audio'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/delete/downloads', methods=['DELETE'])
def delete_downloads():
    try:
        if not os.path.exists(TEMP_FOLDER):
            return jsonify({'message': 'La carpeta ya está vacía o no existe.'}), 200

        deleted = 0
        for filename in os.listdir(TEMP_FOLDER):
            file_path = os.path.join(TEMP_FOLDER, filename)
            if os.path.isfile(file_path) and filename.endswith('.m4a'):
                os.remove(file_path)
                deleted += 1

        return jsonify({'message': f'Se eliminaron {deleted} archivos en /tmp.'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
