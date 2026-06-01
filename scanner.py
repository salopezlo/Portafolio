"""
scanner.py — Agente de oportunidades de inversión
Corre diariamente via GitHub Actions a las 4:30pm ET (cierre NYSE)
Genera opportunities.json con top oportunidades del mercado

Requiere variables de entorno (GitHub Secrets):
  FMP_KEY     — Financial Modeling Prep API key (gratis en fmp.com)
  ANTHROPIC_KEY — Claude API key (console.anthropic.com)
"""

import os, json, time, datetime
import urllib.request, urllib.parse

# ══════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════
FMP_KEY       = os.environ.get("FMP_KEY", "")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_KEY", "")

# Universo completo a escanear
ETF_UNIVERSE = [
    "VOO","QQQ","VTI","SPY","IVV","SCHD","VIG","GLD","SLV",
    "SOXX","XLK","XLF","XLE","ARKK","IBIT","BND","AGG","VNQ","VWO"
]

STOCK_UNIVERSE = [
    # Mega cap
    "AAPL","MSFT","NVDA","AMZN","GOOGL","META","TSLA","BRK-B","AVGO","LLY",
    # Large cap tech
    "AMD","NFLX","CRM","ORCL","ADBE","NOW","SNOW","PLTR","ARM","TSM",
    # Large cap otros sectores
    "JPM","V","MA","UNH","HD","COST","WMT","PG","JNJ","KO",
    # Santi's portfolio
    "MSFT","NVDA","AMZN","META","VIG"
]

ALL_TICKERS = list(dict.fromkeys(ETF_UNIVERSE + STOCK_UNIVERSE))  # sin duplicados

# ══════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════
def fetch_json(url, headers=None, retries=3):
    """Fetch URL con reintentos."""
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers or {
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/json"
            })
            with urllib.request.urlopen(req, timeout=10) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            if i == retries - 1:
                print(f"  ⚠️  Error {url[:60]}: {e}")
                return None
            time.sleep(2 ** i)
    return None


def fmp_get(endpoint):
    """Llama a Financial Modeling Prep API."""
    if not FMP_KEY:
        return None
    url = f"https://financialmodelingprep.com/api/v3/{endpoint}&apikey={FMP_KEY}"
    return fetch_json(url)


# ══════════════════════════════════════════════
# 1. PRECIOS — Yahoo Finance
# ══════════════════════════════════════════════
def get_price_data(ticker):
    """Obtiene precio actual, cambio, rango 52s, volumen, market cap."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=30d"
    d = fetch_json(url)
    if not d:
        return None
    try:
        meta  = d["chart"]["result"][0]["meta"]
        closes= d["chart"]["result"][0].get("indicators",{}).get("quote",[{}])[0].get("close",[])
        closes= [c for c in closes if c is not None]
        price = meta.get("regularMarketPrice")
        prev  = meta.get("chartPreviousClose") or meta.get("previousClose") or price
        h52   = meta.get("fiftyTwoWeekHigh")
        l52   = meta.get("fiftyTwoWeekLow")
        vol   = meta.get("regularMarketVolume", 0)
        cap   = meta.get("marketCap", 0)
        name  = meta.get("longName") or meta.get("shortName") or ticker
        exchg = meta.get("exchangeName","")
        if not price:
            return None

        # Dip desde máximo 30 días
        max30 = max(closes) if closes else price
        dip30 = (max30 - price) / max30 * 100 if max30 > 0 else 0

        # Posición en rango 52 semanas
        range52 = (price - l52) / (h52 - l52) * 100 if h52 and l52 and h52 > l52 else 50

        # Momentum 5 días
        mom5 = (price / closes[-6] - 1) * 100 if len(closes) >= 6 else 0

        # Cambio hoy
        change_pct = (price - prev) / prev * 100 if prev else 0

        return {
            "ticker":     ticker,
            "name":       name,
            "exchange":   exchg,
            "price":      round(price, 2),
            "change_pct": round(change_pct, 2),
            "dip30":      round(dip30, 2),
            "range52pct": round(range52, 1),
            "h52":        round(h52, 2) if h52 else None,
            "l52":        round(l52, 2) if l52 else None,
            "mom5":       round(mom5, 2),
            "volume":     vol,
            "market_cap": cap,
        }
    except Exception as e:
        print(f"  ⚠️  parse error {ticker}: {e}")
        return None


# ══════════════════════════════════════════════
# 2. FUNDAMENTALES — FMP API
# ══════════════════════════════════════════════
def get_fundamentals(ticker):
    """Obtiene P/E, FCF, revenue growth, deuda, márgenes."""
    if not FMP_KEY:
        return {}

    # Quote (P/E, forward P/E, analyst target)
    q = fmp_get(f"quote/{ticker}?")
    if not q or not isinstance(q, list) or not q:
        return {}
    q = q[0]

    # Ratios (FCF yield, EV/EBITDA, P/S, PEG)
    r = fmp_get(f"ratios-ttm/{ticker}?")
    r = r[0] if r and isinstance(r, list) and r else {}

    # Income statement (revenue growth)
    inc = fmp_get(f"income-statement/{ticker}?limit=2&period=annual")
    rev_growth = None
    if inc and isinstance(inc, list) and len(inc) >= 2:
        rev_curr = inc[0].get("revenue", 0)
        rev_prev = inc[1].get("revenue", 1)
        if rev_prev > 0:
            rev_growth = round((rev_curr / rev_prev - 1) * 100, 1)

    # Cash flow (FCF)
    cf = fmp_get(f"cash-flow-statement/{ticker}?limit=1&period=annual")
    fcf = None
    if cf and isinstance(cf, list) and cf:
        fcf = cf[0].get("freeCashFlow")

    pe       = q.get("pe")
    fpe      = q.get("priceEarningsRatio") or r.get("priceEarningsRatioTTM")
    target   = q.get("priceAvg200") or q.get("analystTargetPrice")
    rec      = q.get("revenueGrowth")
    de       = r.get("debtEquityRatioTTM")
    op_margin= r.get("operatingProfitMarginTTM")
    ev_ebitda= r.get("enterpriseValueMultipleTTM")
    fcf_yield= r.get("freeCashFlowYieldTTM")
    eps      = q.get("eps")
    beta     = q.get("beta")
    div_yield= q.get("lastDividendYield") or r.get("dividendYieldTTM")
    n_analysts = q.get("numberOfAnalysts") or 0
    analyst_target = q.get("targetMeanPrice") or q.get("priceAvgTarget")

    upside = None
    if analyst_target and q.get("price"):
        upside = round((analyst_target - q["price"]) / q["price"] * 100, 1)

    return {
        "pe":           round(pe, 1) if pe else None,
        "forward_pe":   round(fpe, 1) if fpe else None,
        "eps":          round(eps, 2) if eps else None,
        "beta":         round(beta, 2) if beta else None,
        "div_yield":    round(div_yield * 100, 2) if div_yield else None,
        "rev_growth":   rev_growth,
        "op_margin":    round(op_margin * 100, 1) if op_margin else None,
        "fcf":          fcf,
        "fcf_yield":    round(fcf_yield * 100, 2) if fcf_yield else None,
        "ev_ebitda":    round(ev_ebitda, 1) if ev_ebitda else None,
        "debt_equity":  round(de, 2) if de else None,
        "analyst_target": round(analyst_target, 2) if analyst_target else None,
        "analyst_upside": upside,
        "n_analysts":   n_analysts,
    }


# ══════════════════════════════════════════════
# 3. SCORING
# ══════════════════════════════════════════════
def score_ticker(price_data, fund_data):
    """Calcula score de oportunidad 0–10."""
    scores = {}

    # ── Técnico (35%)
    # Dip 30 días: 0% dip = 0 pts, 20%+ dip = 10 pts
    dip  = price_data.get("dip30", 0)
    scores["dip"] = min(10, dip / 2)  # 20% dip = 10 pts

    # Posición 52s: bottom 0% = 10 pts, top 100% = 0 pts
    r52  = price_data.get("range52pct", 50)
    scores["range52"] = max(0, (100 - r52) / 10)

    # Momentum 5d: caída reciente = señal contrarian
    mom  = price_data.get("mom5", 0)
    scores["momentum"] = min(10, max(0, -mom / 2 + 5))  # -10% mom = 10 pts, +10% = 0 pts

    tech_score = scores["dip"] * 0.15 + scores["range52"] * 0.12 + scores["momentum"] * 0.08

    # ── Fundamentales (45%)
    fund_score = 5.0  # default neutral si no hay datos

    if fund_data:
        f_parts = []

        # Forward P/E < 20 = bueno, > 40 = malo
        fpe = fund_data.get("forward_pe")
        if fpe and fpe > 0:
            f_parts.append(max(0, min(10, (40 - fpe) / 3)))

        # FCF yield > 4% = muy bueno
        fcf_y = fund_data.get("fcf_yield")
        if fcf_y is not None:
            f_parts.append(min(10, fcf_y * 1.5))

        # Revenue growth > 15% = bueno
        rev_g = fund_data.get("rev_growth")
        if rev_g is not None:
            f_parts.append(min(10, max(0, rev_g / 3)))

        # Deuda: D/E < 1 = 8 pts, > 3 = 2 pts
        de = fund_data.get("debt_equity")
        if de is not None and de >= 0:
            f_parts.append(max(0, min(10, 10 - de * 2.5)))

        fund_score = sum(f_parts) / len(f_parts) if f_parts else 5.0

    # ── Analistas (20%)
    analyst_score = 5.0  # neutral default
    upside = fund_data.get("analyst_upside") if fund_data else None
    if upside is not None:
        analyst_score = min(10, max(0, upside / 3))

    # ── Total
    total = tech_score * 0.35 + fund_score * 0.45 + analyst_score * 0.20
    total = round(min(10, max(0, total)), 1)

    return {
        "total":    total,
        "tech":     round(tech_score, 1),
        "fund":     round(fund_score, 1),
        "analyst":  round(analyst_score, 1),
        "detail":   scores,
    }


# ══════════════════════════════════════════════
# 4. CLASIFICACIÓN DE RIESGO
# ══════════════════════════════════════════════
def classify_risk(ticker, market_cap, is_etf):
    if is_etf:
        return "etf"
    if market_cap and market_cap >= 500e9:
        return "mega"
    if market_cap and market_cap >= 10e9:
        return "large"
    return "speculative"


ETF_TICKERS = set(ETF_UNIVERSE)

def is_etf(ticker):
    return ticker in ETF_TICKERS


# ══════════════════════════════════════════════
# 5. ANÁLISIS NARRATIVO — Claude API
# ══════════════════════════════════════════════
def generate_narrative(ticker, name, price_data, fund_data, score_data):
    """Genera análisis narrativo en español usando Claude API."""
    if not ANTHROPIC_KEY:
        return None

    # Construir contexto financiero
    ctx_parts = [f"Ticker: {ticker} — {name}"]
    ctx_parts.append(f"Precio: ${price_data['price']} ({'+' if price_data['change_pct']>=0 else ''}{price_data['change_pct']}% hoy)")
    ctx_parts.append(f"Caída desde máximo 30 días: {price_data['dip30']}%")
    ctx_parts.append(f"Posición en rango 52 semanas: {price_data['range52pct']}% (0%=mínimo, 100%=máximo)")
    ctx_parts.append(f"Score de oportunidad: {score_data['total']}/10")

    if fund_data:
        if fund_data.get("pe"):          ctx_parts.append(f"P/E actual: {fund_data['pe']}x")
        if fund_data.get("forward_pe"):  ctx_parts.append(f"P/E forward: {fund_data['forward_pe']}x")
        if fund_data.get("rev_growth"):  ctx_parts.append(f"Crecimiento revenue YoY: {fund_data['rev_growth']}%")
        if fund_data.get("op_margin"):   ctx_parts.append(f"Margen operativo: {fund_data['op_margin']}%")
        if fund_data.get("fcf_yield"):   ctx_parts.append(f"FCF yield: {fund_data['fcf_yield']}%")
        if fund_data.get("debt_equity"): ctx_parts.append(f"Deuda/Equity: {fund_data['debt_equity']}x")
        if fund_data.get("analyst_upside") is not None:
            ctx_parts.append(f"Upside vs objetivo analistas: {'+' if fund_data['analyst_upside']>=0 else ''}{fund_data['analyst_upside']}%")
        if fund_data.get("ev_ebitda"):   ctx_parts.append(f"EV/EBITDA: {fund_data['ev_ebitda']}x")

    context = "\n".join(ctx_parts)

    prompt = f"""Eres un analista de inversiones senior. Analiza este activo para un inversor colombiano con perfil AGRESIVO y horizonte de largo plazo (20+ años) que usa estrategia DCA (Dollar Cost Averaging).

DATOS DEL ACTIVO:
{context}

Genera un análisis financiero conciso en español (máximo 250 palabras) con esta estructura exacta:

📊 SITUACIÓN ACTUAL
[1-2 líneas: precio, tendencia reciente, dónde está en el rango anual]

💼 NEGOCIO Y VENTAJA
[2-3 líneas: qué hace la empresa/ETF, por qué es relevante, ventaja competitiva]

📈 SEÑALES FINANCIERAS
[3-4 métricas clave con interpretación breve en lenguaje simple, no solo números]

⚠️ RIESGOS PRINCIPALES
[2-3 riesgos concretos, no genéricos]

⚡ SEÑAL DCA
[1-2 líneas directas: ¿es momento de comprar ahora, esperar corrección mayor, o evitar? Sé directo.]

Usa lenguaje claro y directo. Evita clichés financieros. Los términos técnicos en español."""

    # Llamar Claude API
    payload = json.dumps({
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 600,
        "messages": [{"role": "user", "content": prompt}]
    }).encode()

    try:
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={
                "x-api-key": ANTHROPIC_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            resp = json.loads(r.read().decode())
            return resp["content"][0]["text"]
    except Exception as e:
        print(f"  ⚠️  Claude API error para {ticker}: {e}")
        return None


# ══════════════════════════════════════════════
# 6. MAIN
# ══════════════════════════════════════════════
def main():
    print(f"\n🚀 Scanner iniciado — {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} UTC")
    print(f"   FMP API: {'✅' if FMP_KEY else '❌ no configurada'}")
    print(f"   Claude API: {'✅' if ANTHROPIC_KEY else '❌ no configurada'}")
    print(f"   Tickers a analizar: {len(ALL_TICKERS)}\n")

    results = []

    for i, ticker in enumerate(ALL_TICKERS):
        print(f"[{i+1}/{len(ALL_TICKERS)}] {ticker}...", end=" ")

        # Precio
        pd = get_price_data(ticker)
        if not pd:
            print("sin datos")
            continue

        # Fundamentales (solo para stocks, no ETFs — ahorra calls API)
        fd = {}
        if not is_etf(ticker) and FMP_KEY:
            fd = get_fundamentals(ticker)
            time.sleep(0.3)  # rate limit FMP

        # Score
        sd = score_ticker(pd, fd)
        print(f"score={sd['total']}")

        # Riesgo
        risk = classify_risk(ticker, pd.get("market_cap"), is_etf(ticker))

        results.append({
            "ticker":      ticker,
            "name":        pd["name"],
            "risk":        risk,
            "score":       sd,
            "price":       pd,
            "fundamentals": fd,
            "narrative":   None,  # se genera on-demand en el browser
            "updated_at":  datetime.datetime.utcnow().isoformat()
        })

        time.sleep(0.5)  # rate limit Yahoo Finance

    # Ordenar por score descendente
    results.sort(key=lambda x: x["score"]["total"], reverse=True)

    # Generar narrativas solo para top 10 (ahorra costo Claude API)
    if ANTHROPIC_KEY:
        print("\n📝 Generando análisis narrativos (top 10)...")
        for item in results[:10]:
            print(f"  Claude → {item['ticker']}...", end=" ")
            narrative = generate_narrative(
                item["ticker"], item["name"],
                item["price"], item["fundamentals"], item["score"]
            )
            item["narrative"] = narrative
            print("✅" if narrative else "❌")
            time.sleep(1)  # rate limit Claude

    # Estadísticas
    top5    = results[:5]
    by_risk = {
        "etf":         [r for r in results if r["risk"] == "etf"][:5],
        "mega":        [r for r in results if r["risk"] == "mega"][:5],
        "large":       [r for r in results if r["risk"] == "large"][:5],
        "speculative": [r for r in results if r["risk"] == "speculative"][:3],
    }

    output = {
        "generated_at":  datetime.datetime.utcnow().isoformat(),
        "market_date":   datetime.date.today().isoformat(),
        "total_scanned": len(results),
        "top5":          top5,
        "by_risk":       by_risk,
        "all_results":   results
    }

    # Guardar
    with open("opportunities.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n✅ opportunities.json generado")
    print(f"   {len(results)} activos analizados")
    print(f"   Top 3: {', '.join(r['ticker']+'('+str(r['score']['total'])+')' for r in results[:3])}")
    print(f"   Narrativas generadas: {sum(1 for r in results if r.get('narrative'))}")


if __name__ == "__main__":
    main()
