# Reconstructing AudioSet Windows

This repository is a small pipeline for turning AudioSet metadata into local audio clips. You choose a sound label such as `Cough`; the code finds the matching YouTube IDs, downloads the sources that are still available, cuts the annotated time windows with FFmpeg, and saves the resulting MP3 segments locally.

The goal is to turn AudioSet's IDs and timestamps into a working set of audio I can inspect or prepare for later ML experiments. It does not train a model itself.

Here is one real row from the CSV:

```text
130v5XJl8G0 · 70→80 s
Cough | Speech | Child speech
             │
             ├── exact label filter: "Cough"
             ├── source still available? ── no → skipped
             └── yes → yt-dlp → audio/Cough_raw/130v5XJl8G0.mp3
                                      │ FFmpeg [70, 80]
                                      ↓
                  audio/Cough_cut/130v5XJl8G0_70_80_10.mp3
```

That row also shows the main catch: asking for `Cough` does not give you clips containing only coughs. AudioSet windows can have several labels and several sounds at once.

Only the metadata and code are tracked in Git. Downloaded audio stays local.

I kept the stack simple:

- `pandas` and Python's `json` module read the metadata, map ontology IDs to names, and filter rows by label;
- `yt-dlp` retrieves the best available audio stream from each source;
- `ffmpeg-python` calls the native FFmpeg executable to cut the requested `[start, end]` window;
- `tqdm` shows progress while the pipeline works through the selected rows; and
- `librosa`, NumPy, Matplotlib and Seaborn are used in the notebook for audio and metadata exploration.

## Try it

I used Conda because FFmpeg needs to be installed as a native executable, not only as a Python package.

```bash
conda env create -f main/environment.yml
conda activate ift6758-conda-env-2
cd main
```

From a Python shell or notebook opened inside `main/`:

```python
from q3 import data_pipeline, rename_files

data_pipeline("data/audio_segments_clean.csv", "Cough")
rename_files("audio/Cough_cut", "data/audio_segments_clean.csv")
```

I kept renaming as a separate step because the original exercise treated it as a post-processing pass.

```text
audio/
├── Cough_raw/    # audio extracted by yt-dlp
└── Cough_cut/    # requested time windows
    └── <YTID>_<rounded-start>_<rounded-end>_<duration>.mp3
```

The CSV is still the source of truth. Three rows have fractional timestamps: FFmpeg receives the exact values, while the filename uses rounded integers.

If you prefer pip, install `main/requirements.txt` and install FFmpeg separately through your operating system.

<details>
<summary>Using an authenticated source</summary>

Most public sources do not need authentication. If you are allowed to access a restricted source, pass a cookie export kept outside the repository:

```python
data_pipeline(
    "data/audio_segments_clean.csv",
    "Cough",
    cookiefile="/absolute/path/outside-this-repository/cookies.txt",
)
```

Do not commit browser cookies or downloaded media.

</details>

## What Git can—and cannot—keep

The metadata, ontology, label selection, requested interval and naming rule are all versioned here. YouTube availability is not. Neither are the exact MP3 bytes: the source, yt-dlp, FFmpeg and dependency versions can all change.

On a rerun, the pipeline skips raw or cut files that already exist. If a download fails, it does not try to cut the missing file and moves to the next row. Failures are not written to a report yet, so a folder of clips is not proof that every matching row succeeded.

## The snapshot I used

I worked with `audio_segments.csv`, a snapshot based on AudioSet's evaluation metadata. In the notebook, I map the ontology IDs to readable names, count the labels, and write `audio_segments_clean.csv`, which is the file the pipeline actually uses.

| Measurement | Value |
|---|---:|
| Annotation rows / unique YouTube IDs | 20,371 |
| Represented sound classes | 527 |
| Positive label assignments | 51,804 |
| Rows with several labels | 76.73% |
| Maximum labels on one row | 11 |
| Candidate rows for `Cough` / `Hammer` | 60 / 60 |

The number I find most useful is 76.73%. It makes the limitation concrete: this pipeline creates a label-selected working set, not a clean single-event dataset. Of the 60 `Cough` rows, 42 have several labels and 32 are also labelled `Speech`.

## Code and checks

The project is deliberately small:

```text
main/
├── q1.py                  # ontology mapping and label utilities
├── q2.py                  # yt-dlp download and FFmpeg cutting
├── q3.py                  # filtering, orchestration and filenames
├── visualize.ipynb       # metadata and audio exploration
├── tests/test_pipeline.py
└── data/                  # raw and enriched metadata
```

Run the tests from `main/`:

```bash
python -m unittest discover -s tests -v
```

I added six offline tests for existing-file skipping, external cookies, expected paths, reruns, and the rule that cutting must not run after a failed download. They replace yt-dlp and FFmpeg with test doubles, so they check my orchestration logic—not current YouTube availability or real audio output.

The current version is sequential and has no retries or failure report. It converts the best available source audio to 192-kbps MP3, but does not normalize the sample rate or channel count, validate the final duration, or guarantee bit-for-bit reproducibility.
