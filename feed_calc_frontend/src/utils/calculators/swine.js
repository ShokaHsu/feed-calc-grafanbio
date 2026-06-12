//豬專用：SID, ME Pig

import { weightedAvg, calculateProximate } from './common.js';

export const calculateSwine = (items, w) => {
    const base = calculateProximate(items, w);
    return {
        ...base, // 繼承通用屬性
        
        // 豬專用能量
        me: weightedAvg(items, 'me_pig', w), 
        
        // 豬專用 SID 胺基酸
        lys: weightedAvg(items, 'lys_sid', w),
        met: weightedAvg(items, 'met_sid', w),
        met_cys: weightedAvg(items, 'met_cys_sid', w),
        thr: weightedAvg(items, 'thr_sid', w),
        trp: weightedAvg(items, 'trp_sid', w),
    };
};