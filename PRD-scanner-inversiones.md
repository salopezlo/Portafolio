# PRD — Agente Scanner de Oportunidades de Inversión
**Versión:** 1.0  
**Fecha:** Mayo 2026  
**Autor:** Santi  
**Estado:** En construcción — Fase 2

---

## 0. Resumen ejecutivo

Agente automatizado que escanea el mercado completo diariamente, identifica las mejores oportunidades de inversión, genera análisis financiero detallado y produce un informe narrativo en español usando Claude API — integrado en portafolio-v5.html.

---

## 1. Problema y motivación

Santi invierte con metodología DCA en portafolio agresivo de largo plazo. Sin este sistema:
- Revisa manualmente cada activo cuando recuerda
- Sin visibilidad de oportunidades fuera de sus 7 tickers
- Sin análisis financiero profundo para respaldar decisiones
- Sin saber si hay mejores oportunidades en el resto del mercado

---

## 2. Arquitectura

```
GitHub Actions (4:30pm ET, lunes-viernes)
    → scanner.py
        → Yahoo Finance: precios, dip, rango 52s, momentum
        → FMP API: P/E, FCF, revenue growth, deuda, márgenes
        → Scoring engine: técnico 35% + fundamental 45% + analistas 20%
        → Claude API (Haiku): narrativa en español top 10
        → Commit opportunities.json al repo
    → GitHub Pages sirve portafolio-v5.html
        → Lee opportunities.json
        → Muestra scanner con análisis detallado on-click
```

---

## 3. Scoring (0–10)

| Componente | Peso | Señales |
|---|---|---|
| Técnico | 35% | Dip 30d + posición rango 52s + momentum 5d |
| Fundamental | 45% | Forward P/E + FCF yield + revenue growth + D/E |
| Analistas | 20% | Upside vs precio objetivo + consenso |

**Labels:** 8-10 Oportunidad fuerte · 6-8 Interesante · 4-6 Neutral · 2-4 Precaución · 0-2 Evitar

---

## 4. Universo de escaneo

- **ETFs:** VOO, QQQ, VTI, SPY, IVV, SCHD, VIG, GLD, SLV, SOXX, XLK, XLF, XLE, ARKK, IBIT, BND, AGG, VNQ, VWO
- **Stocks:** AAPL, MSFT, NVDA, AMZN, GOOGL, META, TSLA, BRK-B, AVGO, LLY, AMD, NFLX, CRM, ORCL, ADBE, NOW, SNOW, PLTR, ARM, TSM, JPM, V, MA, UNH, HD, COST, WMT, PG, JNJ, KO

---

## 5. Clasificación de riesgo

| Nivel | Criterio |
|---|---|
| 🟢 ETF | Fondos diversificados |
| 🟡 Mega cap | Market cap > $500B |
| 🟠 Large cap | Market cap $10B–$500B |
| 🔴 Especulativo | < $10B o sector emergente |

---

## 6. Stack técnico

| Componente | Tecnología | Costo |
|---|---|---|
| Hosting | GitHub Pages (salopezlo.github.io/Portafolio) | Gratis |
| Agente diario | GitHub Actions | Gratis |
| Datos precio | Yahoo Finance API | Gratis |
| Datos fundamentales | Financial Modeling Prep API | Gratis 250 calls/día |
| Análisis narrativo | Claude API Haiku | ~$0.003/análisis |

---

## 7. Fases

| Fase | Estado | Descripción |
|---|---|---|
| 1 | ✅ Completa | portafolio-v5.html funcional + GitHub Pages |
| 2 | 🔄 En progreso | scanner.py + GitHub Actions workflow |
| 3 | ⏳ Pendiente | FMP API → financials profundos |
| 4 | ⏳ Pendiente | Claude API → análisis narrativo |
| 5 | ⏳ Pendiente | UI scanner completa en portafolio-v5 |

---

## 8. Secrets requeridos en GitHub

- `FMP_KEY` — financialmodelingprep.com (gratis, sin tarjeta)
- `ANTHROPIC_KEY` — console.anthropic.com

---

## 9. Estructura del repo

```
salopezlo/Portafolio/
├── portafolio-v5.html      ← app principal (GitHub Pages)
├── scanner.py              ← agente Python
├── opportunities.json      ← generado por scanner (auto-commit)
├── PRD-scanner-inversiones.md
├── ABRIR-PORTAFOLIO.bat    ← uso local únicamente
└── .github/
    └── workflows/
        └── scanner.yml     ← GitHub Actions
```
