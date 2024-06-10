"""
This is the main file for the dub editor. It uses the bottle framework to serve the web app.

After running this file, you can access the dub editor at http://localhost:8080/
"""
import os

import pydub
from bottle import route, request, static_file, run, abort

from locations import VOICES_DIR, DUBS_FILE_PATH, USED_DUBS_FILE_PATH

ROOT = "dub_editor/"

@route('/')
def root():
    return static_file('index.html', root=ROOT)

@route("/<filepath:re:.*\.js>")
def js(filepath):
    return static_file(filepath, root=ROOT)

@route('/voices')
def voices():
    folders = os.listdir(VOICES_DIR)
    return {'voices': folders}

@route('/new/voice/<name>')
def new_voice(name):
    path = f'{VOICES_DIR}{name}'
    if os.path.exists(path):
        return {'success': False}
    os.makedirs(path)
    return {'success': os.path.exists(path)}

@route('/delete/voice/<name>')
def delete_voice(name):
    path = f'{VOICES_DIR}{name}'
    if not os.path.exists(path):
        return {'success': False}
    # TODO: delete all files too with os.remove(path) and os.listdir()
    try:
        os.rmdir(path)
        return {'success': True}
    except Exception as e:
        return {"success": False, "message": str(e)}

@route('/dubs/<name>')
def voice_dubs(name):
    path = f'{VOICES_DIR}{name}/'
    if not os.path.exists(path):
        return {'dubs': [], 'voice': name, 'found': False}
    dubs = os.listdir(path)
    return {'dubs': dubs, 'voice': name, 'found': True}

@route('/dubs/')
def dubs():
    return static_file(DUBS_FILE_PATH, root='.')

@route('/usage/')
def usage():
    return static_file(USED_DUBS_FILE_PATH, root='.')

@route('/audio/<voice>/<code>')
def audio(voice, code):
    path = os.path.join(VOICES_DIR, voice, code+'.mp3')
    if not os.path.exists(path):
        abort(400, f'Voice {voice} does not have code {code}')
    return static_file(path, root='.')

@route('/delete/<voice>/<code>')
def audio(voice, code):
    path = os.path.join(VOICES_DIR, voice, code+'.mp3')
    if not os.path.exists(path):
        abort(400, f'Voice {voice} does not have code {code}')
    os.remove(path)
    return "File deleted successfully"

@route('/upload', method='POST')
def do_upload():
    voice = request.forms.get('voice')
    code = request.forms.get('code')
    upload = request.files.get('upload')
    name, ext = os.path.splitext(upload.filename)
    if ext not in ('.wav', '.mp3'):
        return {"success": False, "message": "File extension not allowed."}

    save_path = f"{VOICES_DIR}{voice}"
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    
    try:
        print(upload.file)
        sound = pydub.AudioSegment.from_file(upload.file)
    except Exception as e:
        return {"success": False, "message": f"File failed to convert:\n"+str(e)}
    
    file_path = f"{save_path}/{code}.mp3"
    sound.export(file_path, format="mp3")
    #upload.save(file_path)
    return {"success": True, "message": f"File successfully saved to '{save_path}'.", 
            "url": f"/audio/{voice}/{code}"}

if __name__ == '__main__':
    run(host='localhost', port=8080, reloader=True)
