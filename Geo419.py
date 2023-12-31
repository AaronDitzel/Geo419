# -*- coding: utf-8 -*-
"""
Created on Sat Jul  1 18:11:37 2023
Dieses Python-Skript hilft Ihnen dabei, GeoTIFF-Bilddaten zu bearbeiten und zu visualisieren, die möglicherweise in ZIP-Archiven verpackt sind.
@author: Aaron Ditzel
"""
# Importiere die benötigten Module
import os
import argparse
import requests
import zipfile
import rasterio
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

# Funktion, die überprüft, ob eine ZIP-Datei im angegebenen Verzeichnis existiert (directory -- Pfad zum Verzeichnis (string))
def check_zip_file(directory):
    if not os.path.exists(directory):
        print(f"Das Verzeichnis {directory} existiert nicht.")
        return

    files = os.listdir(directory)

    zip_files = [file for file in files if file.endswith(".zip")]

    if zip_files:
        print("Es wurde ein oder mehrere ZIP-Archive gefunden:")
        for zip_file in zip_files:
            print(zip_file)
    else:
        print("Es wurden keine ZIP-Archive gefunden.")

# Funktion zum Herunterladen einer ZIP-Datei von einer URL (string)
def download_zip(url, directory):
    filename = url.split("/")[-1]
    file_path = os.path.join(directory, filename)

    if os.path.exists(file_path):
        print(f"Die Datei {filename} existiert bereits im Verzeichnis {directory}.")
        return

    print(f"Lade Datei von {url} herunter...")
    response = requests.get(url)

    if response.status_code == 200: #Http Code 200 = Anfrage erfolgreich
        with open(file_path, 'wb') as f: # Öffnen der Datei im Write-Binary-Modus
            f.write(response.content)
        print(f"Die Datei wurde erfolgreich als {filename} im Verzeichnis {directory} gespeichert.")
    else:
        print("Es gab einen Fehler beim Herunterladen der Datei. Bitte überprüfen Sie die URL.")

# Funktion zum Überprüfen, ob eine GeoTiff-Datei im angegebenen Verzeichnis existiert (string)
def check_geotiff_file(directory, geotiff_name):
    if not os.path.exists(directory):
        print(f"Das Verzeichnis {directory} existiert nicht.")
        return

    files = os.listdir(directory)

    if geotiff_name in files:
        print(f"Die GeoTiff-Datei {geotiff_name} wurde gefunden.")
    else:
        print(f"Die GeoTiff-Datei {geotiff_name} wurde nicht gefunden.")

# Funktion zum Entpacken einer GeoTiff-Datei, falls sie sich in einer ZIP-Datei befindet (string)
def unzip_geotiff_if_needed(directory, geotiff_name):
    files = os.listdir(directory)

    if geotiff_name in files:
        print(f"Die GeoTiff-Datei {geotiff_name} wurde gefunden.")
        return

    zip_files = [file for file in files if file.endswith(".zip")]
    for zip_file in zip_files:
        with zipfile.ZipFile(os.path.join(directory, zip_file), 'r') as zip_ref:
            if geotiff_name in zip_ref.namelist():
                print(f"Die GeoTiff-Datei {geotiff_name} wurde im ZIP-Archiv {zip_file} gefunden, beginne mit dem Entpacken.")
                zip_ref.extractall(directory)
                return

    print(f"Die GeoTiff-Datei {geotiff_name} wurde in keinem der ZIP-Archive gefunden.")

# Funktion zur Bearbeitung einer GeoTiff-Datei (string)
def process_image(input_path=None, output_path=None):
    if input_path is None:
        input_path = input("Bitte geben Sie den Pfad zur Eingabedatei ein: ")
    if output_path is None:
        output_path = input("Bitte geben Sie den Pfad zur Ausgabedatei ein: ")

    # Die Eingabedatei wird geöffnet und in eine Matrix geladen
    with rasterio.open(input_path) as src:
        img_array = src.read(1)

        img_array = img_array + 1e-10 # Verhindert Division durch Null in der folgenden Berechnung

         # Fortschrittsbalken für den Benutzer
        with tqdm(total=100, desc='Bild wird geladen', unit='%') as pbar:
            img_array_db = 10 * np.log10(img_array)

            # Schreiben der umgewandelten Matrix in die Ausgabedatei
            with rasterio.open(
                output_path, 'w', driver='GTiff', height=img_array_db.shape[0],
                width=img_array_db.shape[1], count=1, dtype=img_array_db.dtype,
                crs=src.crs, transform=src.transform
            ) as dst:
                dst.write(img_array_db, 1)
            
            pbar.update(100)  # Aktualisierung des Fortschrittsbalkens

    return output_path

# Funktion zum Anzeigen einer GeoTiff-Datei (string)
def plot_image(path=None):
    # Wenn kein Pfad angegeben wurde, wird der Benutzer danach gefragt
    if path is None:
        path = input("Bitte geben Sie den Pfad zur Bilddatei ein: ")
        
    # Die Bilddatei wird geöffnet und in eine Matrix geladen
    with rasterio.open(path) as src:
        img_array = src.read(1)

        # Maske für fehlende Daten erstellen
        mask = img_array == src.nodata

        # Farbschema für die Anzeige festlegen
        cmap = 'terrain'

        plt.figure(figsize=(10, 8))                         # Erstellen einer neuen Matplotlib-Figur
        plt.imshow(img_array, cmap=cmap)                    # Anzeigen des Bildes mit dem festgelegten Farbschema
        plt.colorbar(label='dB')                            # Hinzufügen einer Farbleiste
        plt.title('Rückstreuintensität (dB)')               # Setzen des Titels des Plots
        plt.xlabel('X-Koordinate')
        plt.ylabel('Y-Koordinate')
        plt.gca().set_aspect('equal', adjustable='box')     # Festlegen des Aspekts des Plots
        plt.gca().xaxis.set_major_locator(plt.MaxNLocator(5))
        plt.gca().yaxis.set_major_locator(plt.MaxNLocator(5))
        plt.gca().set_xticklabels([int(x) for x in plt.gca().get_xticks()], rotation=45)
        plt.gca().set_yticklabels([int(y) for y in plt.gca().get_yticks()])

        # Anwendung der Maske auf das Bild
        img_array = np.ma.masked_where(mask, img_array)

        # Anzeigen des maskierten Bildes
        plt.imshow(img_array, cmap=cmap, alpha=0.7)

        # Visualisierung
        plt.show()

# Hauptfunktion, die die oben definierten Funktionen aufruft
def main(directory=None, geotiff_name=None, zip_url=None):
    if directory is None:
        directory = input("Bitte geben Sie das Verzeichnis ein, in dem nach ZIP-Archiven gesucht werden soll: ")
        
    check_zip_file(directory)
    
    if input("Möchten Sie eine ZIP-Datei herunterladen? (Y/N): ").lower() == 'y':
        if zip_url is None:
            zip_url = input("Bitte geben Sie die URL der ZIP-Datei ein, die heruntergeladen werden soll: ")
        download_zip(zip_url, directory)
        check_zip_file(directory)

    if geotiff_name is None:
        geotiff_name = input("Bitte geben Sie den Namen der GeoTiff-Datei ein: ")
        
    check_geotiff_file(directory, geotiff_name)
    unzip_geotiff_if_needed(directory, geotiff_name)

    input_path = input("Bitte geben Sie den Pfad zur Eingabedatei ein: ")
    output_path = input("Bitte geben Sie den Pfad zur Ausgabedatei ein: ")
    processed_image_path = process_image(input_path, output_path)
    plot_image(processed_image_path)


# Aufruf des Skript
if __name__ == "__main__":
    # ArgumentParser wird zum Verarbeiten der Befehlszeilenargumente verwendet
    parser = argparse.ArgumentParser(description="Überprüft, ob ein ZIP-Archiv und eine GeoTiff-Datei in einem Verzeichnis vorhanden sind und lädt sie herunter.")
    parser.add_argument("directory", nargs='?', default=None, help="Das Verzeichnis, in dem nach ZIP-Archiven gesucht werden soll.")
    parser.add_argument("geotiff_name", nargs='?', default=None, help="Der Name der GeoTiff-Datei, die verarbeitet werden soll.")
    parser.add_argument("zip_url", nargs='?', default=None, help="Die URL der ZIP-Datei, die heruntergeladen werden soll.")
    args = parser.parse_args()
    # Aufruf der Hauptfunktion mit den über die Befehlszeile übergebenen Argumenten
    main(args.directory, args.geotiff_name, args.zip_url)
