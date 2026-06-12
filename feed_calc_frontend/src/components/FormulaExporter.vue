<template>
  <el-dialog 
    v-model="visible" 
    title="配方報表預覽" 
    width="800px"  
    top="5vh" 
    destroy-on-close
    :close-on-click-modal="false"
    class="export-dialog"
  >
    <div class="no-print" style="margin-bottom: 20px; display: flex; gap: 10px; justify-content: flex-end;">
      <el-button type="primary" @click="downloadCSV">
        <el-icon style="margin-right: 5px"><Document /></el-icon> 下載 CSV
      </el-button>
      <el-button type="danger" @click="handlePrint">
        <el-icon style="margin-right: 5px"><Printer /></el-icon> 列印 / 另存PDF
      </el-button>
    </div>

    <div id="print-area" class="print-container">
      
      <div class="report-header">
        <h1>飼料配方分析報告</h1>
        <div class="meta-grid">
            <div class="meta-row">
                <span class="label">配方名稱:</span> 
                <span class="value">{{ data.meta.recipeName || '未命名' }}</span>
            </div>
            <div class="meta-row">
                <span class="label">客戶名稱:</span> 
                <span class="value">{{ data.meta.customerName || '-' }}</span>
            </div>
            <div class="meta-row">
                <span class="label">適用物種:</span> 
                <span class="value">{{ data.meta.species }} / {{ data.meta.stage }}</span>
            </div>
            <div class="meta-row">
                <span class="label">列印日期:</span> 
                <span class="value">{{ data.meta.date }}</span>
            </div>
            <div class="meta-row full">
                <span class="label">參考標準:</span> 
                <span class="value">{{ data.meta.standardName || '無' }}</span>
            </div>
        </div>
      </div>

      <div class="summary-box">
        <div class="sum-item">總重量: <b>{{ data.totals.weight }} kg</b></div>
        <div class="sum-item">總成本: <b>${{ formatNumber(data.totals.cost, 0) }}</b></div>
        <div class="sum-item">平均單價: <b>${{ data.totals.unitCost }} / kg</b></div>
      </div>

      <h3 class="section-title">1. 原料組成 (Formula Composition)</h3>
      <table class="report-table">
        <thead>
          <tr>
            <th style="width: 50%">原料名稱</th>
            <th style="width: 25%; text-align: right;">使用量 (kg)</th>
            <th style="width: 25%; text-align: right;">佔比 (%)</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in data.items" :key="item.id">
            <td>{{ item.name }}</td>
            <td class="text-right">{{ item.amount }}</td>
            <td class="text-right">{{ item.percentage }}%</td>
          </tr>
        </tbody>
      </table>

      <h3 class="section-title">2. 營養預估 (Calculated Analysis)</h3>
      <table class="report-table analysis-table">
        <thead>
          <tr>
            <th style="width: 45%">項目</th>
            <th style="width: 30%; text-align: right;">計算值</th>
            <th style="width: 25%; text-align: right;">單位</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="(groupItems, groupKey) in data.nutrients" :key="groupKey">
            <tr v-if="groupItems && groupItems.length > 0" class="group-header">
               <td colspan="3">{{ getGroupTitle(groupKey) }}</td>
            </tr>
            <tr v-for="item in groupItems" :key="item.label">
                <td class="indent">{{ item.label }}</td>
                <td class="text-right">{{ formatNumber(item.current, item.decimals) }}</td>
                <td class="text-right">{{ item.unit }}</td>
            </tr>
          </template>
        </tbody>
      </table>
      
      <div class="footer-note">
        <p>備註: {{ data.meta.description || '無' }}</p>
        <p style="margin-top: 5px; font-size: 10px; color: #999;">本報表由配方計算系統自動生成</p>
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { computed } from 'vue'
import { Document, Printer } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: Boolean,
  data: Object
})
const emit = defineEmits(['update:modelValue'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const getGroupTitle = (key) => {
    const titles = {
        proximate: '基礎營養 (Proximate)',
        energy: '能量指標 (Energy)',
        amino_acids: '胺基酸組成 (Amino Acids)',
        minerals: '礦物質 (Minerals)'
    }
    return titles[key] || key
}

const formatNumber = (val, decimals = 2) => {
    if (val === undefined || val === null) return '-'
    // 如果 decimals 是 undefined，預設為 2
    const d = decimals === undefined ? 2 : decimals
    return Number(val).toFixed(d)
}

const handlePrint = () => {
    // 1. 抓取原本報表區塊的 HTML 內容
    const printContent = document.getElementById('print-area').innerHTML;
    
    // 2. 建立一個全新的 div 容器
    const printDiv = document.createElement('div');
    printDiv.id = 'print-wrapper'; // 給它一個專屬 ID
    printDiv.innerHTML = printContent; // 把內容塞進去
    
    // 3. 把這個新容器直接掛載到 body 的最尾端 (跳脫 Dialog/Vue App 的層級)
    document.body.appendChild(printDiv);
    
    // 4. 觸發列印 (瀏覽器會看到這個位於最上層的 div)
    window.print();
    
    // 5. 列印視窗關閉後，馬上移除這個暫時的 div，恢復原狀
    document.body.removeChild(printDiv);
}

const downloadCSV = () => {
    const d = props.data
    if (!d) return

    const esc = (val) => {
        const str = String(val ?? '')
        return str.includes(',') || str.includes('"') || str.includes('\n')
            ? `"${str.replace(/"/g, '""')}"`
            : str
    }

    const rows = []

    // Meta
    rows.push([esc('配方名稱'), esc(d.meta.recipeName)])
    rows.push([esc('客戶名稱'), esc(d.meta.customerName)])
    rows.push([esc('物種/階段'), esc(`${d.meta.species} / ${d.meta.stage}`)])
    rows.push([esc('參考標準'), esc(d.meta.standardName)])
    rows.push([esc('日期'), esc(d.meta.date)])
    rows.push([esc('備註'), esc(d.meta.description)])
    rows.push([])

    // Totals
    rows.push([esc('總重量 (kg)'), esc(d.totals.weight)])
    rows.push([esc('總成本 (TWD)'), esc(d.totals.cost)])
    rows.push([esc('平均單價 (TWD/kg)'), esc(d.totals.unitCost)])
    rows.push([])

    // Composition
    rows.push([esc('原料名稱'), esc('使用量 (kg)'), esc('佔比 (%)')])
    d.items.forEach(item => {
        rows.push([esc(item.name), esc(item.amount), esc(item.percentage)])
    })
    rows.push([])

    // Nutrients
    rows.push([esc('營養項目'), esc('計算值'), esc('目標值'), esc('單位')])
    const groupTitles = {
        proximate: '基礎營養 (Proximate)',
        energy: '能量指標 (Energy)',
        amino_acids: '胺基酸組成 (Amino Acids)',
        minerals: '礦物質 (Minerals)'
    }
    Object.entries(d.nutrients).forEach(([key, groupItems]) => {
        if (groupItems && groupItems.length > 0) {
            rows.push([esc(groupTitles[key] || key)])
            groupItems.forEach(n => {
                rows.push([
                    esc(n.label),
                    esc(formatNumber(n.current, n.decimals)),
                    n.target != null && n.target !== 0 ? esc(formatNumber(n.target, n.decimals)) : esc('-'),
                    esc(n.unit)
                ])
            })
        }
    })

    const csvContent = rows.map(r => r.join(',')).join('\n')
    // UTF-8 BOM ensures Excel opens Chinese characters correctly
    const blob = new Blob(['﻿' + csvContent], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${d.meta.recipeName || '配方'}_${d.meta.date}.csv`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
}
</script>

<style scoped>
/* === 預覽視窗容器 === */
.preview-container {
  padding: 40px;
  background: white;
  min-height: 800px;
  box-shadow: 0 0 10px rgba(0,0,0,0.1);
  font-family: "Microsoft JhengHei", "Arial", sans-serif;
}

/* === 1. 標題與 Meta Grid (您想要保留的排版) === */
.report-header h1 {
  text-align: center; 
  font-size: 22px; 
  margin-bottom: 20px; 
  border-bottom: 2px solid #333; 
  padding-bottom: 10px;
  color: #333;
}

.meta-grid { 
  display: flex; 
  flex-wrap: wrap; 
  gap: 10px; 
  margin-bottom: 20px; 
  font-size: 14px; 
}

.meta-row { 
  width: 48%; /* 左右兩欄 */
  border-bottom: 1px solid #eee; 
  padding: 5px 0; 
}

.meta-row.full { 
  width: 100%; /* 單欄 */
}

.label { 
  font-weight: bold; 
  color: #555; 
  margin-right: 5px; 
}

/* === 2. 總結框 === */
.summary-box { 
  display: flex; 
  justify-content: space-around; 
  background-color: #f8f9fa; 
  padding: 10px; 
  border: 1px solid #ddd; 
  margin-bottom: 20px; 
  border-radius: 4px; 
}

/* === 3. 區塊標題 === */
.section-title { 
  font-size: 16px; 
  border-left: 4px solid #409EFF; 
  padding-left: 8px; 
  margin: 20px 0 10px 0; 
  background: #f2f2f2; 
  padding: 5px 10px; 
  color: #303133;
}

/* === 4. 表格樣式 (淺色邊框) === */
.report-table { 
  width: 100%; 
  border-collapse: collapse; 
  font-size: 13px; 
}

.report-table th, .report-table td { 
  border: 1px solid #ccc; /* 您指定的淺色邊框 */
  padding: 6px 8px; 
}

.report-table th { 
  background-color: #f5f5f5; 
  font-weight: bold;
  color: #333;
}

.group-header td { 
  background-color: #eef1f6; 
  font-weight: bold; 
  color: #333; 
}

.text-right { text-align: right; }
.indent { padding-left: 20px; }

/* === Footer === */
.footer-note {
  margin-top: 30px;
  font-size: 12px;
  color: #666;
  text-align: center;
  border-top: 1px solid #eee;
  padding-top: 10px;
}
</style>

<style>
/* === 針對列印時的微調 === */
@media print {
  @page { margin: 10mm; size: A4; }

  /* 隱藏網頁雜訊 */
  body > *:not(#print-wrapper) { display: none !important; }
  .el-overlay, .el-dialog__header, .el-dialog__footer, .no-print, .toolbar { display: none !important; }

  /* 顯示報表容器 */
  #print-wrapper, #export-content {
    display: block !important;
    position: absolute; top: 0; left: 0; width: 100%;
    background: white !important;
    color: #333 !important; /* 強制文字深灰 */
    z-index: 99999;
  }

  /* ⚠️ 關鍵修正：強制表格線條為 #333 (深灰色) */
  #export-content .report-table th,
  #export-content .report-table td {
    border: 1px solid #333 !important; 
    color: #333 !important;
  }

  /* 標題與裝飾線 */
  #export-content .report-header h1 { border-bottom: 2px solid #333 !important; }
  #export-content .section-title { 
    border-left: 4px solid #333 !important; 
    background: none !important; 
  }
  
  /* Meta Grid 底線 */
  #export-content .meta-row { border-bottom: 1px solid #333 !important; }
}
</style>