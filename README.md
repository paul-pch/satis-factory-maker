# satis-factory-maker

Python client that helps to build factory or only factory layer depending on either the target item, or depending on the resources available.

## Installation

Requires [uv](https://docs.astral.sh/uv/). Clone the repository, then:

```bash
    make
```

`make` syncs the environment (`uv sync`), builds the `dist/satisfactory` binary and adds `dist/` to the `PATH` in `~/.zshrc`. Use `make sync` to only install the dependencies and `make test` to run the tests.

## Usage

```bash
    satisfactory --help                     # or: uv run satis.py --help
```

### Data

Factory commands read `data/data.json`, generated from the game's own data file (`<Satisfactory install>/CommunityResources/Docs/en-US.json`):

```bash
    satisfactory parse --file <path/to/en-US.json>     # writes data/data.json (--output to change)
```

Regenerate and commit `data/data.json` after each game update rather than editing it.

### Search

```bash
    satisfactory search item --query iron
    satisfactory search recipe --query iron-plate      # matches recipe names and products
```

### Build

```bash
    satisfactory build --query heavy-modular-frame --minute-rate 2
```

For each item of the production chain, the matching recipes are listed with their number in the `#` column: type that number to use the recipe, or `0` to consider the item as imported from a train station (unlimited supply). Imported items are not produced and are listed in the "Imports en gare" table.

By default (simple mode), the recipe chosen for an item is reused everywhere that item appears in the chain: each item is asked only once. Add `--complex` to choose a recipe for every node of the tree (e.g. smelt the ingots of one branch and import those of another).

At the end, the build prints an `ID usine` (e.g. `heavy-modular-frame:1210…`): the target item followed by one character per recipe choice (`item:…` in simple mode, `item::…` in complex mode, which `--id` replays in the same mode). Pass it back with `--id` to rebuild the same factory without the prompts, at any rate:

```bash
    satisfactory build --id heavy-modular-frame:1210… --minute-rate 10
```

The choices are recipe positions in `data/data.json`: an ID may become invalid after a game update.

## Features

### Bugs

* Les taux d'entrée et de sortie sur l'affichage d'une factory ne sont pas multipliés par le nombre de machines (ils sont donnés pour une seule machine)
* Un item sans recette de fabrication (leaves, mycelia, power slugs, remains, déchets nucléaires…) arrête le build sur "No recipe found" sans proposer l'import en gare : contournement, importer l'item parent (ex. `biomass`)
* Choisir des recettes qui se consomment mutuellement (ex. `alt-recycled-plastic` / `alt-recycled-rubber`) fait boucler le build à l'infini (RecursionError)

### Build

* Build factory lines from target item with 100% efficiency
* * Afficher les surproduction ou les équilibrage sur les Productionline
* * Ajouter la possibilité de cibler 2 items avec 2 taux minutes
* * Ajouter la possibilité de pas traiter un item (quand il est importé comme le caoutchou/plastique)
* * Contraindre le build d'une usine pour que chaque item soit en surproduction
* * Possibilité de ne pas faire de limit rate ? (defaut output de recipe)

en mode simple (par défaut) je veux que les recette que j'ai déjà choisies soient réutilisées pour les même items. Je garde un mode complexe pour choisir chaque recette de l'arbre
 
### Problématiques

* Traiter efficacement les produits dérivés en sortie (seul le premier produit d'une recette est pris en compte : choisir la recette `fuel` pour du polymer-resin crée une ligne `fuel`)
