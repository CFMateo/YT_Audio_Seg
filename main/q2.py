
import ffmpeg
import pandas as pd
import numpy as np
import csv
import threading
from tqdm import tqdm
from os.path import exists

import yt_dlp as youtube_dl



def download_audio(YTID: str, path: str) -> None:
    """
    Créez une fonction qui télécharge l'audio de la vidéo Youtube avec un identifiant donné
    et l'enregistre dans le dossier donné par `path`. Téléchargez-le en mp3. S'il y a un problème lors du téléchargement du fichier, gérez l'exception. Si il y a déjà un fichier à `path`, la fonction devrait retourner sans tenter de le télécharger à nouveau.

    ** Utilisez la librairie youtube_dl : https://github.com/ytdl-org/youtube-dl/ **
    
    Arguments:
    - YTID: Contient l'identifiant youtube, la vidéo youtube correspondante peut être trouvée sur
    'https://www.youtube.com/watch?v='+YTID
    - path: Le chemin d'accès au fichier où l'audio sera enregistré
    """
    if exists(path):
        return   # on sort direct

    ydl_opts = {
        "quiet": True,
        'no_warnings': True,
        'format': 'bestaudio/best',
        'outtmpl': path,
        "cookiefile": "cookies.txt",
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
         "ignoreerrors": True,
    }

    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"https://www.youtube.com/watch?v={YTID}"])
    except Exception as e:
        return






def cut_audio(in_path: str, out_path: str, start: float, end: float) -> None:
    """
    Créez une fonction qui coupe l'audio de in_path pour n'inclure que le segment de start à end et l'enregistre dans out_path.

    ** Utilisez la bibliothèque ffmpeg: https://github.com/kkroening/ffmpeg-python
    Arguments:
    - in_path: Chemin du fichier audio à couper
    - out_path: Chemin du fichier pour enregistrer l'audio coupé
    - start : Indique le début de la séquence (en secondes)
    - end : Indique la fin de la séquence (en secondes)
    """
    ffmpeg.input(in_path, ss=start, t=(end-start)).output(out_path).run(overwrite_output=True)

import os
if __name__== '__main__':
    print("CWD:", os.getcwd())

    download_audio("-1LQP2wemiQ", "TEST_RAW")
    print("raw exists?", os.path.exists("TEST_RAW"))


    cut_audio("TEST_RAW.mp3","TEST_CUT.mp3",5, 10)
    print("cut exists?", os.path.exists("TEST_CUT"))






