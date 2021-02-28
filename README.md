# MCMC pseudoword generator

## Training

Type `make` to download some corpus and train a model:

```console
$ make
...
```

Generate some pseudo-words:

```console
$ _venv/bin/python -m wordgen.cli generate --group Simple --count 4 _data/models.h5
unusabby
distified
shrify
eate
$ _venv/bin/python -m wordgen.cli generate --group Universe --count 4 _data/models.h5
uncorphilticlasily
dipothyrinum
unremonin
flavory
$ _venv/bin/python -m wordgen.cli generate --group Name --count 4 _data/models.h5
phill
rin
anate
bell
```

You can train the model using your own corpus and with different parameter:

```console
$ make _init.ok
$ _venv/bin/python -m wordgen.cli train --token-size 4 --group MyModel models.h5 < my_corpus.txt
```

This example extracts ASCII words from `my_corpus.txt`, trains a 4-gram MCMC
transition matrix and stores it in `MyModel` group defined in `models.h5` HDF5
file.
