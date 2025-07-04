from typing import List
from pathlib import Path
import json
from datetime import date

from domain.models import Budget, FixedExpense, InstallmentExpense

class JSONRepository:
    def __init__(self, path: str):
        self.path = Path(path)
        # 1) Garante que o diretório parent existe
        self.path.parent.mkdir(parents=True, exist_ok=True)
        # 2) Carrega ou inicializa o arquivo
        self._load()

    def _load(self):
        if not self.path.exists():
            # arquivo não existe: cria dados iniciais e já salva
            self.data = {
                "config": {},
                "fixed": [],
                "installments": [],
                "history": []
            }
            self._save()
        else:
            # lê o JSON existente
            text = self.path.read_text(encoding='utf-8')
            self.data = json.loads(text)

    def _save(self):
        with self.path.open('w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2, default=str)

    # --- Fixed expenses ---
    def load_fixed(self) -> List[FixedExpense]:
        return [FixedExpense(**f) for f in self.data["fixed"]]

    def save_fixed(self, fixed_list: List[FixedExpense]):
        self.data["fixed"] = [vars(f) for f in fixed_list]
        self._save()

    # --- Installments ---
    def load_installments(self) -> List[InstallmentExpense]:
        out = []
        for i in self.data["installments"]:
            sm = i.get("start_month")
            if isinstance(sm, str):
                i["start_month"] = date.fromisoformat(sm)
            out.append(InstallmentExpense(**i))
        return out

    def save_installments(self, inst_list: List[InstallmentExpense]):
        serializable = []
        for inst in inst_list:
            d = vars(inst).copy()
            sm = d.get("start_month")
            if isinstance(sm, date):
                d["start_month"] = sm.isoformat()
            serializable.append(d)
        self.data["installments"] = serializable
        self._save()

    # --- History ---
    def load_history(self) -> List[InstallmentExpense]:
        out = []
        for h in self.data["history"]:
            sm = h.get("start_month")
            if isinstance(sm, str):
                h["start_month"] = date.fromisoformat(sm)
            out.append(InstallmentExpense(**h))
        return out

    def save_history(self, hist_list: List[InstallmentExpense]):
        serializable = []
        for h in hist_list:
            d = vars(h).copy()
            sm = d.get("start_month")
            if isinstance(sm, date):
                d["start_month"] = sm.isoformat()
            serializable.append(d)
        self.data["history"] = serializable
        self._save()

    # --- Budget config ---
    def load_config(self) -> Budget:
        cfg = self.data.get("config", {})
        return Budget(month=cfg.get("month"), limit=cfg.get("budget", 0.0))

    def save_config(self, budget: Budget):
        self.data["config"] = {"month": budget.month, "budget": budget.limit}
        self._save()
