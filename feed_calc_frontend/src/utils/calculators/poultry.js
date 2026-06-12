//雞專用：Total AA, AMEn

import { weightedAvg, calculateProximate } from './common.js';

export const calculatePoultry = (items, w) => {
    const base = calculateProximate(items, w);
    return {
        ...base, 
        
        // 雞專用能量
        amen_broiler: weightedAvg(items, 'amen_broiler', w),
        amen_broiler: weightedAvg(items, 'amen_cockerel', w),

        
        // 雞專用 Total 胺基酸
        lys: weightedAvg(items, 'lys_total', w),
        met: weightedAvg(items, 'met_total', w),
        met_cys: weightedAvg(items, 'met_cys_total', w),
        thr: weightedAvg(items, 'thr_total', w),
        trp: weightedAvg(items, 'trp_total', w),
    };
};