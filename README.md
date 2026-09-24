# CS2 NOTÍCIAS / CS2NEWS

Portal bilíngue e automatizado de Counter-Strike 2.

## Edições

- **CS2 NOTÍCIAS**: PT-BR com foco em Brasil/LATAM e cenário global.
- **CS2NEWS**: EN-US com foco em América do Norte e cenário global.

## Dados e automação

- Valve Regional Standings: Global, Americas, Europe e Asia.
- Comparação automática entre snapshots para rank movement.
- Roster Tracker baseado nos rosters registrados no VRS.
- Notícias oficiais do Counter-Strike / Steam.
- Conteúdo editorial automatizado a partir de mudanças verificáveis nos dados.
- PandaScore opcional para partidas e placares ao vivo via `PANDASCORE_TOKEN`.
- Sincronização programada a cada 30 minutos.
- Build e validação automática antes de cada deploy.

## Portal

O build gera:

- homes PT-BR e EN-US;
- notícias e páginas individuais;
- rankings regionais;
- perfis de times;
- perfis de jogadores;
- roster tracker;
- campeonatos;
- busca;
- páginas About / Editorial / Privacy / Advertise / Contact;
- sitemap e robots.txt.

## Validação

```bash
python scripts/build.py
python scripts/validate.py
node --check assets/app.js
```

## Produção

- https://campanhasupernow-rgb.github.io/sitescs/cs2noticias/
- https://campanhasupernow-rgb.github.io/sitescs/cs2news/
