from flask import Flask, jsonify, request, send_file
import yt_dlp
import os

app = Flask(__name__)

TEMP_FOLDER = '/tmp'  # Carpeta temporal válida en Render, Azure, etc.

@app.route('/download/audio', methods=['POST'])
def download_audio():
    data = request.get_json()
    url = data.get('url')
    custom_name = data.get('name', 'audio')

    if not url:
        return jsonify({'error': 'Falta la URL'}), 400

    # Obtener cookies desde variable de entorno
    cookies_txt = os.environ.get('YOUTUBE_COOKIES_TXT')
    if not cookies_txt:
        return jsonify({'error': 'No se encontraron las cookies configuradas en el servidor'}), 500

    # Definir path para archivo temporal de cookies
    cookie_path = os.path.join(TEMP_FOLDER, 'cookies.txt')

    try:
        if not os.path.exists(TEMP_FOLDER):
            os.makedirs(TEMP_FOLDER)

        # Guardar cookies en archivo temporal (sobreescribe si existe)
        with open(cookie_path, 'w') as f:
            f.write(cookies_txt)

        # Template para archivo de salida
        output_template = os.path.join(TEMP_FOLDER, f'{custom_name}.%(ext)s')

        ydl_opts = {
            'outtmpl': output_template,
            'format': 'bestaudio[ext=m4a]/bestaudio',
            'quiet': True,
            'cookiefile': cookie_path,  # Usar archivo de cookies
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)

        # Eliminar el archivo de cookies inmediatamente para mayor seguridad
        os.remove(cookie_path)

        # Ruta final del audio descargado
        filename = os.path.join(TEMP_FOLDER, f'{custom_name}.m4a')
        if os.path.exists(filename):
            return send_file(filename, as_attachment=True)

        return jsonify({'error': 'No se pudo descargar el audio'}), 500

    except Exception as e:
        # En caso de error, también asegurarse de borrar el archivo cookies
        if os.path.exists(cookie_path):
            os.remove(cookie_path)
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
    app.run(debug=False, host='0.0.0.0', port=port)
