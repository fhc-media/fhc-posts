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

## Panneaux illustrés
Chaque panneau peut être une **scène** vectorielle (`scene`) : `mosque`, `city`, `cabin`, `desk`, `thinker`, `money`, `bills`, `scale`, `shield`, `house`, `stocks`, `family` (tools/scenes.py). Habillage : légende sombre en haut (`cap`), pastille jaune en bas (`hl`), question jaune (`q`) et bulle « Dis-le en commentaire ! » (`cm`).

## Ce que le générateur ne fait pas
Les scènes peintes très détaillées (personnages en situation, enfants, arène de hockey) viennent d'un générateur d'images IA. Ici : scènes vectorielles et mascotte fixe.

## Format d'une spec (JSON)
- `slug`, `title` (`<mark>` pour le surlignage, `\n` pour un retour à la ligne), `subtitle`, `pose` (`think`/`smile`), `cta`.
- Réglages optionnels : `tsize` (taille du titre), `sub_top`, `psize`, `xsize`, `isize`.
- `rows` : liste de lignes `{"h": poids, "inset": marge, "panels": [...]}`. Convention : ligne 1 pleine largeur, lignes suivantes avec `inset` ≈ 52 (le cercle rogne les coins).
- Panneau scène : `scene`, `cap`, `hl`, `q`, `cm`, `w` (poids de largeur).
- Panneau info : `tone` (`navy`/`light`), `color` (`blue`/`green`/`orange`/`purple`/`red`), `num`, `icon` (emoji), `iconpos` (`left`), `title`, `text`, `stat`, `note`, `hl`, `warn`, `center`.
- Exemples : `specs/*.json`. Commande : `python3 tools/make_post.py specs/<nom>.json`.

## Variante « colonnes » (sans mascotte)
- `header: "workspace"` remplace la mascotte par un bureau dessiné (portable, tasse, livres).
- Panneau colonne : `col: true`, `num`, `color` (`gold`/`green`/`blue`/`purple`/`teal`), `title`, `icons` (emojis), `bullets`, `ex`, `hl`, `mb` (marge basse pour suivre la courbe du cercle). Réglages : `head_h`, `foot_h`, `cbsize`, `cisize`. Exemple : `specs/commencer-1000.json`.
- Deux familles de visuels : (A) générés par ChatGPT (style peint, publiés tels quels après vérification du texte) ; (B) générés ici (vectoriel, automatisables).
