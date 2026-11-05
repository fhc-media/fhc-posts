# Finance Halal Canada — visuels

Hébergement des visuels (1080×1920) publiés sur TikTok, Instagram et Facebook, et générateur d'images au gabarit FHC.

## Générer un visuel

```
python3 tools/make_post.py specs/<nom>.json
```

Sortie : `posts/<slug>.jpg` (JPEG 1350×1350, environ 300 Ko). Prérequis : Python avec Playwright (Chromium) et Pillow, police Poppins.

## Style et format des specs

Voir `docs/STYLE.md` (charte visuelle et format JSON). Exemples : `specs/*.json`.

## Lien public d'une image

```
https://raw.githubusercontent.com/fhc-media/fhc-posts/main/posts/<slug>.jpg
```
