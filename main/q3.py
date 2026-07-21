import re
import os
import pandas as pd
from pathlib import Path
from tqdm import tqdm
from q1 import contains_label
from q2 import download_audio, cut_audio
from typing import Optional


def _segment_filename(ytid: str, start: float, end: float) -> str:
    start_int = int(round(start))
    end_int = int(round(end))
    length_int = max(0, end_int - start_int)
    return f"{ytid}_{start_int}_{end_int}_{length_int}.mp3"





def filter_df(csv_path: str, label: str) -> pd.DataFrame:  #List[str]
    """
    Écrivez une fonction qui prend le path vers le csv traité (dans la partie notebook de q1) et renvoie un df avec seulement les rangées qui contiennent l'étiquette `label`.

    Par exemple:
    get_ids("audio_segments_clean.csv", "Speech") ne doit renvoyer que les lignes où l'un des libellés est "Speech"
    
    """
    data = pd.read_csv(csv_path)
    filtered_labels = contains_label(data["label_names"], label)
    return data[data["label_names"].isin(filtered_labels)] # is in retourne que les ligens qui contiennent l'arg



def data_pipeline(csv_path: str, label: str, cookiefile: Optional[str] = None) -> None:
    """
    En utilisant vos fonctions précédemment créées, écrivez une fonction qui prend un csv traité et pour chaque vidéo avec l'étiquette donnée:
    1. Le télécharge à <label>_raw/<ID>.mp3
    2. Le coupe au segment approprié
    3. L'enregistre dans <label>_cut/<ID>.mp3
    (n'oubliez pas de créer le dossier audio/ et le dossier label associé !).

    Il est recommandé d'itérer sur les rangées de filter_df().
    Utilisez tqdm pour suivre la progression du processus de téléchargement (https://tqdm.github.io/)

    Malheureusement, il est possible que certaines vidéos ne peuvent pas être téléchargées. Dans de tels cas, votre pipeline doit gérer l'échec en passant à la vidéo suivante avec l'étiquette.

    cookiefile est facultatif et doit désigner un fichier conservé hors du dépôt.
    """
    if cookiefile is not None:
        cookie_path = Path(cookiefile).expanduser()
        if not cookie_path.is_file():
            raise FileNotFoundError(f"Cookie file not found: {cookie_path}")
        cookiefile = str(cookie_path)

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

            raw_stem = os.path.join(raw_dir, ytid)
            cut_stem = os.path.join(cut_dir, ytid)
            raw_mp3 = f"{raw_stem}.mp3"
            cut_mp3 = f"{cut_stem}.mp3"
            renamed_cut_mp3 = os.path.join(
                cut_dir, _segment_filename(ytid, start, end)
            )

            if os.path.exists(cut_mp3) or os.path.exists(renamed_cut_mp3):
                continue

            #  download (skip si présent)
            if not os.path.exists(raw_mp3):
                download_audio(ytid, raw_stem, cookiefile=cookiefile)

            if not os.path.exists(raw_mp3):
                continue

            cut_audio(raw_mp3, cut_mp3, start, end)
            """
            if index == 0:
                print("CWD:", os.getcwd())
                print("raw_mp3:", raw_mp3, "exists?", os.path.exists(raw_mp3))
                print("cut_mp3:", cut_mp3, "exists?", os.path.exists(cut_mp3))
            """

                
        except Exception as e:
            continue

            

def rename_files(path_cut: str, csv_path: str) -> None:
    """
    Supposons que nous voulons maintenant renommer les fichiers que nous avons téléchargés dans `path_cut` pour inclure les heures de début et de fin ainsi que la longueur du segment. Alors que
    cela aurait pu être fait dans la fonction data_pipeline(), supposons que nous avons oublié et que nous ne voulons pas tout télécharger à nouveau.

    Écrivez une fonction qui, en utilisant regex (c'est-à-dire la bibliothèque `re`), renomme les fichiers existants de "<ID>.mp3" -> "<ID>_<start_seconds_int>_<end_seconds_int>_<length_int>.mp3"
    dans path_cut. csv_path est le chemin vers le csv traité à partir de q1. `path_cut` est un chemin vers le dossier avec l'audio coupé.

    Par exemple
    "--BfvyPmVMo.mp3" -> "--BfvyPmVMo_20_30_10.mp3"

    ## ATTENTION: supposez que l'YTID peut contenir des caractères spéciaux tels que'.' ou même '.mp3' ##
    """
    if not os.path.isdir(path_cut):
        return

    #  Lecture unique + normalisation d’en-têtes
    df = pd.read_csv(csv_path)
    df.columns = [re.sub(r'^[#\s]+', '', c).strip() for c in df.columns]
    #  variantes fréquentes
    df = df.rename(columns={
        'startseconds': 'start_seconds',
        'endseconds': 'end_seconds'
    })

    required = {'YTID', 'start_seconds', 'end_seconds'}
    if not required.issubset(df.columns):
        return  # rien à faire si les colonnes clés manquent

    
    df['start_int']  = df['start_seconds'].round().astype(int)
    df['end_int']    = df['end_seconds'].round().astype(int)
    df['length_int'] = (df['end_int'] - df['start_int']).clip(lower=0)

    info = df.set_index('YTID')[['start_int','end_int','length_int']].to_dict('index')

    # cas part
    for fname in os.listdir(path_cut):
        if not fname.endswith('.mp3'):
            continue
        ytid = re.sub(r'\.mp3$', '', fname)  

        meta = info.get(ytid)
        if not meta:
            continue  # pas dans le CSV, juste ignore

        new_name = _segment_filename(ytid, meta['start_int'], meta['end_int'])
        old_path = os.path.join(path_cut, fname)
        new_path = os.path.join(path_cut, new_name)

        if old_path == new_path or os.path.exists(new_path):
            continue  # idempotent: ne supprime rien
        os.rename(old_path, new_path)

"""
if __name__ == "__main__":
    print(filter_df("data/audio_segments_clean.csv", "Laughter"))
    #data_pipeline("data/audio_segments_clean.csv", "Laughter")
    rename_files("audio/Laughter_cut", "data/audio_segments_clean.csv")
"""
