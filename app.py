# application/app.py

from flask import Flask, render_template, request, redirect, url_for
from domain.models import Budget, FixedExpense, InstallmentExpense
from domain.services import ExpenseService
from persistence.json_repository import JSONRepository
from datetime import date, datetime

app = Flask(__name__)

def get_repo():
    return JSONRepository('data/expenses.json')

@app.before_request
def before():
    repo = get_repo()
    cfg  = repo.load_config()

    # Reconciliação inicial: traz de volta ao ativo quem ainda não expirou
    inst_list = repo.load_installments()
    hist_list = repo.load_history() or []
    today     = date.today()
    moved     = []
    for h in hist_list:
        diff_months = (today.year - h.start_month.year) * 12 + (today.month - h.start_month.month) + 1
        # se estiver dentro do intervalo 1..n_parcels, volta para inst_list
        if 1 <= diff_months <= h.n_parcels:
            h.current_parcel = diff_months
            inst_list.append(h)
            moved.append(h)
    if moved:
        # remove do history e salva ambas listas
        for h in moved:
            hist_list.remove(h)
        repo.save_installments(inst_list)
        repo.save_history(hist_list)

    # … então o seu código existente de rollover mensal …
    current_month = today.strftime("%Y-%m")
    if cfg.month != current_month:
        service = ExpenseService(repo)
        service.process_new_month(current_month)
        cfg.month = current_month
        repo.save_config(cfg)


from datetime import date

@app.route('/')
def index():
    repo         = get_repo()
    cfg          = repo.load_config()
    fixed        = repo.load_fixed()
    installments = repo.load_installments()
    history      = repo.load_history() or []

    today = date.today()
    for inst in installments:
        diff_months = (today.year - inst.start_month.year) * 12 + (today.month - inst.start_month.month)
        inst.current_parcel = max(1, min(inst.n_parcels, diff_months + 1))

    service   = ExpenseService(repo)
    remaining = service.calculate_remaining(cfg)

    return render_template(
        'index.html',
        budget=cfg,
        remaining=remaining,
        fixed=fixed,
        installments=installments,
        history=history
    )


@app.route('/fixed/toggle/<int:id>', methods=['POST'])
def toggle_fixed(id):
    repo = get_repo()
    fixed_list = repo.load_fixed()

    # 1) Encontra o item clicado
    target = next((fe for fe in fixed_list if fe.id == id), None)
    if not target:
        return ('', 404)

    # 2) Decide o novo estado e pega o affiliate
    new_paid = not target.paid
    aff = target.affiliate

    # 3) Aplica a todos com o mesmo affiliate (e no próprio também)
    for fe in fixed_list:
        if fe.affiliate and fe.affiliate == aff:
            fe.paid = new_paid

    repo.save_fixed(fixed_list)
    return ('', 204)


@app.route('/installments/toggle/<int:id>', methods=['POST'])
def toggle_installment(id):
    repo = get_repo()
    inst_list = repo.load_installments()

    # 1) Encontra o item clicado
    target = next((inst for inst in inst_list if inst.id == id), None)
    if not target:
        return ('', 404)

    # 2) Novo estado e affiliate
    new_paid = not target.paid
    aff = target.affiliate

    # 3) Marca/desmarca todos do mesmo affiliate
    for inst in inst_list:
        if inst.affiliate and inst.affiliate == aff:
            inst.paid = new_paid

    repo.save_installments(inst_list)
    return ('', 204)


@app.route('/fixed', methods=['POST'])
def add_fixed():
    repo = get_repo()
    form = request.form
    fixed_list = repo.load_fixed()
    new_id = max((fe.id for fe in fixed_list), default=0) + 1
    fe = FixedExpense(
        id=new_id,
        name=form['name'],
        value=float(form['value']),
        due_day=int(form['due_day']),
        paid=False,
        affiliate=form['affiliate']
    )
    fixed_list.append(fe)
    repo.save_fixed(fixed_list)
    return redirect(url_for('index'))

from datetime import date, datetime

@app.route('/installments', methods=['POST'])
def add_installment():
    repo      = get_repo()
    inst_list = repo.load_installments()
    hist_list = repo.load_history() or []

    # --- 0) remover dos ativos todos os expirados e mandar pro histórico ---
    expired = [i for i in inst_list if i.current_parcel >= i.n_parcels]
    inst_list = [i for i in inst_list if i.current_parcel < i.n_parcels]
    hist_list.extend(expired)

    # agora inst_list tem só os não-vencidos, e hist_list recebeu todos expirados

    # --- 1) determina novo ID ---
    new_id = max((item.id for item in inst_list + hist_list), default=0) + 1

    # --- 2) parse do mês de início ---
    start_date = datetime.strptime(request.form['start_month'], "%Y-%m").date()

    # --- 3) calcula quantos meses se passaram (início conta como 1) ---
    today         = date.today()
    diff_months   = (today.year - start_date.year) * 12 + (today.month - start_date.month)
    months_passed = diff_months + 1

    total_parcels = int(request.form['n_parcels'])
    # clamp para [1, total_parcels]
    current = max(1, min(months_passed, total_parcels))

    # --- 4) cria o parcelamento ---
    inst = InstallmentExpense(
        id=new_id,
        name=request.form['name'],
        total=float(request.form['total']),
        n_parcels=total_parcels,
        start_month=start_date,
        current_parcel=current,
        paid=False,
        affiliate=request.form['affiliate']
    )

    # --- 5) adiciona no lugar certo ---
    if months_passed > total_parcels:
        # já expirou, vai pro histórico
        inst.current_parcel = total_parcels
        hist_list.append(inst)
    else:
        inst_list.append(inst)

    # --- 6) persiste as duas listas limpas ---
    repo.save_installments(inst_list)
    repo.save_history(hist_list)

    return redirect(url_for('index'))


# (Opcional) Rotas de delete
@app.route('/fixed/delete/<int:id>', methods=['POST'])
def delete_fixed(id):
    repo = get_repo()
    repo.save_fixed([fe for fe in repo.load_fixed() if fe.id != id])
    return ('', 204)

@app.route('/installments/delete/<int:id>', methods=['POST'])
def delete_installment(id):
    repo = get_repo()
    repo.save_installments([i for i in repo.load_installments() if i.id != id])
    return ('', 204)

@app.route('/config', methods=['POST'])
def update_config():
    repo = get_repo()
    cfg = repo.load_config()
    cfg.limit = float(request.form['limit'])
    repo.save_config(cfg)
    return redirect(url_for('index'))

@app.route('/fixed/edit/<int:id>', methods=['POST'])
def edit_fixed(id):
    repo = get_repo()
    fixed_list = repo.load_fixed()
    for fe in fixed_list:
        if fe.id == id:
            fe.name      = request.form['name']
            fe.value     = float(request.form['value'])
            fe.due_day   = int(request.form['due_day'])
            fe.affiliate = request.form['affiliate']
            break
    repo.save_fixed(fixed_list)
    return redirect(url_for('index'))

@app.route('/installments/edit/<int:id>', methods=['POST'])
def edit_installment(id):
    from datetime import datetime
    repo = get_repo()
    inst_list = repo.load_installments()
    for inst in inst_list:
        if inst.id == id:
            inst.name        = request.form['name']
            inst.total       = float(request.form['total'])
            inst.n_parcels   = int(request.form['n_parcels'])
            inst.start_month = datetime.strptime(request.form['start_month'], "%Y-%m").date()
            inst.affiliate   = request.form['affiliate']
            break
    repo.save_installments(inst_list)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)