# Fotografien und Team

Dieses eigenständige Quarto-Projekt ergänzt die Website um eine reproduzierbare Bildübersicht in HTML und PDF. Es wird bewusst getrennt vom HTML-Template der Website gerendert.

## Voraussetzungen

- Quarto
- XeLaTeX
- Arial
- Die fünf ausgewählten JPEG-Dateien im Unterordner `images/`

## Rendern

Vom Repository-Hauptverzeichnis:

```sh
quarto render review/photo-review.qmd --to all
```

Ergebnisse:

- `review/output/photo-review.html` (mit eingebetteten Bildern)
- `review/output/photo-review.pdf`

Die Porträts sind neutral beschriftet; Namen und Rollen stehen in einem gemeinsamen Teamabsatz. Nach dem Rendern das PDF in Seitenbilder umwandeln und alle drei Seiten visuell kontrollieren. Die Bildlegenden verwenden fett gesetzte Panelbuchstaben und normal gesetzte Titel.

Das gerenderte HTML zusätzlich bei Desktop- und Mobilbreite visuell prüfen: Alle fünf Bilder sollen sichtbar sein, ohne horizontalen Überlauf.

Die Bilddateien stammen aus der vom Projektleiter bereitgestellten [Galerie von Verena Müller](https://www.picdrop.com/verenamuellerfotografie/7e4Z7c46Ma). Der PDF-Export verwendet JPEG-Versionen derselben Auswahl wie die Website; keine KI-generierten Elemente oder Retuschen.
