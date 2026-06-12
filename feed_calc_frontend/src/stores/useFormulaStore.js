// src/stores/useFormulaStore.js
import { defineStore } from 'pinia'
import { ref, computed, reactive, watch } from 'vue'
import request from '@/api/request'

export const useFormulaStore = defineStore('formula', () => {

    // ==========================================
    // 1. State (資料狀態)
    // ==========================================
    
    // --- 資料庫 ---
    const allStandards = ref([])     // 所有營養標準
    const allIngredients = ref([])   // 所有原料資料庫
    
    // --- 使用者選擇 ---
    const selectedSpecies = ref('')    // 目前選擇的物種
    const selectedStage = ref(null)    // 目前選擇的階段
    const targetStandardId = ref(null) // 目前選擇的標準 ID
    
    // --- 配方編輯區 ---
    const formulaItems = ref([]) // 已加入配方的原料列表

    // --- 計算結果 ---
    const calculated = reactive({ 
        // 基礎成分
        cp: 0, cf: 0, fat: 0, ash: 0, 
        
        // 能量
        de_pig: 0, me_pig: 0, ne_pig_g: 0, ne_pig_s: 0,
        amen_broiler: 0, amen_cockerel: 0,

        // 胺基酸 (Total)
        lys_total: 0, met_total: 0, met_cys_total: 0, thr_total: 0, 
        trp_total: 0, val_total: 0, ile_total: 0, 
        leu_total: 0, arg_total: 0, his_total: 0,
        
        // SID Pig
        lys_sid_pig: 0, met_sid_pig: 0, met_cys_sid_pig: 0, thr_sid_pig: 0, 
        trp_sid_pig: 0, val_sid_pig: 0, ile_sid_pig: 0, leu_sid_pig: 0,
        arg_sid_pig: 0, his_sid_pig: 0,
        
        // SID Poultry
        lys_sid_poultry: 0, met_sid_poultry: 0, met_cys_sid_poultry: 0, thr_sid_poultry: 0, 
        trp_sid_poultry: 0, val_sid_poultry: 0, ile_sid_poultry: 0, leu_sid_poultry: 0,
        arg_sid_poultry: 0, his_sid_poultry: 0,

        // 礦物質
        ca: 0, p: 0, avail_p: 0, na: 0, cl: 0, k: 0, mg: 0,
        
        // 維生素
        vit_a: 0, vit_d: 0, vit_e: 0, vit_k: 0,
        vit_b1: 0, vit_b2: 0, vit_b3: 0, vit_b5: 0, vit_b6: 0, vit_b12: 0,
        choline: 0, folic: 0, biotin: 0
    })

    // ==========================================
    // 2. Getters (計算屬性)
    // ==========================================
    
    const totalWeight = computed(() => formulaItems.value.reduce((s, i) => s + (i.amount || 0), 0))
    const totalCost = computed(() => formulaItems.value.reduce((s, i) => s + ((i.amount || 0) * (i.cost || 0)), 0))

    // 取得目前選中的標準詳細資料
    const targetStandardData = computed(() => {
        return allStandards.value.find(s => s.id === targetStandardId.value) || null
    })

    // 根據物種篩選可用的階段
    const availableStages = computed(() => {
        if (!selectedSpecies.value) return []
        const list = allStandards.value.filter(s => s.species === selectedSpecies.value)
        const unique = new Set(list.map(s => s.stage).filter(Boolean)); 
        const map = { 
            'NURSERY': '保育期', 'GROWER': '生長期', 'FINISHER': '肥育期', 
            'GESTATION': '懷孕期', 'LACTATION': '泌乳期', 
            'BROILER_STARTER': '肉雞前期', 'BROILER_GROWER': '肉雞中期', 
            'OTHER': '其他' 
        };
        return Array.from(unique).map(code => ({ value: code, label: map[code] || code })); 
    })

    // 根據階段篩選可用的標準
    const filteredStandards = computed(() => {
        if (!selectedSpecies.value || !selectedStage.value) return []
        const list = allStandards.value.filter(s => s.species === selectedSpecies.value && s.stage === selectedStage.value)
        const unique = new Set(); const opts = [];
        list.forEach(s => { 
            if (s.name && !unique.has(s.name)) { 
                unique.add(s.name); 
                opts.push({ id: s.id, name: s.name }) 
            } 
        });
        return opts;
    })

    // ==========================================
    // 3. Actions (邏輯與動作)
    // ==========================================

    // [API] 載入標準資料
    async function fetchStandards() {
        for (let attempt = 0; attempt < 3; attempt++) {
            try {
                const res = await request.get('standards/requirements/')
                allStandards.value = res.data.results || res.data;
                return;
            } catch (e) {
                if (attempt === 2) console.error("Store: 載入標準失敗", e);
                else await new Promise(r => setTimeout(r, 2000));
            }
        }
    }

    // [API] 載入所有原料
    async function fetchAllIngredients() {
        for (let attempt = 0; attempt < 3; attempt++) {
            try {
                const res = await request.get('ingredients/', { params: { page_size: 1000 } })
                allIngredients.value = res.data.results || res.data
                return;
            } catch (e) {
                if (attempt === 2) console.error("Store: 載入原料失敗", e);
                else await new Promise(r => setTimeout(r, 2000));
            }
        }
    }

    // 設定物種
    function setSpecies(val) {
        selectedSpecies.value = val
        selectedStage.value = null
        targetStandardId.value = null
    }

    // 設定階段
    function setStage(val) {
        selectedStage.value = val
        targetStandardId.value = null
    }

    function _formatIngredient(ing) {
        return {
            id: ing.id, name: ing.name, amount: 0, cost: ing.cost_per_kg_twd || 0,
            cp: ing.crude_protein_percent || 0, cf: ing.crude_fiber_percent || 0, fat: ing.crude_fat_percent || 0, ash: ing.ash_percent || 0,
            de_pig: ing.de_pig_kcal_per_kg || 0, me_pig: ing.me_pig_kcal_per_kg || 0, ne_pig_g: ing.ne_pig_growth_kcal_per_kg || 0, ne_pig_s: ing.ne_pig_sow_kcal_per_kg || 0,
            amen_broiler: ing.amen_broiler_kcal_per_kg || 0, amen_cockerel: ing.amen_cockerel_kcal_per_kg || 0,
            lys_total: ing.lysine_total_g_kg || 0, met_total: ing.methionine_total_g_kg || 0, met_cys_total: ing.met_cys_total_g_kg || 0, thr_total: ing.threonine_total_g_kg || 0, trp_total: ing.tryptophan_total_g_kg || 0, val_total: ing.valine_total_g_kg || 0, ile_total: ing.isoleucine_total_g_kg || 0, leu_total: ing.leucine_total_g_kg || 0, arg_total: ing.arginine_total_g_kg || 0, his_total: ing.histidine_total_g_kg || 0,
            lys_sid_pig: ing.lysine_sid_pig_g_kg || 0, met_sid_pig: ing.methionine_sid_pig_g_kg || 0, met_cys_sid_pig: ing.met_cys_sid_pig_g_kg || 0, thr_sid_pig: ing.threonine_sid_pig_g_kg || 0, trp_sid_pig: ing.tryptophan_sid_pig_g_kg || 0, val_sid_pig: ing.valine_sid_pig_g_kg || 0, ile_sid_pig: ing.isoleucine_sid_pig_g_kg || 0, leu_sid_pig: ing.leucine_sid_pig_g_kg || 0, arg_sid_pig: ing.arginine_sid_pig_g_kg || 0, his_sid_pig: ing.histidine_sid_pig_g_kg || 0,
            lys_sid_poultry: ing.lysine_sid_poultry_g_kg || 0, met_sid_poultry: ing.methionine_sid_poultry_g_kg || 0, met_cys_sid_poultry: ing.met_cys_sid_poultry_g_kg || 0, thr_sid_poultry: ing.threonine_sid_poultry_g_kg || 0, trp_sid_poultry: ing.tryptophan_sid_poultry_g_kg || 0, val_sid_poultry: ing.valine_sid_poultry_g_kg || 0, ile_sid_poultry: ing.isoleucine_sid_poultry_g_kg || 0, leu_sid_poultry: ing.leucine_sid_poultry_g_kg || 0, arg_sid_poultry: ing.arginine_sid_poultry_g_kg || 0, his_sid_poultry: ing.histidine_sid_poultry_g_kg || 0,
            ca: ing.calcium_g_per_kg || 0, p: ing.phosphorus_g_per_kg || 0, avail_p: ing.available_phosphorus_g_per_kg || 0, na: ing.sodium_g_per_kg || 0, cl: ing.chloride_g_per_kg || 0, k: ing.potassium_g_per_kg || 0, mg: ing.magnesium_g_per_kg || 0,
            vit_a: ing.vitamin_a_kiu_kg || 0, vit_d: ing.vitamin_d_kiu_kg || 0, vit_e: ing.vitamin_e_mg_kg || 0, vit_k: ing.vitamin_k_mg_kg || 0,
            vit_b1: ing.vitamin_b1_mg_kg || 0, vit_b2: ing.riboflavin_mg_kg || 0, vit_b3: ing.niacin_mg_kg || 0, vit_b5: ing.pantothenic_acid_mg_kg || 0, vit_b6: ing.vitamin_b6_mg_kg || 0, vit_b12: ing.vitamin_b12_ug_kg || 0,
            choline: ing.choline_mg_kg || 0, folic: ing.folic_acid_mg_kg || 0, biotin: ing.biotin_mcg_kg || 0
        }
    }

    function addIngredient(rawIngredient) {
        if (!rawIngredient) return false
        if (formulaItems.value.some(i => i.id === rawIngredient.id)) return false 
        formulaItems.value.push(_formatIngredient(rawIngredient))
        return true
    }

    function removeIngredient(index) {
        formulaItems.value.splice(index, 1)
    }
    
    function clearFormula() {
        formulaItems.value = []
    }

    function recalculate() {
        Object.keys(calculated).forEach(k => calculated[k] = 0)
        const w = totalWeight.value
        if (w === 0) return 
        let sums = { ...calculated }
        formulaItems.value.forEach(i => {
            const amt = i.amount || 0; if (amt === 0) return
            Object.keys(sums).forEach(key => {
                if (i[key] !== undefined) sums[key] += amt * i[key]
            })
        })
        Object.keys(sums).forEach(k => calculated[k] = sums[k] / w)
    }

    watch(formulaItems, () => recalculate(), { deep: true })

    return {
        // State
        allStandards,
        allIngredients, 
        selectedSpecies,
        selectedStage,
        targetStandardId,
        formulaItems,
        calculated,
        
        // Getters
        totalWeight,
        totalCost,
        targetStandardData,
        availableStages,
        filteredStandards,
        
        // Actions
        fetchStandards,     
        fetchAllIngredients,
        setSpecies,         
        setStage,           
        addIngredient,
        removeIngredient,
        clearFormula,
        recalculate
    }
})
