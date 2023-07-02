# GeoTIFF-Processing
Dieses Python-Skript hilft Ihnen dabei, GeoTIFF-Bilddaten zu bearbeiten und zu visualisieren, die möglicherweise in ZIP-Archiven verpackt sind.

## Anforderungen
Stellen Sie sicher, dass Sie folgende Python-Pakete installiert haben:

os
argparse
requests
zipfile
rasterio
matplotlib
numpy
tqdm

Diese können Sie installieren mit:

    pip install argparse requests zipfile rasterio matplotlib numpy tqdm

## Verwendung
Sie können das Skript direkt von der Befehlszeile aus mit optionalen Argumenten ausführen, die das zu durchsuchende Verzeichnis, den Namen der GeoTIFF-Datei und die URL der zu downloadenden ZIP-Datei spezifizieren.

Hier ist ein Beispielaufruf:
(bash)
    
    python Geo417.py /Pfad/zum/Ordner S1A_IW_20230214T031857_DVP_RTC10_G_gpunem_A42B_VH_clipped.tif https://upload.uni-jena.de/data/64830a407fda25.17120430/S1A_IW_20230214T031857_DVP_RTC10_G_gpunem_A42B_VH_clipped.tif.zip

Wenn Sie das Skript ohne Argumente ausführen, werden Sie zur Eingabe der benötigten Informationen aufgefordert.

## Das Skript führt folgende Schritte aus:

1. Überprüfung, ob das angegebene Verzeichnis existiert und ob es ZIP-Archive enthält.
2. Falls gewünscht, wird eine ZIP-Datei von einer URL heruntergeladen.
3. Es wird überprüft, ob die gewünschte GeoTIFF-Datei im Verzeichnis oder in einem der ZIP-Archive vorhanden ist.
4. Falls die GeoTIFF-Datei in einem ZIP-Archiv gefunden wurde, wird sie entpackt.
5. Das GeoTIFF-Bild wird bearbeitet und das Ergebnis wird als neues GeoTIFF-Bild gespeichert.
6. Das bearbeitete GeoTIFF-Bild wird angezeigt.
