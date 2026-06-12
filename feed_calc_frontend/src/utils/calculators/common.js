// 通用：五大營養、礦物質

export const weightedAvg = (items, key, totalWeight) => {
    if (!totalWeight || totalWeight === 0) return 0;
    let sum = items.reduce((acc, item) => {
        const val = parseFloat(item[key]) || 0;
        return acc + (item.amount * val);
    }, 0);
    return sum / totalWeight;
};

export const calculateProximate = (items, w) => ({
    cp: weightedAvg(items, 'cp', w),
    cf: weightedAvg(items, 'cf', w),
    fat: weightedAvg(items, 'fat', w),
    ca: weightedAvg(items, 'ca', w),
    p: weightedAvg(items, 'p', w),
    avail_p: weightedAvg(items, 'avail_p', w),
    na: weightedAvg(items, 'na', w),
});