import requests
import os

def download_file(url, folder):
    local_filename = os.path.join(folder, url.split('/')[-1])
    print(f"Downloading {url} to {local_filename}...")
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename

if __name__ == "__main__":
    audio_url = "https://groups.inf.ed.ac.uk/ami/AMICorpusMirror/amicorpus/ES2002a/audio/ES2002a.Headset-0.wav"
    transcript_url = "https://groups.inf.ed.ac.uk/ami/AMICorpusMirror/amicorpus/ES2002a/browsable/ES2002a.Transcript.html"
    
    audio_folder = r"f:\LiveMeetingAnalyzerProject\audio"
    os.makedirs(audio_folder, exist_ok=True)
    
    download_file(audio_url, audio_folder)
    download_file(transcript_url, audio_folder)
    print("Download complete.")
