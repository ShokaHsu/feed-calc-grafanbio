<template>
  <div class="general-panel">
    <el-alert 
      title="未選擇標準，僅顯示計算值" 
      type="info" 
      :closable="false" 
      style="margin-bottom: 20px;" 
      show-icon
    />

    <!-- 1. 能量與概略養分 -->
    <NutrientGroup 
      name="能量與概略養分" 
      color="#2563eb" 
      :mode="mode"
    >
      <NutrientRow label="粗蛋白 (CP)" :current="data.cp" unit="%" accentColor="#2563eb" />
      <NutrientRow label="粗纖維 (CF)" :current="data.cf" unit="%" accentColor="#2563eb" />
      <NutrientRow label="粗脂肪 (EE)" :current="data.fat" unit="%" accentColor="#2563eb" />
      <NutrientRow label="粗灰分 (Ash)" :current="data.ash" unit="%" accentColor="#2563eb" />
      <NutrientRow label="代謝能 (ME)" :current="data.me_pig" unit="kcal" :decimals="0" accentColor="#2563eb" />
    </NutrientGroup>

    <!-- 2. 胺基酸 -->
    <NutrientGroup 
      name="胺基酸" 
      color="#7c3aed" 
      :mode="mode"
    >
      <NutrientRow label="離胺酸 (Lys)" :current="data.lys_total/10" unit="%" accentColor="#7c3aed" />
      <NutrientRow label="含硫胺基酸 (M+C)" :current="data.met_cys_total/10" unit="%" accentColor="#7c3aed" />
      <NutrientRow label="羥丁胺酸 (Thr)" :current="data.thr_total/10" unit="%" accentColor="#7c3aed" />
      <NutrientRow label="色胺酸 (Trp)" :current="data.trp_total/10" unit="%" accentColor="#7c3aed" />
    </NutrientGroup>

    <!-- 3. 礦物質 -->
    <NutrientGroup 
      name="礦物質" 
      color="#d97706" 
      :initialCollapsed="mode === 'basic'"
      :mode="mode"
    >
      <NutrientRow label="鈣 (Ca)" :current="data.ca/10" unit="%" accentColor="#d97706" />
      <NutrientRow label="總磷 (P)" :current="data.p/10" unit="%" accentColor="#d97706" />
      <NutrientRow label="有效磷 (Avail.P)" :current="data.avail_p/10" unit="%" accentColor="#d97706" />
    </NutrientGroup>

    <!-- 4. 維生素 -->
    <NutrientGroup 
      name="維生素" 
      color="#16a34a" 
      :initialCollapsed="mode === 'basic'"
      :mode="mode"
    >
      <NutrientRow label="維生素 A" :current="data.vit_a" unit="KIU" accentColor="#16a34a" />
      <NutrientRow label="維生素 E" :current="data.vit_e" unit="mg" accentColor="#16a34a" />
      <NutrientRow label="維生素 B12" :current="data.vit_b12" unit="ug" accentColor="#16a34a" />
    </NutrientGroup>
  </div>
</template>

<script setup>
import NutrientRow from './NutrientRow.vue'
import NutrientGroup from './NutrientGroup.vue'

defineProps({
  data: Object,
  mode: String
})
</script>
