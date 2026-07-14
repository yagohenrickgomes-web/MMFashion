# MM Fashion — E-commerce

Site institucional + painel administrativo da MM Fashion.
HTML5 / CSS3 / JavaScript puro (sem frameworks). Cada página é um arquivo único e autocontido.

## Estrutura de pastas

```
MM Fashion/
├── index.html              → Página inicial (loja)
├── pages/                  → Páginas públicas da loja
│   ├── produto.html        → Página de produto (a criar)
│   ├── carrinho.html       → Carrinho (a criar)
│   └── login.html          → Login / cadastro (a criar)
├── admin/                  → Painel administrativo
│   ├── painel-admin.html   → Dashboard (pronto)
│   ├── produtos-admin.html → Cadastro de produtos (a criar)
│   ├── estoque.html        → Controle de estoque (a criar)
│   ├── pedidos.html        → Gestão de pedidos (a criar)
│   ├── clientes.html       → Gestão de clientes (a criar)
│   ├── financeiro.html     → Financeiro (a criar)
│   ├── relatorios.html     → Relatórios (a criar)
│   └── configuracoes.html  → Configurações (a criar)
└── assets/
    ├── images/              → Logos, favicon, imagens locais
    ├── css/                 → (reservado — hoje o CSS está inline em cada página)
    └── js/                  → (reservado — hoje o JS está inline em cada página)
```

> As imagens de produto/categoria hoje vêm do Unsplash (URLs remotas), só como exemplo visual.
> Quando tiver as fotos reais da loja, salve em `assets/images/` e troque os `src` nos arquivos.

## Como rodar localmente (Windows)

1. Abra o cmd ou o terminal do VS Code na pasta do projeto:
   ```cmd
   cd "C:\Users\User\Desktop\Yago\Clientes\LOJA ROUPA\MM Fashion"
   ```

2. Suba o servidor local com Python (não precisa instalar nada extra):
   ```cmd
   python -m http.server 8000
   ```
   Se `python` não for reconhecido, use `py -m http.server 8000`.

3. Acesse no navegador:
   - Loja: http://localhost:8000
   - Painel admin: http://localhost:8000/admin/painel-admin.html

4. Para parar o servidor: `Ctrl + C` no terminal.

## Como publicar (Railway)

1. Suba o projeto pro GitHub (se ainda não subiu):
   ```cmd
   cd "C:\Users\User\Desktop\Yago\Clientes\LOJA ROUPA\MM Fashion"
   git add .
   git commit -m "Deploy via Railway"
   git push
   ```

2. Crie conta em https://railway.com (dá pra entrar direto com o GitHub).

3. No painel do Railway: **New Project → Deploy from GitHub repo** → selecione o repositório `MMFashion`.

4. Adicione o banco: dentro do projeto, clique em **+ New → Database → Add PostgreSQL**.
   O Railway já cria a variável `DATABASE_URL` sozinho e conecta ao serviço web automaticamente.

5. No serviço web, vá em **Settings → Variables** e confira/adicione:
   - `SECRET_KEY` → uma string aleatória longa (pode gerar em https://randomkeygen.com)
   - `FLASK_ENV` → `production`

6. O Railway lê o `railway.json` sozinho e já sabe como instalar as dependências e iniciar o app.

7. Depois do primeiro deploy, abra o **Shell** do serviço (ou rode localmente apontando pro banco do Railway) e execute uma vez:
   ```cmd
   cd backend
   python init_db.py
   ```
   Isso cria as tabelas e o admin padrão (`admin@mmfashion.com.br` / `mudar123` — troque depois).

8. O Railway te dá uma URL pública tipo `https://mmfashion-production.up.railway.app` — é só acessar. O painel fica em `/admin/painel-admin.html`.

## Próximos passos

- Criar as páginas restantes de `pages/` e `admin/` seguindo a mesma identidade visual.
- Trocar imagens de exemplo (Unsplash) pelas fotos reais da MM Fashion.
- Se/quando precisar de backend (login real, banco de dados, carrinho persistente), migrar para um projeto Flask.
