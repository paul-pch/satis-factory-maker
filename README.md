# satis-factory-maker

Python client that helps to build factory or only factory layer depending on either the target item, or depending on the resources available.

## Installation

To install **satis-factory-maker**, clone the repository and install the dependencies:

```bash
    git clone https://github.com/yourusername/satis-factory-maker.git
    cd satis-factory-maker
    make
```

## Usage

```bash
    satis --help
```

## Features

### Global

* [ ] test - Setup unit testing system

### Data

* [x] parse - Builds `data/data.json` from the game file `CommunityResources/Docs/en-US.json` (`satis.py parse --file <path>`)
* [ ] verify - Checks the integrity of the current data file

### Bugs

* [ ] Les taux de sortie sur l'affichage d'une factory ne sont pas multipliés par le nombre de machines 

### Build

* [ ] Build factory lines from target item with 100% efficiency
* * [ ] Afficher les surproduction ou les équilibrage sur les Productionline
* * [ ] Ajouter une feature de sauvegarde/lecture des usines
* * [ ] Ajouter la possibilité de cibler 2 items avec 2 taux minutes
* * [ ] Ajouter la possibilité de pas traiter un item (quand il est importé comme le caoutchou/plastique)
* * [ ] Contraindre le build d'une usine pour que chaque item soit en surproduction
* * [ ] Possibilité de considérer un item comme illimité (alimenté en gare)
* * [ ] Possibilité de ne pas faire de limit rate ? (defaut output de recipe)

### Problématiques

* [ ] Traiter efficacement les produits dérivés en sortie
