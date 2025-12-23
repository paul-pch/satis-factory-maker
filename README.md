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

* [x] fetch - Gathers json data of the game
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


### Problématiques

* [ ] Traiter efficacement les produits dérivés en sortie
