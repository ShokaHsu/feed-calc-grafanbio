import { calculateSwine } from './calculators/swine.js';
import { calculatePoultry } from './calculators/poultry.js';
import { calculateProximate } from './calculators/common.js';

export const calculateNutrients = (species, items, totalWeight) => {
    if (!items || items.length === 0 || totalWeight === 0) {
        // 回傳全 0 的安全物件 (避免前端 undefined)
        return { cp:0, cf:0, fat:0, me:0, lys:0, met:0, met_cys:0, thr:0, trp:0, ca:0, p:0, avail_p:0, na:0 };
    }

    switch (species) {
        case 'SWINE':
            return calculateSwine(items, totalWeight);
        case 'POULTRY':
            return calculatePoultry(items, totalWeight);
        default:
            // 預設回傳通用 (只算五大和礦物質，其他補 0)
            return { 
                ...calculateProximate(items, totalWeight), 
                me: 0, lys: 0, met: 0, met_cys: 0, thr: 0, trp: 0 
            };
    }
};