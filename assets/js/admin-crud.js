/* ============================================================
   AdminCRUD — motor único de cadastro/listagem usado por todas
   as abas do painel administrativo (Pedidos, Categorias, Clientes,
   Estoque, Financeiro, Cupons, Funcionários).
   Cada página só passa a configuração (colunas, campos, dados) —
   isso evita repetir o mesmo código 9 vezes e mantém o sistema leve.

   Guarda os dados no localStorage por enquanto (funciona offline,
   sem precisar de backend pra cada módulo). Quando cada módulo for
   ligado no PostgreSQL de verdade, só troca loadItems/saveItems
   por chamadas fetch — o resto do motor continua igual.
   ============================================================ */
const AdminCRUD = (() => {

  function money(v){
    const n = parseFloat(v) || 0;
    return n.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }

  function showToast(msg){
    let toastEl = document.getElementById('toast');
    if (!toastEl){
      toastEl = document.createElement('div');
      toastEl.className = 'toast';
      toastEl.id = 'toast';
      toastEl.innerHTML = '<svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg><span id="toastMsg"></span>';
      document.body.appendChild(toastEl);
    }
    document.getElementById('toastMsg').textContent = msg;
    toastEl.classList.add('show');
    clearTimeout(window._crudToastTimer);
    window._crudToastTimer = setTimeout(() => toastEl.classList.remove('show'), 2800);
  }

  function init(config){
    const { storageKey, title, itemLabel, subtitle, columns, fields, sampleData, mountId, searchable } = config;
    const mount = document.getElementById(mountId || 'crudMount');
    let items = loadItems();

    function loadItems(){
      try {
        const saved = localStorage.getItem('mmfashion_' + storageKey);
        if (saved) return JSON.parse(saved);
      } catch (e) { /* ignora */ }
      return sampleData.map((d, i) => ({ id: i + 1, ...d }));
    }

    function saveItems(){
      try { localStorage.setItem('mmfashion_' + storageKey, JSON.stringify(items)); } catch (e) { /* ignora */ }
    }

    function render(filterText){
      const filtered = !filterText ? items : items.filter(item =>
        columns.some(c => String(item[c.key] ?? '').toLowerCase().includes(filterText.toLowerCase()))
      );

      mount.innerHTML = `
        <div class="panel-head">
          <div><h3>${title}</h3><span class="sub">${subtitle}</span></div>
          <div style="display:flex;gap:10px;align-items:center;">
            ${searchable ? `<div class="topbar-search" style="width:200px;box-shadow:none;border:1px solid rgba(45,45,45,.12);">
              <svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
              <input type="text" id="crudSearch" placeholder="Buscar...">
            </div>` : ''}
            <button class="btn-new-product" id="crudAddBtn">
              <svg viewBox="0 0 24 24"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
              Novo
            </button>
          </div>
        </div>
        <div class="table-wrap">
          <table>
            <thead><tr>${columns.map(c => `<th>${c.label}</th>`).join('')}<th></th></tr></thead>
            <tbody>${
              filtered.length
                ? filtered.map(rowHtml).join('')
                : `<tr><td colspan="${columns.length + 1}" style="text-align:center;color:var(--gray);padding:34px;">Nada por aqui ainda. Clique em "Novo" para cadastrar.</td></tr>`
            }</tbody>
          </table>
        </div>
      `;

      document.getElementById('crudAddBtn').addEventListener('click', () => openModal());
      mount.querySelectorAll('[data-edit]').forEach(b => b.addEventListener('click', () => openModal(b.dataset.edit)));
      mount.querySelectorAll('[data-delete]').forEach(b => b.addEventListener('click', () => removeItem(b.dataset.delete)));

      const searchInput = document.getElementById('crudSearch');
      if (searchInput){
        searchInput.value = filterText || '';
        searchInput.addEventListener('input', () => render(searchInput.value));
        searchInput.focus();
        searchInput.selectionStart = searchInput.value.length;
      }
    }

    function rowHtml(item){
      return `<tr>
        ${columns.map(c => `<td>${c.render ? c.render(item) : (item[c.key] ?? '—')}</td>`).join('')}
        <td style="text-align:right;white-space:nowrap;">
          <button class="row-action" data-edit="${item.id}" aria-label="Editar">
            <svg viewBox="0 0 24 24"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.12 2.12 0 0 1 3 3L12 15l-4 1 1-4z"/></svg>
          </button>
          <button class="row-action" data-delete="${item.id}" aria-label="Excluir">
            <svg viewBox="0 0 24 24"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/></svg>
          </button>
        </td>
      </tr>`;
    }

    function fieldHtml(f, editing){
      const val = editing ? (editing[f.key] ?? '') : (f.default ?? '');
      const fullClass = f.full ? ' field-full' : '';

      if (f.type === 'select'){
        return `<div class="field${fullClass}"><label>${f.label}</label>
          <select name="${f.key}">${f.options.map(o => `<option value="${o}" ${o === val ? 'selected' : ''}>${o}</option>`).join('')}</select>
        </div>`;
      }
      if (f.type === 'textarea'){
        return `<div class="field${fullClass}"><label>${f.label}</label><textarea name="${f.key}" rows="3">${val}</textarea></div>`;
      }
      return `<div class="field${fullClass}"><label>${f.label}</label>
        <input type="${f.type || 'text'}" name="${f.key}" value="${val}" ${f.required ? 'required' : ''}>
      </div>`;
    }

    function openModal(editId){
      const editing = editId ? items.find(i => String(i.id) === String(editId)) : null;
      const overlay = document.createElement('div');
      overlay.className = 'modal-overlay';
      overlay.innerHTML = `
        <div class="modal-box">
          <h3 style="font-family:var(--font-display);margin-bottom:20px;">${editing ? 'Editar' : 'Novo(a)'} ${itemLabel}</h3>
          <form id="crudForm">
            <div class="form-grid">${fields.map(f => fieldHtml(f, editing)).join('')}</div>
            <div class="form-actions">
              <button type="button" class="btn-cancel" id="crudCancelBtn">Cancelar</button>
              <button type="submit" class="btn-save">Salvar</button>
            </div>
          </form>
        </div>`;
      document.body.appendChild(overlay);

      overlay.querySelector('#crudCancelBtn').addEventListener('click', () => overlay.remove());
      overlay.addEventListener('click', (e) => { if (e.target === overlay) overlay.remove(); });

      overlay.querySelector('#crudForm').addEventListener('submit', (e) => {
        e.preventDefault();
        const data = {};
        fields.forEach(f => {
          const el = overlay.querySelector(`[name="${f.key}"]`);
          data[f.key] = el.value;
        });

        if (editing){
          Object.assign(editing, data);
        } else {
          items.unshift({ id: Date.now(), ...data });
        }
        saveItems();
        render(document.getElementById('crudSearch')?.value);
        overlay.remove();
        showToast(editing ? 'Atualizado com sucesso!' : 'Cadastrado com sucesso!');
      });
    }

    function removeItem(id){
      if (!confirm('Tem certeza que quer excluir? Essa ação não pode ser desfeita.')) return;
      items = items.filter(i => String(i.id) !== String(id));
      saveItems();
      render(document.getElementById('crudSearch')?.value);
      showToast('Removido.');
    }

    render();
  }

  return { init, money, showToast };
})();
