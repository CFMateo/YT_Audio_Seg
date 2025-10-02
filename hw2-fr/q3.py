import re
import os
import pandas as pd
from tqdm import tqdm
from q2 import download_audio, cut_audio
from typing import List

import json
from q1 import contains_label
from q2 import download_audio, cut_audio





def filter_df(csv_path: str, label: str) -> List[str]: #pd.DataFrame plutot nan 
    """
    Écrivez une fonction qui prend le path vers le csv traité (dans la partie notebook de q1) et renvoie un df avec seulement les rangées qui contiennent l'étiquette `label`.

    Par exemple:
    get_ids("audio_segments_clean.csv", "Speech") ne doit renvoyer que les lignes où l'un des libellés est "Speech"
    
    """
    
    data = pd.read_csv(csv_path)
    #return (contains_label(data['label_names'], label).to_frame()) # le frame permet de tranf la series en df
    filtrer = data["label_names"].apply(lambda el: label in el.split("|")) # donne une Series, l'unique colonne a sur chaque ligen soit True soit False.
    return data[filtrer].reset_index(drop=True) # retourne tte les lignes qui contiennent label dans leurs colonne label names 9tte celle qui etait marquer par true par le filtre)


    



def data_pipeline(csv_path: str, label: str) -> None:
    """
    En utilisant vos fonctions précédemment créées, écrivez une fonction qui prend un csv traité et pour chaque vidéo avec l'étiquette donnée:
    1. Le télécharge à <label>_raw/<ID>.mp3
    2. Le coupe au segment approprié
    3. L'enregistre dans <label>_cut/<ID>.mp3
    (n'oubliez pas de créer le dossier audio/ et le dossier label associé !).

    Il est recommandé d'itérer sur les rangées de filter_df().
    Utilisez tqdm pour suivre la progression du processus de téléchargement (https://tqdm.github.io/)

    Malheureusement, il est possible que certaines vidéos ne peuvent pas être téléchargées. Dans de tels cas, votre pipeline doit gérer l'échec en passant à la vidéo suivante avec l'étiquette.
    """
    '''
    df_filtrer = filter_df(csv_path,label)
    long = len(df_filtrer)
    df_filtrer["YTID"].apply(download_audio(sur lui,"/audio/<label>_raw/<ID>.mp3"))
    for i in range(0,long):
        cut_audio("/audio/<label>_raw/<ID>.mp3","/audio/<label>_cut/<ID>.mp3",df_filtrer['start_seconds'][i], df_filtrer['end_seconds'][i] )
    '''
    df_filtrer = filter_df(csv_path, label)
    

    # Dossiers de sortie, la ou on va stock les sorties
    raw_dir = os.path.join("audio", f"{label}_raw")
    cut_dir = os.path.join("audio", f"{label}_cut")
    os.makedirs(raw_dir, exist_ok=True) # cree juste si il n exsite pas
    os.makedirs(cut_dir, exist_ok=True)

    for index, row in tqdm(df_filtrer.iterrows(), total=len(df_filtrer)): #on itere sur index et row mais on a pas besoin d acceder a index
        try:
            ytid  = row["YTID"]
            start = float(row["start_seconds"])
            end   = float(row["end_seconds"])
            if end <= start:
                continue # gere le cas si erreur entre start et end

            raw_mp3 = os.path.join(raw_dir, f"{label}_raw_{ytid}")
            cut_mp3 = os.path.join(cut_dir, f"{label}_cut_{ytid}")

            # 1) Download (skip si présent)
            if not os.path.exists(raw_mp3):
                download_audio(ytid, raw_mp3)

            # 2) Cut (skip si présent)
            if (not os.path.exists(cut_mp3)) and (os.path.exists(raw_mp3)):
                cut_audio(raw_mp3, cut_mp3, start, end)
                
        except Exception as e:
            print(f"[ERREUR!!!! Avec:] YTID={row.get('YTID','?')}: {e}")
            continue

            



def rename_files(path_cut: str, csv_path: str) -> None:
    """
    Supposons que nous voulons maintenant renommer les fichiers que nous avons téléchargés dans `path_cut` pour inclure les heures de début et de fin ainsi que la longueur du segment. Alors que
    cela aurait pu être fait dans la fonction data_pipeline(), supposons que nous avons oublié et que nous ne voulons pas tout télécharger à nouveau.

    Écrivez une fonction qui, en utilisant regex (c'est-à-dire la bibliothèque `re`), renomme les fichiers existants de "<ID>.mp3" -> "<ID>_<start_seconds_int>_<end_seconds_int>_<length_int>.mp3"
    dans path_cut. csv_path est le chemin vers le csv traité à partir de q1. `path_cut` est un chemin vers le dossier avec l'audio coupé.

    Par exemple
    "--BfvyPmVMo.mp3" -> "--BfvyPmVMo_20_30_10.mp3"

    ## ATTENTION : supposez que l'YTID peut contenir des caractères spéciaux tels que '.' ou même '.mp3' ##
    """
    # TODO
    pass


if __name__ == "__main__":
    print(filter_df("data/audio_segments_clean.csv", "Laughter"))
    data_pipeline("data/audio_segments_clean.csv", "Laughter")
    rename_files("Laughter_cut", "audio_segments_clean.csv")
