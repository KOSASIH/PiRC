import { normalizeMicrosToMacro, calculateWcfParity } from './calculations.js';

// Configuration
const REFRESH_INTERVAL_MS = 5000; // 5 seconds for simulation fidelity

// Multilingual translations database
const translations = {
    en: {
        metrics_iou_price: "IOU Speculative Parity",
        metrics_wcf_price: "Vanguard Bridge Backed Parity ($WCF)",
        metrics_wcf_ref: "Conceptual Pioneer Equity ($REF)",
        col_hash: "TX HASH",
        col_class: "CLASSIFICATION",
        col_micros: "CEX MICROS",
        col_macro: "MACRO PI",
        col_ref: "WEIGHTED (REF)",
        chart_title: "IOU Price Visualization (Simulation)",
        ledger_title: "Vanguard Bridge Telemetry Ledger",
        footer_disclaimer: "This interface is a research prototype visualizing PiRC-101 conceptual modeling. It is NOT an official Pi Network utility."
    },
    ar: {
        metrics_iou_price: "تكافؤ IOU المضاربي",
        metrics_wcf_price: "تكافؤ الأوزان المدعوم ($WCF)",
        metrics_wcf_ref: "قيمة حقوق الرواد المرجحة ($REF)",
        col_hash: "TX HASH",
        col_class: "التصنيف",
        col_micros: "CEX MICROS",
        col_macro: "MACRO PI",
        col_ref: "الوزن المرجح",
        chart_title: "تصور سعر IOU (محاكاة)",
        ledger_title: "دفتر الأستاذ للقياس العادل",
        footer_disclaimer: "هذه الواجهة عبارة عن نموذج بحثي لتصور نمذجة PiRC-101 المفاهيمية. إنها ليست أداة رسمية لشبكة Pi."
    },
    zh: {
        metrics_iou_price: "IOU 投机性挂钩",
        metrics_wcf_price: "Vanguard Bridge 支持挂钩 ($WCF)",
        metrics_wcf_ref: "概念先锋权益 ($REF)",
        col_hash: "TX HASH",
        col_class: "分类",
        col_micros: "CEX MICROS",
        col_macro: "MACRO PI",
        col_ref: "加权 (REF)",
        chart_title: "IOU 价格可视化（模拟）",
        ledger_title: "公正遥测账本",
        footer_disclaimer: "此界面是可视化 PiRC-101 概念建模的研究原型。不是官方 Pi Network 实用程序。"
    },
    id: {
        metrics_iou_price: "Paritas Spekulatif IOU",
        metrics_wcf_price: "Paritas Didukung Vanguard Bridge ($WCF)",
        metrics_wcf_ref: "Ekuitas Pionir Konseptual ($REF)",
        col_hash: "TX HASH",
        col_class: "KLASIFIKASI",
        col_micros: "CEX MICROS",
        col_macro: "MACRO PI",
        col_ref: "TERBOBOT (REF)",
        chart_title: "Visualisasi Harga IOU (Simulasi)",
        ledger_title: "Buku Besar Telemetri Keadilan",
        footer_disclaimer: "Antarmuka ini adalah prototipe penelitian yang memvisualisasikan pemodelan konseptual PiRC-101. Ini BUKAN utilitas resmi Pi Network."
    },
    fr: {
        metrics_iou_price: "Parité spéculative IOU",
        metrics_wcf_price: "Parité soutenue Vanguard Bridge ($WCF)",
        metrics_wcf_ref: "Fonds propres conceptuels des Pionniers ($REF)",
        col_hash: "HASH TX",
        col_class: "CLASSIFICATION",
        col_micros: "MICROS CEX",
        col_macro: "MACRO PI",
        col_ref: "PONDÉRÉ (REF)",
        chart_title: "Visualisation du prix IOU (Simulation)",
        ledger_title: "Registre de télémétrie de justice",
        footer_disclaimer: "Cette interface est un prototype de recherche visualisant la modélisation conceptuelle PiRC-101. Ce n'est PAS un utilitaire officiel de Pi Network."
    },
    ms: {
        metrics_iou_price: "Pariti Spekulatif IOU",
        metrics_wcf_price: "Pariti Disokong Vanguard Bridge ($WCF)",
        metrics_wcf_ref: "Ekuiti Pionir Konseptual ($REF)",
        col_hash: "HASH TX",
        col_class: "KLASIFIKASI",
        col_micros: "CEX MICROS",
        col_macro: "MACRO PI",
        col_ref: "DITIMBANG (REF)",
        chart_title: "Visualisasi Harga IOU (Simulasi)",
        ledger_title: "Lejar Telemetri Keadilan",
        footer_disclaimer: "Antaramuka ini adalah prototaip penyelidikan yang memvisualisasikan pemodelan konseptual PiRC-101. Ia BUKAN utiliti rasmi Pi Network."
    }
};

// Global Fiat Currency & Exchange Rates (Conceptual Telemetry)
const FIAT_CURRENCY_DATA = {
    USD: { symbol: "$", rate: 1.0 },
    JOD: { symbol: "د.أ", rate: 0.71 },
    EGP: { symbol: "ج.م", rate: 47.90 },
    SAR: { symbol: "ر.س", rate: 3.75 },
    TND: { symbol: "د.ت", rate: 3.10 },
    EUR: { symbol: "€", rate: 0.92 },
    JPY: { symbol: "¥", rate: 150.45 }
};

let currentLang = 'en';
let selectedCurrency = 'USD';

/**
 * Changes the interface language and adjusts text direction
 * @param {string} lang - The language code (en, ar, etc.).
 */
export function changeLanguage(lang) {
    currentLang = lang;
    // Ar requires full Right-to-Left interface flip
    document.body.dir = (lang === 'ar') ? 'rtl' : 'ltr'; 
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (translations[lang] && translations[lang][key]) {
            el.innerText = translations[lang][key];
        }
    });
}

/**
 * Handles currency switching for the entire dashboard
 */
export function handleCurrencyChange(event) {
    selectedCurrency = event.target.value;
    syncTelemetry(); // Refresh data with new conversion rate
}

// Chart Initialization
const chart = LightweightCharts.createChart(document.getElementById('main-chart'), {
    layout: { background: { color: 'transparent' }, textColor: '#c9d1d9' },
    grid: { vertLines: { color: '#30363d' }, horzLines: { color: '#30363d' } }
});
const lineSeries = chart.addLineSeries({ color: '#ffa500' });

/**
 * Fetches conceptual telemetry data and updates the UI ledger.
 */
async function syncTelemetry() {
    try {
        // Calling backend Netlify Functions for secure real-world information
        // Prices are strictly marked as speculative IOU instruments.
        const priceRes = await fetch('/.netlify/functions/prices'); 
        const priceData = await priceRes.json();
        const baseIouPriceUsd = priceData.iouPrice; // Base IOU price from OKX/MEXC in USD
        
        // Trades are simulated to show Micro vs Macro transformation
        const tradeRes = await fetch('/.netlify/functions/telemtry_sim');
        const tradeData = await tradeRes.json();

        // Local Fiat Currency Conversion
        const currencyInfo = FIAT_CURRENCY_DATA[selectedCurrency];
        const convertedIouPrice = baseIouPriceUsd * currencyInfo.rate;

        // Update Price Cards with correct currency labeling
        document.getElementById('ext-price-val').innerText = `${currencyInfo.symbol} ${convertedIouPrice.toFixed(2)} (Speculative IOU)`;
        
        // Update Chart visualization
        lineSeries.update({ time: Math.floor(Date.now() / 1000), value: convertedIouPrice });

        // Ledger Population showing Micro vs. Macro logic
        const ledgerBody = document.getElementById('ledger-body');
        ledgerBody.innerHTML = ''; // clear existing data

        tradeData.trades.forEach(t => {
            const macroPi = normalizeMicrosToMacro(t.microAmount);
            const wcfParityUsd = calculateWcfParity(macroPi, t.refMultiplier);
            const convertedWcfParity = wcfParityUsd * currencyInfo.rate;

            const row = `<tr>
                <td>${t.txHash.substring(0,8)}...</td>
                <td class="classification-${t.classification}">${t.classification}</td>
                <td style="font-family: monospace;">${t.microAmount.toLocaleString()} MICROS</td> <td style="font-family: monospace; font-weight: bold;">${macroPi.toLocaleString()} π</td> <td style="color: #3fb950; font-weight:bold;">${convertedWcfParity.toLocaleString()} ${selectedCurrency} (WCF)</td> </tr>`;
            ledgerBody.insertAdjacentHTML('beforeend', row);
        });
        
    } catch (e) {
        console.error("Telemetry sync failed (ensure netlify is running):", e);
    }
}

// Global scope definition for HTML onclick triggers
window.changeLanguage = changeLanguage;
window.handleCurrencyChange = handleCurrencyChange;

// Initial Start
setInterval(syncTelemetry, REFRESH_INTERVAL_MS);
syncTelemetry();
changeLanguage('en'); // Default to English for international reviewers

