# Notícias PT

Leitor de feeds RSS de jornais portugueses, hospedado no GitHub Pages.

## Como funciona

- O **GitHub Actions** corre 5× por dia (7h, 10h, 13h, 17h, 21h UTC) e vai buscar os feeds RSS
- O script Python gera um `docs/feeds.json` com as notícias
- O **GitHub Pages** serve o `docs/index.html` que lê esse JSON

## Configuração

1. Faz fork ou cria um novo repositório com estes ficheiros
2. Vai a **Settings → Pages** → Source: `Deploy from a branch` → Branch: `main` → Folder: `/docs`
3. Vai a **Actions** e ativa os workflows
4. Corre o workflow manualmente pela primeira vez: **Actions → Fetch RSS Feeds → Run workflow**

## Estrutura
```
.github/workflows/fetch-feeds.yml   # agendamento automático
scripts/fetch_feeds.py              # vai buscar os feeds RSS
docs/index.html                     # a aplicação web
docs/feeds.json                     # notícias geradas (atualizado automaticamente)
```

## Adicionar/remover fontes

Edita a lista `SOURCES` em `scripts/fetch_feeds.py` e em `docs/index.html`.
