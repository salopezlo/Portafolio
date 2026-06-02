# PRD — Portafolio de Inversiones · Santi
**Versión:** 2.0  
**Fecha:** Junio 2026  
**Estado:** Activo — en producción

---

## 0. Estado actual (auditado Junio 2026)

**Todo en producción y funcionando:**

| Componente | Estado | URL / Path |
|---|---|---|
| Portafolio app | ✅ Live | salopezlo.github.io/Portafolio/portafolio-v5.html |
| GitHub repo | ✅ Público | github.com/salopezlo/Portafolio |
| Scanner diario | ✅ Activo | GitHub Actions · 4:30pm ET lunes-viernes |
| Gemini API | ✅ Configurado | Narrativas en español · free tier |
| FMP API | ✅ Configurado | Fundamentales · 250 calls/día gratis |
| opportunities.json | ✅ Auto-commit | Se actualiza diariamente |

---

## 1. Arquitectura en producción

```
GitHub Actions (4:30pm ET, L-V)
    → scanner.py
        → Yahoo Finance: precios, dip, rango 52s, momentum (49 tickers)
        → FMP API: P/E, FCF, revenue growth, deuda, márgenes
        → Scoring: técnico 35% + fundamental 45% + analistas 20%
        → Gemini 1.5 Flash: narrativa en español top 10 (gratis)
        → Auto-commit opportunities.json al repo
    → GitHub Pages sirve portafolio-v5.html
        → Lee opportunities.json sin CORS (mismo dominio)
        → Scanner mercado con ranking + análisis detallado on-click
```

---

## 2. Páginas del portafolio (13 en total)

**Principal:** Dashboard · Mi Portafolio · Patrimonio Total

**Herramientas:** Bitácora DCA · Simulador · ETFs & Acciones

**Calculadoras:** Interés Compuesto · Historial & Activos (redimensionable) · Vivir de inversiones (FIRE)

**Agente:** 🔭 Scanner mercado · 🔎 Analizar activo

**Aprender:** Trading vs Inversión · Guía IBKR

---

## 3. Stack técnico

| Componente | Tecnología | Costo |
|---|---|---|
| Hosting | GitHub Pages | Gratis |
| Agente diario | GitHub Actions | Gratis |
| Datos precio/técnicos | Yahoo Finance API | Gratis |
| Datos fundamentales | Financial Modeling Prep | Gratis (250/día) |
| Análisis narrativo | Google Gemini 1.5 Flash | Gratis (free tier) |
| Frontend | HTML/JS/Chart.js | — |
| Backend script | Python 3.11 | — |

**Costo mensual total: $0**

---

## 4. Secrets configurados en GitHub

- `FMP_KEY` ✅
- `GEMINI_KEY` ✅
- `ANTHROPIC_KEY` ✅ (guardado como backup, no activo)

---

## 5. Diseño visual

- **Colores:** esmeralda `#00c896` como acento principal
- **Tipografía:** Figtree (display) + DM Mono (números/mono)
- **Fondo:** `#0a0c0b` oscuro con tono verde
- **Historial & Activos:** gráfica redimensionable arrastrando borde derecho

---

## 6. Flujo de trabajo local → GitHub

```cmd
cd "C:\Users\SANTI Y LUI\Cowork\Portafolio"
git add .
git commit -m "descripción"
git pull --rebase   ← necesario porque el scanner commitea el JSON diariamente
git push
```

---

## 7. Pendiente / próximas mejoras

- [ ] **Reglas del portafolio:** expandir con más detalle y explicación
- [ ] **Gráfico satélites:** chart de distribución acciones principales (VOO, QQQ, NVDA, MSFT, AMZN, META, VIG)
- [ ] Node.js 20 → 24 en el workflow (deprecación sept 2026, no urgente)
- [ ] Analizar activo: mejorar cuando CORS bloquea (ya funciona desde GitHub Pages)
- [ ] Escáner: ampliar universo más allá de 49 tickers predefinidos

---

## 8. Perfil de inversión de Santi

**Broker inversión:** Interactive Brokers (IBKR)  
**Broker trading:** Pepperstone — MT5, metodología SMC/ICT  
**Perfil:** Agresivo · horizonte 20+ años  
**Aporte:** mínimo 20% de profits del trading → VOO  

**Portafolio objetivo:**
- VOO 30% · QQQ 20% (Core)
- NVDA 12% · MSFT 10% · AMZN 10% · META 8% (Satélites)
- VIG 10% (Dividendos)

**Reglas:** Core intocable · Satélites revisión 6 meses · Mercado -20% = comprar más

---

*Actualizado: 2 de junio de 2026*
