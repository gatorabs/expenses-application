from domain.models import FixedExpense, InstallmentExpense, Budget

class ExpenseService:
    def __init__(self, repo):
        # único repositório JSON para fixed, installments e history
        self.repo = repo

    def process_new_month(self, new_month):
        # 1) Resetar flag de pago nos gastos fixos
        fixed_list = self.repo.load_fixed()
        for fe in fixed_list:
            fe.paid = False
        self.repo.save_fixed(fixed_list)

        # 2) Avançar parcelas ou mover ao histórico
        inst_list = self.repo.load_installments()
        history_list = self.repo.load_history() or []

        new_active = []
        for inst in inst_list:
            # avança a parcela e reseta paid
            inst.current_parcel += 1
            inst.paid = False

            # só permanece ativo se ainda não tiver ultrapassado o total
            if inst.current_parcel > inst.n_parcels:
                history_list.append(inst)
            else:
                new_active.append(inst)

        # 3) Persiste listas atualizadas
        self.repo.save_installments(new_active)
        self.repo.save_history(history_list)

    def calculate_remaining(self, budget: Budget) -> float:
        # Soma todos os valores fixos (independente de pago)
        total_fixed = sum(fe.value for fe in self.repo.load_fixed())
        # Soma a parcela mensal de cada parcelamento ativo
        total_inst = sum(inst.total / inst.n_parcels for inst in self.repo.load_installments())
        return budget.limit - (total_fixed + total_inst)