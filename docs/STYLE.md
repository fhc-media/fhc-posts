# Style visuel Finance Halal Canada (v2, illustré)

Référence : les infographies « circulaires » illustrées de la marque (format carré 1080×1080, rendu 1350×1350).

## Forme
- Fond menthe très pâle, grand **cercle liseré jaune** (#f6df4b) qui rogne tout le contenu.
- Trois zones : **en-tête** (ciel bleu/marine, skyline de Toronto avec la tour CN et un dôme de mosquée, sapins), **corps** (panneaux arrondis), **pied** (marine, skyline, logo FHC).
- **Mascotte** : homme barbu, cheveux noirs, sweat marine ; pose « think » (main au menton) ou « smile ».

## Couleurs
- Marine #12244a, jaune surligneur #f6df4b, or #d9b24f, fond clair #f8fcfb.
- Cartes numérotées : bleu, vert, orange, violet, rouge (dégradés). Panneaux « light » à liseré vert, rouge si avertissement.

## Typographie
- **Poppins** : titres (800), titres de panneaux (700), textes (500).
- **Kalam** (manuscrite) : sous-titre jaune, pastilles de surlignage jaune, bulle d'appel à l'action.
- Un mot-clé du titre est surligné en jaune (`<mark>`).

## Ton et contenu
- Tutoiement, phrases courtes, un hook en titre, une question d'engagement dans la bulle jaune du pied.
- Chiffres canadiens à jour (ex. CELI 2026 : 7 000 $, droits cumulés 109 000 $). Rendements : toujours « historique, non garanti ».
- Avertissement de conformité quand c'est pertinent (comités de conformité, vérifier la source).
- Slogan du pied : « ÉPARGNER · INVESTIR · BÂTIR · UN AVENIR HALAL » (« UN » et non « UNE »).
- Logo : « FHC » en serif blanc avec barre rouge et feuille d'érable or, puis FINANCE / HALAL (or) / CANADA.

## Ce que le générateur ne fait pas
Les scènes illustrées complexes (personnage en situation, décors détaillés) viennent d'un générateur d'images IA. Ici : mascotte vectorielle fixe, icônes Twemoji, skyline vectorielle.

## Format d'une spec (JSON)
- `slug`, `title` (`<mark>` pour le surlignage, `\n` pour un retour à la ligne), `subtitle`, `pose` (`think`/`smile`), `cta`.
- Réglages optionnels : `tsize` (taille du titre), `sub_top`, `psize`, `xsize`, `isize`.
- `rows` : liste de lignes `{"h": poids, "inset": marge, "panels": [...]}`.
- Panneau : `tone` (`navy`/`light`), `color` (`blue`/`green`/`orange`/`purple`/`red`), `num`, `icon` (emoji), `iconpos` (`left`), `title`, `text`, `stat`, `note`, `hl`, `warn`, `center`.
- Exemples : `specs/*.json`. Commande : `python3 tools/make_post.py specs/<nom>.json`.
