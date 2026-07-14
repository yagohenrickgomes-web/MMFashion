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

## Próximos passos

- Criar as páginas restantes de `pages/` e `admin/` seguindo a mesma identidade visual.
- Trocar imagens de exemplo (Unsplash) pelas fotos reais da MM Fashion.
- Se/quando precisar de backend (login real, banco de dados, carrinho persistente), migrar para um projeto Flask.
