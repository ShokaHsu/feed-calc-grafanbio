<template>
  <div class="swine-panel">
    <!-- 1. 能量與概略養分 -->
    <NutrientGroup 
      name="能量與概略養分" 
      color="#2563eb" 
      :status="energyStatus.status" 
      :count="energyStatus.count"
      :mode="mode"
    >
      <NutrientRow label="粗蛋白 (CP)" :current="data.cp" :target="getTarget('crude_protein_percent')" unit="%" accentColor="#2563eb" />
      <NutrientRow label="粗纖維 (CF)" :current="data.cf" :target="getTarget('crude_fiber_percent', true)" unit="%" isMax accentColor="#2563eb" />
      <NutrientRow label="粗脂肪 (EE)" :current="data.fat" :target="getTarget('crude_fat_percent')" unit="%" accentColor="#2563eb" />
      <NutrientRow label="粗灰分 (Ash)" :current="data.ash" :target="getTarget('ash_percent', true)" unit="%" isMax accentColor="#2563eb" />
      <NutrientRow label="消化能 (DE)" :current="data.de_pig" :target="getTarget('de_pig_kcal_per_kg')" unit="kcal" :decimals="0" accentColor="#2563eb" />
      <NutrientRow label="代謝能 (ME)" :current="data.me_pig" :target="getTarget('me_pig_kcal_per_kg')" unit="kcal" :decimals="0" accentColor="#2563eb" />
      <NutrientRow label="淨能 (NEg)" :current="data.ne_pig_g" :target="getTarget('ne_pig_growth_kcal_per_kg')" unit="kcal" :decimals="0" accentColor="#2563eb" />
    </NutrientGroup>

    <!-- 2. 胺基酸 -->
    <NutrientGroup 
      name="胺基酸" 
      color="#7c3aed" 
      :status="aaStatus.status" 
      :count="aaStatus.count"
      :mode="mode"
    >
      <NutrientRow label="離胺酸 (Lys)" :current="data.lys_total/10" :target="getTarget('lysine_total_g_kg')/10" unit="%" accentColor="#7c3aed" />
      <NutrientRow label="含硫胺基酸 (M+C)" :current="data.met_cys_total/10" :target="getTarget('met_cys_total_g_kg')/10" unit="%" accentColor="#7c3aed" />
      <NutrientRow label="甲硫胺酸 (Met)" :current="data.met_total/10" :target="getTarget('methionine_total_g_kg')/10" unit="%" accentColor="#7c3aed" />
      <NutrientRow label="羥丁胺酸 (Thr)" :current="data.thr_total/10" :target="getTarget('threonine_total_g_kg')/10" unit="%" accentColor="#7c3aed" />
      <NutrientRow label="色胺酸 (Trp)" :current="data.trp_total/10" :target="getTarget('tryptophan_total_g_kg')/10" unit="%" accentColor="#7c3aed" />
      
      <!-- 進階模式：顯示 SID -->
      <template v-if="mode === 'advanced'">
        <el-divider border-style="dashed" style="margin: 12px 0" />
        <NutrientRow label="SID-離胺酸" :current="data.lys_sid_pig/10" :target="getTarget('lysine_sid_pig_g_kg')/10" unit="%" accentColor="#7c3aed" />
        <NutrientRow label="SID-含硫胺基酸" :current="data.met_cys_sid_pig/10" :target="getTarget('met_cys_sid_pig_g_kg')/10" unit="%" accentColor="#7c3aed" />
        <NutrientRow label="SID-甲硫胺酸" :current="data.met_sid_pig/10" :target="getTarget('methionine_sid_pig_g_kg')/10" unit="%" accentColor="#7c3aed" />
        <NutrientRow label="SID-羥丁胺酸" :current="data.thr_sid_pig/10" :target="getTarget('threonine_sid_pig_g_kg')/10" unit="%" accentColor="#7c3aed" />
        <NutrientRow label="SID-色胺酸" :current="data.trp_sid_pig/10" :target="getTarget('tryptophan_sid_pig_g_kg')/10" unit="%" accentColor="#7c3aed" />
      </template>
    </NutrientGroup>

    <!-- 3. 礦物質 -->
    <NutrientGroup 
      name="礦物質" 
      color="#d97706" 
      :status="mineralsStatus.status" 
      :count="mineralsStatus.count"
      :initialCollapsed="mode === 'basic'"
      :mode="mode"
    >
      <NutrientRow label="鈣 (Ca)" :current="data.ca/10" :target="getTarget('calcium_g_per_kg')/10" unit="%" accentColor="#d97706" />
      <NutrientRow label="總磷 (P)" :current="data.p/10" :target="getTarget('phosphorus_g_per_kg')/10" unit="%" accentColor="#d97706" />
      <NutrientRow label="消化磷 (DP)" :current="data.avail_p/10" :target="getTarget('digestible_p_pig_no_phytase_g_kg')/10" unit="%" accentColor="#d97706" />
      <NutrientRow label="鈉 (Na)" :current="data.na/10" :target="getTarget('sodium_g_per_kg')/10" unit="%" accentColor="#d97706" />
      <NutrientRow label="氯 (Cl)" :current="data.cl/10" :target="getTarget('chloride_g_per_kg')/10" unit="%" accentColor="#d97706" />
      <NutrientRow label="鉀 (K)" :current="data.k/10" :target="getTarget('potassium_g_per_kg')/10" unit="%" accentColor="#d97706" />
      <NutrientRow label="鎂 (Mg)" :current="data.mg/10" :target="getTarget('magnesium_g_per_kg')/10" unit="%" accentColor="#d97706" />
    </NutrientGroup>

    <!-- 4. 維生素 (無目標值) -->
    <NutrientGroup 
      name="維生素" 
      color="#16a34a" 
      status="ok"
      :initialCollapsed="mode === 'basic'"
      :mode="mode"
    >
      <NutrientRow label="維生素 A" :current="data.vit_a" unit="KIU" accentColor="#16a34a" />
      <NutrientRow label="維生素 D" :current="data.vit_d" unit="KIU" accentColor="#16a34a" />
      <NutrientRow label="維生素 E" :current="data.vit_e" unit="mg" accentColor="#16a34a" />
      <NutrientRow label="維生素 K" :current="data.vit_k" unit="mg" accentColor="#16a34a" />
      <NutrientRow label="維生素 B1" :current="data.vit_b1" unit="mg" accentColor="#16a34a" />
      <NutrientRow label="維生素 B2" :current="data.vit_b2" unit="mg" accentColor="#16a34a" />
      <NutrientRow label="維生素 B6" :current="data.vit_b6" unit="mg" accentColor="#16a34a" />
      <NutrientRow label="維生素 B12" :current="data.vit_b12" unit="ug" accentColor="#16a34a" />
      <NutrientRow label="膽鹼 (Choline)" :current="data.choline" unit="mg" accentColor="#16a34a" />
      <NutrientRow label="生物素 (Biotin)" :current="data.biotin" unit="mcg" accentColor="#16a34a" />
    </NutrientGroup>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import NutrientRow from './NutrientRow.vue'
import NutrientGroup from './NutrientGroup.vue'
import { useGroupStatus } from '../../composables/useGroupStatus'

const props = defineProps({
  data: Object,
  standard: Object,
  mode: String
})

const getTarget = (key, isMax = false) => {
  if (!props.standard) return 0;
  const k = isMax ? `max_${key}` : `min_${key}`;
  return props.standard[k] !== undefined ? props.standard[k] : 0;
}

// 計算各群組狀態
const energyStatus = computed(() => {
  const nutrients = [
    { current: props.data.cp, target: getTarget('crude_protein_percent') },
    { current: props.data.cf, target: getTarget('crude_fiber_percent', true), isMax: true },
    { current: props.data.de_pig, target: getTarget('de_pig_kcal_per_kg') },
    { current: props.data.me_pig, target: getTarget('me_pig_kcal_per_kg') }
  ]
  return useGroupStatus(nutrients)
})

const aaStatus = computed(() => {
  const nutrients = [
    { current: props.data.lys_total/10, target: getTarget('lysine_total_g_kg')/10 },
    { current: props.data.met_cys_total/10, target: getTarget('met_cys_total_g_kg')/10 },
    { current: props.data.thr_total/10, target: getTarget('threonine_total_g_kg')/10 }
  ]
  
  if (props.mode === 'advanced') {
    nutrients.push(
      { current: props.data.lys_sid_pig/10, target: getTarget('lysine_sid_pig_g_kg')/10 },
      { current: props.data.met_cys_sid_pig/10, target: getTarget('met_cys_sid_pig_g_kg')/10 }
    )
  }
  return useGroupStatus(nutrients)
})

const mineralsStatus = computed(() => {
  const nutrients = [
    { current: props.data.ca/10, target: getTarget('calcium_g_per_kg')/10 },
    { current: props.data.p/10, target: getTarget('phosphorus_g_per_kg')/10 },
    { current: props.data.avail_p/10, target: getTarget('digestible_p_pig_no_phytase_g_kg')/10 }
  ]
  return useGroupStatus(nutrients)
})
</script>
