# Finance Halal Canada — visuels

Hébergement des visuels (1080×1920) publiés sur TikTok, Instagram et Facebook, et générateur d'images au gabarit FHC.

## Générer un visuel

```
python3 tools/make_post.py specs/<nom>.json
```

Sortie : `posts/<slug>.jpg` (JPEG, environ 300 Ko). Prérequis : `wkhtmltoimage`, Pillow, police Poppins.

## Format d'une spec (JSON)

- `slug` : nom du fichier de sortie
- `title` : titre (`\n` pour un retour à la ligne)
- `tagline` : phrase de conclusion en bas du cercle (optionnel)
- `blocks` : liste de blocs parmi `intro`, `dots`, `callout`, `stats`, `note`, `notebox`, `list`, `compare`

Exemple complet : `specs/zakat-calcul.json`.

## Lien public d'une image

```
https://raw.githubusercontent.com/fhc-media/fhc-posts/main/posts/<slug>.jpg
```
