## emplacement du venv

Le venv actif est `/tmp/venv` (`echo $VIRTUAL_ENV`). Il est recréé à chaque rebuild depuis `uv.lock` : déclarez chaque package avec `uv add --active`, sinon il disparaît au rebuild suivant.

## installation package

```bash
uv add --active pandas # (1)
```

1.  le `--active` est essentiel pour utiliser l'env actif, sinon creation d'un nouveau venv
