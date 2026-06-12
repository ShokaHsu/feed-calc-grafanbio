/**
 * useGroupStatus - 計算養分群組的狀態（正常、缺乏、過剩）
 * @param {Array} nutrients - 養分資料陣列 [{ current, target, isMax }, ...]
 * @returns {Object} { status: 'ok' | 'deficient' | 'excess', count: number }
 */
export function useGroupStatus(nutrients) {
  let deficientCount = 0;
  let excessCount = 0;

  nutrients.forEach(n => {
    // 沒設定目標的不列入計算
    if (!n.target || n.target <= 0) return;

    if (n.isMax) {
      // 上限檢查
      if (n.current > n.target) excessCount++;
    } else {
      // 下限檢查
      if (n.current < n.target) deficientCount++;
    }
  });

  if (deficientCount > 0) {
    return { status: 'deficient', count: deficientCount };
  }
  
  if (excessCount > 0) {
    return { status: 'excess', count: excessCount };
  }

  return { status: 'ok', count: 0 };
}
