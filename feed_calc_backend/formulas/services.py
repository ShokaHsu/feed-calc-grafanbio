from django.db.models import Sum
from .models import Formula

class FormulaService:
    @staticmethod
    def calculate_and_save(formula: Formula):
        """
        計算配方的總重、總成本、單價，並更新 Formula 主表的快照欄位。
        """
        
        # 使用 select_related 預先抓取原料的價格，提高效率
        items = formula.items.select_related('ingredient').all()
        
        total_weight = 0.0
        total_cost = 0.0
        
        # 遍歷明細，計算成本
        for item in items:
            weight = item.amount_kg
            price = item.ingredient.cost_per_kg_twd or 0.0
            
            total_weight += weight
            total_cost += weight * price
        
        # 更新 Formula 主檔的快照 (Snapshot)
        formula.batch_size = total_weight
        formula.total_cost = total_cost
        
        if total_weight > 0:
            formula.cost_per_kg = total_cost / total_weight
        else:
            formula.cost_per_kg = 0.0
            
        # 儲存到資料庫
        formula.save()
        
        return formula