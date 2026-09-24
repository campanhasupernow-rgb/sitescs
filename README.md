# CS2 NOTÍCIAS / CS2NEWS

Portal bilíngue de Counter-Strike 2.

- **CS2 NOTÍCIAS**: PT-BR, foco Brasil/LATAM + cenário global.
- **CS2NEWS**: EN-US, foco América do Norte + cenário global.

## Automação

- Valve Regional Standings: sincronização automática sem chave.
- Valve / Steam news: sincronização automática sem chave.
- PandaScore: partidas e placares quando `PANDASCORE_TOKEN` estiver configurado.
- GitHub Actions: sincronização a cada 15 minutos e deploy no GitHub Pages.

## URLs

- `/cs2noticias/`
- `/cs2news/`

## Desenvolvimento local

```bash
python scripts/build.py
python scripts/serve.py
```
