# -*- coding: utf-8 -*-
"""
Created on Sat Jul  1 18:11:37 2023

@author: aaron
"""

import os
import argparse
import requests
import zipfile
import rasterio
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

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


def download_zip(url, directory):
    filename = url.split("/")[-1]
    file_path = os.path.join(directory, filename)

    if os.path.exists(file_path):
        print(f"Die Datei {filename} existiert bereits im Verzeichnis {directory}.")
        return

    print(f"Lade Datei von {url} herunter...")
    response = requests.get(url)

    if response.status_code == 200:
        with open(file_path, 'wb') as f:
            f.write(response.content)
        print(f"Die Datei wurde erfolgreich als {filename} im Verzeichnis {directory} gespeichert.")
    else:
        print("Es gab einen Fehler beim Herunterladen der Datei. Bitte überprüfen Sie die URL.")


def check_geotiff_file(directory, geotiff_name):
    if not os.path.exists(directory):
        print(f"Das Verzeichnis {directory} existiert nicht.")
        return

    files = os.listdir(directory)

    if geotiff_name in files:
        print(f"Die GeoTiff-Datei {geotiff_name} wurde gefunden.")
    else:
        print(f"Die GeoTiff-Datei {geotiff_name} wurde nicht gefunden.")


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


def process_image(input_path=None, output_path=None):
    if input_path is None:
        input_path = input("Bitte geben Sie den Pfad zur Eingabedatei ein: ")
    if output_path is None:
        output_path = input("Bitte geben Sie den Pfad zur Ausgabedatei ein: ")

    with rasterio.open(input_path) as src:
        img_array = src.read(1)

        img_array = img_array + 1e-10

        with tqdm(total=100, desc='Bild wird geladen', unit='%') as pbar:
            img_array_db = 10 * np.log10(img_array)

            with rasterio.open(
                output_path, 'w', driver='GTiff', height=img_array_db.shape[0],
                width=img_array_db.shape[1], count=1, dtype=img_array_db.dtype,
                crs=src.crs, transform=src.transform
            ) as dst:
                dst.write(img_array_db, 1)

            pbar.update(100)

    return output_path


def plot_image(path=None):
    if path is None:
        path = input("Bitte geben Sie den Pfad zur Bilddatei ein: ")

    with rasterio.open(path) as src:
        img_array = src.read(1)

        mask = img_array == src.nodata

        cmap = 'terrain'

        plt.figure(figsize=(10, 8))
        plt.imshow(img_array, cmap=cmap)
        plt.colorbar(label='dB')
        plt.title('Rückstreuintensität (dB)')
        plt.xlabel('X-Koordinate')
        plt.ylabel('Y-Koordinate')
        plt.gca().set_aspect('equal', adjustable='box')
        plt.gca().xaxis.set_major_locator(plt.MaxNLocator(5))
        plt.gca().yaxis.set_major_locator(plt.MaxNLocator(5))
        plt.gca().set_xticklabels([int(x) for x in plt.gca().get_xticks()], rotation=45)
        plt.gca().set_yticklabels([int(y) for y in plt.gca().get_yticks()])

        img_array = np.ma.masked_where(mask, img_array)

        plt.imshow(img_array, cmap=cmap, alpha=0.7)

        plt.show()


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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Überprüft, ob ein ZIP-Archiv und eine GeoTiff-Datei in einem Verzeichnis vorhanden sind und lädt sie herunter.")
    parser.add_argument("directory", nargs='?', default=None, help="Das Verzeichnis, in dem nach ZIP-Archiven gesucht werden soll.")
    parser.add_argument("geotiff_name", nargs='?', default=None, help="Der Name der GeoTiff-Datei, die verarbeitet werden soll.")
    parser.add_argument("zip_url", nargs='?', default=None, help="Die URL der ZIP-Datei, die heruntergeladen werden soll.")
    args = parser.parse_args()
    main(args.directory, args.geotiff_name, args.zip_url)
