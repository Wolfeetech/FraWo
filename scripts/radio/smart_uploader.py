import os
import shutil
import time
import requests
import mutagen
from pathlib import Path
from dotenv import load_dotenv

# Konfiguration
ENV_PATH = Path.home() / '.ai-tools-shared' / '.env'
load_dotenv(ENV_PATH)

API_KEY = os.getenv('AZURACAST_API_KEY', 'b9a8e51be992498c:c55ea5c67b8ff16bffbed39004b056b1')
BASE_URL = os.getenv('AZURACAST_URL', 'https://funk.frawo-tech.de')
STATION_ID = 1

SOURCE_DIR = Path(r"C:\Users\StudioPC\Music\Sorted\_Sorted")
DONE_DIR = Path(r"C:\Users\StudioPC\Music\Sorted\_Uploaded")

HEADERS = {"X-API-Key": API_KEY}

def get_genre(file_path):
    """Extrahiert das Genre aus einer Audiodatei via Mutagen."""
    try:
        audio = mutagen.File(file_path, easy=True)
        if audio and 'genre' in audio:
            # Manchmal ist es eine Liste
            genre = audio['genre'][0] if isinstance(audio['genre'], list) else audio['genre']
            return str(genre).lower()
    except Exception as e:
        print(f"Warnung: Konnte Genre für {file_path.name} nicht lesen: {e}")
    return "unknown"

def determine_target_folder(genre):
    """
    Entscheidungs-Logik: 
    Je nach Genre (und später evtl. BPM) wird der AzuraCast-Ordner festgelegt.
    """
    genre = genre.lower()
    
    # Beispiel-Regelwerk - kann beliebig erweitert werden
    nightshift_genres = ['techno', 'house', 'tech house', 'deep house', 'electronic', 'acid']
    primetime_genres = ['disco', 'funk', 'pop', 'indie dance', 'nu disco']
    
    if any(g in genre for g in nightshift_genres):
        return "Nightshift"
    elif any(g in genre for g in primetime_genres):
        return "Primetime"
    else:
        return "Main_Rotation"

def upload_to_azuracast(file_path, target_folder):
    """Lädt die Datei über die REST-API in den angegebenen Ordner hoch."""
    url = f"{BASE_URL}/api/station/{STATION_ID}/files"
    
    # Der Ordnerpfad in AzuraCast (muss ggf. vorher manuell in AzuraCast existieren!)
    print(f"Lade '{file_path.name}' in den AzuraCast-Ordner '{target_folder}' hoch...")
    
    with open(file_path, 'rb') as f:
        files = {
            'file': (file_path.name, f, 'audio/mpeg' if file_path.suffix.lower() == '.mp3' else 'audio/flac')
        }
        data = {
            'path': target_folder
        }
        
        response = requests.post(url, headers=HEADERS, data=data, files=files, timeout=600)
        
        if response.status_code in [200, 201]:
            print(f"  -> Upload erfolgreich!")
            return True
        else:
            print(f"  -> Upload fehlgeschlagen: {response.status_code} - {response.text}")
            return False

def main():
    print("=== FraWo Funk Smart Uploader gestartet ===")
    
    # Sicherstellen, dass Ordner existieren
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    DONE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Finde alle Audio-Dateien im Quell-Ordner
    audio_files = []
    for ext in ['.mp3', '.flac', '.wav', '.aac']:
        audio_files.extend(SOURCE_DIR.rglob(f"*{ext}"))
        
    if not audio_files:
        print(f"Keine Dateien im Ordner {SOURCE_DIR} gefunden. Warte auf neue Lieder...")
        return

    print(f"{len(audio_files)} Dateien zur Verarbeitung gefunden.\n")
    
    for file_path in audio_files:
        print(f"Verarbeite: {file_path.name}")
        
        # 1. Metadaten lesen & Entscheiden
        genre = get_genre(file_path)
        target_folder = determine_target_folder(genre)
        print(f"  Erkanntes Genre: '{genre}' => Zuweisung: {target_folder}")
        
        # 2. Upload
        success = upload_to_azuracast(file_path, target_folder)
        
        # 3. Aufräumen (lokal verschieben)
        if success:
            dest_path = DONE_DIR / file_path.name
            
            # Falls Datei schon im Upload-Ordner existiert (z.B. neu getaggt), überschreiben
            if dest_path.exists():
                dest_path.unlink()
                
            shutil.move(str(file_path), str(dest_path))
            print(f"  -> Datei lokal nach '_Uploaded' verschoben.\n")
        else:
            print("  -> Datei verbleibt in '_Sorted' für erneuten Versuch.\n")
            
        time.sleep(2) # Kurze Pause zur Schonung der Server-Ressourcen

if __name__ == "__main__":
    main()
