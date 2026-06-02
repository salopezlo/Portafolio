# BITÁCORA — SESIÓN JUNIO 2026
**Proyecto:** Portafolio de Inversiones
**Fecha:** 1-2 de junio de 2026
**Estado al cierre:** Sistema completo en producción

---

## RESUMEN DE LO CONSTRUIDO

### 1. Rediseño visual completo (portafolio-v4 → v5)
- Paleta: dorado → esmeralda `#00c896`
- Tipografía: Syne/IBM Plex Mono → Figtree + DM Mono
- Hero card con número patrimonio más prominente
- Brand dot con glow esmeralda
- Sidebar con borde activo esmeralda
- Clases CSS faltantes agregadas: `.nt`, `.clabel-inline`

### 2. Fix gráficas Chart.js
- Problema raíz: canvas con dimensiones 0 al pasar de display:none → display:block
- Solución: `IntersectionObserver` + `responsive:false` + dimensiones explícitas via `window.innerWidth`
- Función `_triggerChart()` como helper universal

### 3. Historial & Activos — rediseño
- Gráfica compacta (~180px) arrastrable con drag handle esmeralda
- Panel de análisis en grid 2×2 al lado: Tesis / Por década / DCA / Riesgos+TER
- Banner stats: 1.5rem font-weight 700
- Datos para 7 activos: S&P500, QQQ, VTI, SCHD, Oro, Bonos, Bitcoin

### 4. Analizar activo (nueva página)
- Fetch Yahoo Finance v8 + v7
- Score de oportunidad 0-10 con desglose técnico/fundamental/analistas
- Rango 52 semanas visual
- Métricas: P/E, forward P/E, EPS, beta, dividendo, market cap, FCF yield
- Consenso analistas: precio objetivo, upside, recomendación
- Señal DCA directa + botón ir a Bitácora

### 5. CORS — solución definitiva
- Problema: Yahoo Finance bloquea fetch desde file:// y GitHub Pages
- Solución: GitHub Pages como hosting (origen válido)
- ABRIR-PORTAFOLIO.bat para uso local con servidor Python

### 6. Scanner de Oportunidades (nueva página + agente)
- `scanner.py` — agente Python que escanea 49 activos
- `.github/workflows/scanner.yml` — GitHub Actions, corre 4:30pm ET L-V
- Yahoo Finance: precios, dip 30d, rango 52s, momentum
- FMP API: P/E, FCF, revenue growth, márgenes, deuda
- Score compuesto: técnico 35% + fundamental 45% + analistas 20%
- Clasificación riesgo: ETF / Mega cap / Large cap / Especulativo
- Narrativa Gemini Flash (free tier) para top 10 activos
- `opportunities.json` committeado al repo automáticamente
- Clic en activo → análisis detallado con score breakdown + narrativa

### 7. GitHub Pages deployment
- Repo: `github.com/salopezlo/Portafolio` (público)
- URL: `salopezlo.github.io/Portafolio/portafolio-v5.html`
- Secrets configurados: FMP_KEY, GEMINI_KEY, ANTHROPIC_KEY
- Scanner corriendo automáticamente en producción ✅

---

## DECISIONES TOMADAS

| Decisión | Razón |
|---|---|
| Gemini Flash en lugar de Claude Haiku | Free tier, suficiente calidad |
| GitHub Pages público | Gratis, CORS resuelto |
| JSON pre-generado en lugar de fetch on-demand | Sin costo por clic, sin CORS |
| IntersectionObserver para charts | Más confiable que setTimeout |
| FMP free tier (250 calls/día) | Sin costo, cubre el universo |

---

## PENDIENTE PARA PRÓXIMA SESIÓN

- [ ] Reglas del Portafolio: más detalladas y explicativas
- [ ] Gráfico de distribución satélites + acciones principales
- [ ] Actualizar Node.js en workflow (warning Node.js 20)
- [ ] Expandir universo de escaneo (actualmente 49 activos)
- [ ] Mejorar scoring: sector P/E comparison
- [ ] Dashboard: integrar top oportunidades del scanner

---

## ESTADO ACTUAL DEL PROYECTO

```
salopezlo/Portafolio/
├── portafolio-v5.html      ← 13 páginas, ~174KB
├── portafolio-v4.html      ← backup
├── scanner.py              ← agente Python
├── opportunities.json      ← generado diariamente (auto-commit)
├── PRD-scanner-inversiones.md
├── bitacora-sesion-junio2026.md
├── ABRIR-PORTAFOLIO.bat
└── .github/workflows/scanner.yml
```

**Páginas del portafolio:**
Dashboard · Mi Portafolio · Patrimonio Total · Bitácora DCA ·
Simulador · ETFs & Acciones · Interés Compuesto · Historial & Activos ·
Vivir de inversiones · 🔭 Scanner mercado · 🔎 Analizar activo ·
Trading vs Inversión · Guía IBKR
