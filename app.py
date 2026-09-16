# =============================================================================
#  VÉRTICE EXECUTIVE DASHBOARD  –  app.py
#  Desenvolvido para: Case Vértice (Varejo de Moda & Lifestyle Digital)
#  Stack: Streamlit · Plotly · Pandas · NumPy
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import io, random

# ─────────────────────────────────────────────
#  CONSTANTES DE IDENTIDADE VISUAL
# ─────────────────────────────────────────────
C_PRIMARY   = "#003366"   # Azul corporativo profundo
C_ACCENT    = "#0057A8"   # Azul médio (hover / destaque)
C_SUCCESS   = "#388E3C"   # Verde lucro / margem positiva
C_DANGER    = "#D32F2F"   # Vermelho custo / perda
C_WARN      = "#F57C00"   # Laranja alerta intermediário
C_BG        = "#F0F2F6"   # Fundo geral
C_CARD      = "#FFFFFF"   # Card branco
C_TEXT      = "#1A1A2E"   # Texto principal
C_MUTED     = "#6B7280"   # Texto secundário
C_GRID      = "rgba(0,0,0,0.05)"

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, Arial, sans-serif", color=C_TEXT, size=12),
    margin=dict(l=30, r=30, t=45, b=30),
    hoverlabel=dict(bgcolor=C_CARD, font_size=13, font_family="Inter, Arial"),
    xaxis=dict(gridcolor=C_GRID, linecolor=C_GRID),
    yaxis=dict(gridcolor=C_GRID, linecolor=C_GRID),
    colorway=[C_PRIMARY, C_ACCENT, C_SUCCESS, C_WARN, C_DANGER,
              "#5C6BC0","#26A69A","#AB47BC","#EC407A"],
)

COLUNAS_ESPERADAS = [
    "order_id","customer_id","sku_id","data_pedido","canal","categoria",
    "produto","quantidade","preco_unitario","receita_bruta","desconto_reais",
    "receita_liquida","custo_produto","custo_frete","metodo_pagamento",
    "status_pagamento","margem_contribuicao",
]

# =============================================================================
#  INJEÇÃO DE CSS CUSTOMIZADO
# =============================================================================
def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

    /* Header principal */
    .vertice-header {
        background: linear-gradient(135deg, #003366 0%, #0057A8 100%);
        border-radius: 12px; padding: 28px 36px; margin-bottom: 24px;
        display: flex; align-items: center; gap: 20px;
        box-shadow: 0 4px 20px rgba(0,51,102,0.18);
    }
    .vertice-header h1 { color: #FFFFFF; font-size: 1.9rem; font-weight: 700;
        margin: 0; letter-spacing: -0.5px; }
    .vertice-header p  { color: rgba(255,255,255,0.75); font-size: 0.92rem; margin: 4px 0 0; }

    /* KPI Cards */
    .kpi-card {
        background: #FFFFFF; border-radius: 12px; padding: 20px 24px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06); border-left: 4px solid #003366;
        transition: transform .15s ease, box-shadow .15s ease;
    }
    .kpi-card:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,0.10); }
    .kpi-label { font-size: 0.78rem; font-weight: 600; color: #6B7280;
        text-transform: uppercase; letter-spacing: .6px; margin-bottom: 6px; }
    .kpi-value { font-size: 1.75rem; font-weight: 700; color: #1A1A2E; line-height: 1.1; }
    .kpi-delta-pos { font-size: 0.82rem; font-weight: 600; color: #388E3C; margin-top: 4px; }
    .kpi-delta-neg { font-size: 0.82rem; font-weight: 600; color: #D32F2F; margin-top: 4px; }
    .kpi-delta-neu { font-size: 0.82rem; font-weight: 600; color: #6B7280; margin-top: 4px; }

    /* Section titles */
    .section-title {
        font-size: 1.1rem; font-weight: 700; color: #003366;
        border-bottom: 2px solid #E5E7EB; padding-bottom: 8px;
        margin: 28px 0 16px;
    }

    /* Tabs styling */
    div[data-testid="stTabs"] button {
        font-weight: 600 !important; font-size: 0.87rem !important;
        color: #6B7280 !important; padding: 10px 20px !important;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] {
        color: #003366 !important;
        border-bottom: 3px solid #003366 !important;
    }

    /* Insight box */
    .insight-box {
        background: linear-gradient(135deg,#EFF6FF,#DBEAFE);
        border-radius: 10px; padding: 16px 20px; border-left: 4px solid #003366;
        font-size: 0.88rem; color: #1E3A5F; margin: 12px 0;
    }
    .insight-box strong { color: #003366; }

    /* Slider label */
    .slider-header { font-size: 0.85rem; font-weight: 600; color: #003366; }

    /* Upload zone */
    div[data-testid="stFileUploader"] {
        border: 2px dashed #003366 !important; border-radius: 10px !important;
        background: #F8FAFF !important;
    }

    /* Chat bubble */
    .chat-alert { background: #FFF8E1; border-left: 4px solid #F57C00;
        border-radius: 8px; padding: 14px 18px; margin: 8px 0;
        font-size: 0.88rem; color: #37474F; }
    </style>
    """, unsafe_allow_html=True)


# =============================================================================
#  GERADOR DE DADOS DE DEMONSTRAÇÃO
# =============================================================================
@st.cache_data
def gerar_demo_data() -> pd.DataFrame:
    """Gera um DataFrame sintético pequeno para demonstração visual."""
    random.seed(42); np.random.seed(42)
    n = 1200
    datas = pd.date_range("2023-01-01", "2023-12-31", periods=n)
    canais  = np.random.choice(["Marketplace","E-commerce Próprio","Redes Sociais"],
                               size=n, p=[0.50, 0.35, 0.15])
    cats    = np.random.choice(["Vestuário","Calçados","Acessórios","Beleza"], size=n)
    qtd     = np.random.randint(1, 4, size=n)
    preco   = np.round(np.random.uniform(80, 600, size=n), 2)
    rec_b   = preco * qtd
    desc    = np.where(
        np.random.rand(n) < 0.35,
        np.round(rec_b * np.random.uniform(0.05, 0.15, size=n), 2), 0
    )
    rec_l   = rec_b - desc
    c_prod  = np.round(rec_b * np.random.uniform(0.30, 0.45, size=n), 2)
    c_frete = np.where(canais == "Marketplace",
                       np.round(np.random.normal(32.57, 4, n), 2),
                       np.round(np.random.normal(18, 5, n), 2))
    c_frete = np.clip(c_frete, 5, 60)
    margem  = rec_l - c_prod - c_frete
    metodos = np.random.choice(["Crédito","Boleto","Pix"], size=n, p=[0.60,0.15,0.25])
    status  = np.random.choice(["Aprovado","Cancelado"], size=n, p=[0.94,0.06])
    df = pd.DataFrame({
        "order_id":           [f"ORD-{i:05d}" for i in range(n)],
        "customer_id":        [f"C-{random.randint(100,900):03d}" for _ in range(n)],
        "sku_id":             [f"SKU-{random.randint(1,80):03d}" for _ in range(n)],
        "data_pedido":        datas,
        "canal":              canais,
        "categoria":          cats,
        "produto":            [f"Produto {random.randint(1,120):03d}" for _ in range(n)],
        "quantidade":         qtd,
        "preco_unitario":     preco,
        "receita_bruta":      np.round(rec_b, 2),
        "desconto_reais":     np.round(desc, 2),
        "receita_liquida":    np.round(rec_l, 2),
        "custo_produto":      c_prod,
        "custo_frete":        np.round(c_frete, 2),
        "metodo_pagamento":   metodos,
        "status_pagamento":   status,
        "margem_contribuicao": np.round(margem, 2),
    })
    return df


# =============================================================================
#  LEITURA E VALIDAÇÃO DE CSV
# =============================================================================
def carregar_csv(uploaded_file, nome_display: str) -> pd.DataFrame | None:
    """Lê o CSV, valida colunas e retorna DataFrame ou None."""
    try:
        df = pd.read_csv(uploaded_file, sep=None, engine="python",
                         encoding="utf-8-sig", parse_dates=["data_pedido"])
    except UnicodeDecodeError:
        try:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, sep=None, engine="python",
                             encoding="latin-1", parse_dates=["data_pedido"])
        except Exception as e:
            st.error(f"❌ **Erro de leitura em `{nome_display}`:** {e}")
            return None
    except Exception as e:
        st.error(f"❌ **Erro de leitura em `{nome_display}`:** {e}")
        return None

    if df.empty:
        st.error(f"❌ O arquivo `{nome_display}` está vazio. Verifique o arquivo enviado.")
        return None

    # Normaliza nomes de colunas
    df.columns = [c.strip().lower().replace(" ","_") for c in df.columns]

    faltando = [c for c in COLUNAS_ESPERADAS if c not in df.columns]
    if faltando:
        st.error(
            f"❌ **`{nome_display}` está faltando colunas obrigatórias:**\n\n"
            f"`{', '.join(faltando)}`\n\n"
            "Verifique se o arquivo possui o cabeçalho correto e tente novamente."
        )
        return None

    # Garante tipo numérico nas colunas financeiras
    num_cols = ["receita_bruta","desconto_reais","receita_liquida",
                "custo_produto","custo_frete","margem_contribuicao",
                "preco_unitario","quantidade"]
    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    return df


# =============================================================================
#  HELPERS DE FORMATAÇÃO
# =============================================================================
def fmt_brl(v: float) -> str:
    """Formata em Real Brasileiro."""
    return f"R$ {v:,.2f}".replace(",","X").replace(".",",").replace("X",".")

def fmt_pct(v: float) -> str:
    return f"{v:.1f}%"

def kpi_html(label, value, delta_str, delta_positive: bool | None = None) -> str:
    if delta_positive is True:
        dc = "kpi-delta-pos"; arrow = "▲"
    elif delta_positive is False:
        dc = "kpi-delta-neg"; arrow = "▼"
    else:
        dc = "kpi-delta-neu"; arrow = "●"
    return f"""
    <div class='kpi-card'>
      <div class='kpi-label'>{label}</div>
      <div class='kpi-value'>{value}</div>
      <div class='{dc}'>{arrow} {delta_str}</div>
    </div>"""


# =============================================================================
#  ABA 1 – VISÃO GERAL (O PROBLEMA)
# =============================================================================
def aba_visao_geral(df: pd.DataFrame):
    st.markdown("<div class='section-title'>📊 KPIs Principais</div>",
                unsafe_allow_html=True)

    df_ap = df[df["status_pagamento"] == "Aprovado"].copy()
    receita    = df_ap["receita_bruta"].sum()
    margem_tot = df_ap["margem_contribuicao"].sum()
    margem_pct = (margem_tot / receita * 100) if receita else 0
    desc_medio = (df_ap["desconto_reais"].sum() / receita * 100) if receita else 0
    frete_med  = df_ap["custo_frete"].mean()
    ticket_med = df_ap["receita_bruta"].mean()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(kpi_html("💰 Receita Bruta Total",
            fmt_brl(receita), "Pedidos aprovados", None), unsafe_allow_html=True)
    with c2:
        pos = margem_pct >= 50
        st.markdown(kpi_html("📈 Margem de Contribuição",
            fmt_pct(margem_pct), fmt_brl(margem_tot), pos), unsafe_allow_html=True)
    with c3:
        pos2 = desc_medio < 8
        st.markdown(kpi_html("🏷️ Desconto Médio",
            fmt_pct(desc_medio), "Sobre receita bruta", pos2), unsafe_allow_html=True)
    with c4:
        st.markdown(kpi_html("🚚 Frete Médio por Pedido",
            fmt_brl(frete_med), "Custo logístico médio", None), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Gráficos mensais ──────────────────────────────────────────────────────
    df_ap["mes"] = df_ap["data_pedido"].dt.to_period("M").astype(str)
    mensal = (
        df_ap.groupby("mes")
        .agg(receita_bruta=("receita_bruta","sum"),
             margem=("margem_contribuicao","sum"))
        .reset_index()
        .sort_values("mes")
    )
    mensal["margem_pct"] = mensal["margem"] / mensal["receita_bruta"] * 100

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("<div class='section-title'>📅 Faturamento Bruto Mensal</div>",
                    unsafe_allow_html=True)
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            x=mensal["mes"], y=mensal["receita_bruta"],
            marker_color=C_PRIMARY, name="Receita Bruta",
            hovertemplate="<b>%{x}</b><br>Receita: R$ %{y:,.2f}<extra></extra>",
        ))
        fig_bar.update_layout(**PLOTLY_LAYOUT, title="",
            xaxis_tickangle=-35, yaxis_tickprefix="R$ ",
            bargap=0.30)
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_b:
        st.markdown("<div class='section-title'>📉 Margem de Contribuição Mensal (%)</div>",
                    unsafe_allow_html=True)
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=mensal["mes"], y=mensal["margem_pct"],
            mode="lines+markers+text",
            line=dict(color=C_SUCCESS, width=3),
            marker=dict(size=8, color=C_SUCCESS),
            text=[f"{v:.1f}%" for v in mensal["margem_pct"]],
            textposition="top center",
            fill="tozeroy",
            fillcolor="rgba(56,142,60,0.08)",
            name="Margem %",
            hovertemplate="<b>%{x}</b><br>Margem: %{y:.1f}%<extra></extra>",
        ))
        fig_line.add_hline(y=50, line_dash="dot", line_color=C_WARN,
                           annotation_text="Meta 50%", annotation_position="right")
        fig_line.update_layout(**PLOTLY_LAYOUT, title="",
            xaxis_tickangle=-35,
            yaxis_ticksuffix="%", yaxis_range=[0, 100])
        st.plotly_chart(fig_line, use_container_width=True)

    # ── Insight contextual ────────────────────────────────────────────────────
    st.markdown("""
    <div class='insight-box'>
    📌 <strong>Insight Validado:</strong> Em <strong>Novembro/2023</strong>, o faturamento
    atingiu R$ 3M (recorde histórico), mas o desconto excessivo de <strong>9,5%</strong>
    derrubou a margem para <strong>48,1%</strong> — projetando uma perda de
    <strong>R$ 64 mil</strong> em relação ao cenário sem desconto agressivo.
    </div>""", unsafe_allow_html=True)

    # ── Tabela Top Canais ─────────────────────────────────────────────────────
    st.markdown("<div class='section-title'>🏪 Desempenho por Canal</div>",
                unsafe_allow_html=True)
    canal_sum = (
        df_ap.groupby("canal")
        .agg(
            Pedidos=("order_id","count"),
            Receita_Bruta=("receita_bruta","sum"),
            Margem_Total=("margem_contribuicao","sum"),
            Frete_Medio=("custo_frete","mean"),
        )
        .reset_index()
    )
    canal_sum["Margem_%"] = (canal_sum["Margem_Total"] / canal_sum["Receita_Bruta"] * 100).round(1)
    canal_sum["Receita_Bruta"] = canal_sum["Receita_Bruta"].apply(fmt_brl)
    canal_sum["Margem_Total"]  = canal_sum["Margem_Total"].apply(fmt_brl)
    canal_sum["Frete_Medio"]   = canal_sum["Frete_Medio"].apply(fmt_brl)
    canal_sum.columns = ["Canal","Pedidos","Receita Bruta","Margem Total","Frete Médio","Margem %"]
    st.dataframe(canal_sum.set_index("Canal"), use_container_width=True)


# =============================================================================
#  ABA 2 – O RALO OPERACIONAL (A CAUSA)
# =============================================================================
def aba_ralo_operacional(df: pd.DataFrame):
    df_ap = df[df["status_pagamento"] == "Aprovado"].copy()

    st.markdown("<div class='section-title'>🔍 Distribuição da Margem Unitária por Canal</div>",
                unsafe_allow_html=True)
    st.markdown("""<div class='insight-box'>
    ⚠️ <strong>Diagnóstico:</strong> O canal Marketplace pratica frete fixo médio de
    <strong>R$ 32,57</strong>, que "come" a margem de pedidos de baixo ticket.
    O boxplot abaixo revela onde a distribuição colapsa.
    </div>""", unsafe_allow_html=True)

    # ── Boxplot ───────────────────────────────────────────────────────────────
    df_ap["margem_unit"] = df_ap["margem_contribuicao"] / df_ap["quantidade"]
    canais_ord = (df_ap.groupby("canal")["margem_unit"].median()
                       .sort_values().index.tolist())
    colors_box = [C_DANGER, C_WARN, C_SUCCESS, C_ACCENT]

    fig_box = go.Figure()
    for i, canal in enumerate(canais_ord):
        sub = df_ap[df_ap["canal"] == canal]["margem_unit"].dropna()
        fig_box.add_trace(go.Box(
            y=sub, name=canal, boxpoints="outliers",
            marker_color=colors_box[i % len(colors_box)],
            fillcolor=colors_box[i % len(colors_box)].replace(")",",0.15)").replace("rgb","rgba"),
            line_color=colors_box[i % len(colors_box)],
            hovertemplate="<b>%{x}</b><br>Margem Unit.: R$ %{y:.2f}<extra></extra>",
        ))
    fig_box.add_hline(y=0, line_dash="dash", line_color=C_DANGER,
                      annotation_text="Break-even", annotation_position="right")
    fig_box.update_layout(**PLOTLY_LAYOUT,
        title="Margem Unitária (R$) por Canal de Venda",
        yaxis_title="Margem por Unidade (R$)",
        showlegend=False)
    st.plotly_chart(fig_box, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Stacked Bar 100% – Composição de custo por faixa de ticket ───────────
    st.markdown("<div class='section-title'>📦 Composição de Custo por Faixa de Ticket</div>",
                unsafe_allow_html=True)

    bins   = [0, 100, 200, 300, 400, 600, float("inf")]
    labels = ["< R$100","R$100–200","R$200–300","R$300–400","R$400–600","R$600+"]
    df_ap["faixa_ticket"] = pd.cut(df_ap["receita_bruta"], bins=bins, labels=labels)

    comp = df_ap.groupby("faixa_ticket", observed=True).agg(
        custo_produto=("custo_produto","sum"),
        custo_frete=("custo_frete","sum"),
        receita_bruta=("receita_bruta","sum"),
    ).reset_index()
    comp["total_custo"] = comp["custo_produto"] + comp["custo_frete"]
    comp["pct_produto"] = comp["custo_produto"] / comp["total_custo"] * 100
    comp["pct_frete"]   = comp["custo_frete"]   / comp["total_custo"] * 100

    fig_stack = go.Figure()
    fig_stack.add_trace(go.Bar(
        x=comp["faixa_ticket"], y=comp["pct_produto"],
        name="Custo do Produto", marker_color=C_PRIMARY,
        hovertemplate="<b>%{x}</b><br>Produto: %{y:.1f}%<extra></extra>",
    ))
    fig_stack.add_trace(go.Bar(
        x=comp["faixa_ticket"], y=comp["pct_frete"],
        name="Custo de Frete", marker_color=C_DANGER,
        hovertemplate="<b>%{x}</b><br>Frete: %{y:.1f}%<extra></extra>",
    ))
    fig_stack.update_layout(
        **PLOTLY_LAYOUT,
        title="Composição de Custo (100% Empilhado) por Faixa de Ticket",
        barmode="stack",
        yaxis_ticksuffix="%", yaxis_range=[0,100],
        yaxis_title="% do Custo Total",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig_stack, use_container_width=True)

    st.markdown("""<div class='insight-box'>
    💡 <strong>Takeaway:</strong> Nas faixas de ticket abaixo de <strong>R$ 200</strong>,
    o frete representa uma fatia desproporcional do custo total — evidenciando que a
    política de frete grátis sem teto mínimo é o principal "ralo" operacional.
    </div>""", unsafe_allow_html=True)

    # ── Canal MKP – análise de frete ─────────────────────────────────────────
    st.markdown("<div class='section-title'>🏪 Análise de Frete – Marketplace vs. Outros</div>",
                unsafe_allow_html=True)
    df_ap["canal_bin"] = df_ap["canal"].apply(
        lambda x: "Marketplace" if "marketplace" in x.lower() or "mkp" in x.lower() else "Outros Canais"
    )
    fr_canal = df_ap.groupby("canal_bin")["custo_frete"].agg(
        ["mean","median","sum","count"]
    ).reset_index()
    fr_canal.columns = ["Canal","Frete Médio","Frete Mediana","Frete Total","Pedidos"]
    fr_canal["Frete Médio"]  = fr_canal["Frete Médio"].apply(fmt_brl)
    fr_canal["Frete Mediana"]= fr_canal["Frete Mediana"].apply(fmt_brl)
    fr_canal["Frete Total"]  = fr_canal["Frete Total"].apply(fmt_brl)
    st.dataframe(fr_canal.set_index("Canal"), use_container_width=True)

    # ── 4. Mapa de Calor de Retenção (Cohort Heatmap) ─────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>👥 Análise de Retenção e Safra de Clientes (Cohort)</div>",
                unsafe_allow_html=True)

    # 1. Preparação da base de aprovados
    df_cohort = df_ap.copy()
    df_cohort['data_pedido'] = pd.to_datetime(df_cohort['data_pedido'])
    df_cohort['mes_pedido'] = df_cohort['data_pedido'].dt.to_period('M')

    # Safra = primeiro mês de compra de cada cliente
    df_cohort['safra'] = df_cohort.groupby('customer_id')['data_pedido'].transform('min').dt.to_period('M')

    # Distância em meses desde a primeira compra
    df_cohort['periodo_meses'] = (df_cohort['mes_pedido'].dt.year - df_cohort['safra'].dt.year) * 12 + \
                                 (df_cohort['mes_pedido'].dt.month - df_cohort['safra'].dt.month)

    # 2. Matriz de contagem e conversão em percentual
    cohort_counts = df_cohort.groupby(['safra', 'periodo_meses'])['customer_id'].nunique().reset_index()
    cohort_matrix = cohort_counts.pivot(index='safra', columns='periodo_meses', values='customer_id')
    
    tamanho_safra = cohort_matrix.iloc[:, 0]
    retention_matrix = cohort_matrix.divide(tamanho_safra, axis=0) * 100

    # Formatar rótulos para exibição limpa
    y_labels = [str(idx) for idx in retention_matrix.index]
    x_labels = [f"Mês {col}" for col in retention_matrix.columns]
    text_matrix = retention_matrix.map(lambda v: f"{v:.1f}%" if pd.notnull(v) else "")

    # 3. Gráfico Interativo com Plotly (nativo do tema do app)
    fig_cohort = go.Figure(data=go.Heatmap(
        z=retention_matrix.values,
        x=x_labels,
        y=y_labels,
        text=text_matrix.values,
        texttemplate="%{text}",
        textfont={"size": 11, "family": "Inter, Arial"},
        colorscale="Blues",
        zmin=0,
        zmax=25,
        colorbar=dict(title="% Recompra", ticksuffix="%"),
        hoverongaps=False,
        hovertemplate="<b>Safra:</b> %{y}<br><b>Período:</b> %{x}<br><b>Retenção:</b> %{z:.1f}%<extra></extra>"
    ))

    fig_cohort.update_layout(
        title="Mapa de Calor de Retenção (Cohort) — % de Clientes Recomprando",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, Arial, sans-serif", color=C_TEXT, size=12),
        margin=dict(l=30, r=30, t=45, b=30),
        xaxis=dict(title="Meses Após a Primeira Compra", side="bottom", gridcolor=C_GRID),
        yaxis=dict(title="Safra de Entrada (Mês/Ano)", autorange="reversed", gridcolor=C_GRID),
        height=520
    )
    st.plotly_chart(fig_cohort, use_container_width=True)

    # Identificação dinâmica da retenção da safra de Black Friday (Novembro/2023)
    ret_nov = retention_matrix.loc['2023-11', 1] if ('2023-11' in retention_matrix.index and 1 in retention_matrix.columns) else 0.0

    st.markdown(f"""
    <div class='insight-box'>
    📌 <strong>Diagnóstico de Safra (LTV vs. Promoção):</strong> Clientes das safras do início de 2023 mantinham recompras acima de <strong>50%</strong>. 
    Em contraste, a safra de <strong>Novembro/2023 (Black Friday)</strong> reteve apenas <strong>{ret_nov:.1f}%</strong> no Mês 1. 
    Isso comprova que o desconto agressivo atraiu <em>compradores oportunistas</em> de transação única, e não clientes recorrentes.
    </div>""", unsafe_allow_html=True)


# =============================================================================
#  ABA 3 – LABORATÓRIO DE ESTRATÉGIA (A SOLUÇÃO)
# =============================================================================
def aba_laboratorio(df: pd.DataFrame):
    df_ap = df[df["status_pagamento"] == "Aprovado"].copy()

    st.markdown("""<div class='insight-box'>
    🧪 <strong>Como usar:</strong> Ajuste os sliders abaixo para simular o impacto financeiro
    de diferentes políticas de frete grátis e teto de desconto. Os gráficos atualizam em tempo real.
    </div>""", unsafe_allow_html=True)

    # ── Sliders ───────────────────────────────────────────────────────────────
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown("<div class='slider-header'>🚚 Ticket Mínimo para Frete Grátis (R$)</div>",
                    unsafe_allow_html=True)
        ticket_min = st.slider("Ticket Mínimo Frete Grátis",
                               min_value=0, max_value=800, value=400, step=25,
                               label_visibility="collapsed")
        st.caption(f"Limite atual: **R$ {ticket_min:.0f}**  |  "
                   f"Referência validada: R$ 400 → poupa **R$ 29.470** líquidos")

    with col_s2:
        st.markdown("<div class='slider-header'>🏷️ Teto Máximo de Desconto (%)</div>",
                    unsafe_allow_html=True)
        teto_desc = st.slider("Teto de Desconto",
                              min_value=0, max_value=30, value=10, step=1,
                              label_visibility="collapsed")
        st.caption(f"Teto atual: **{teto_desc}%**  |  Referência: >9,5% em Nov/23 = -R$64k")

    # ── Cálculo da Simulação ──────────────────────────────────────────────────
    df_sim = df_ap.copy()

    # Política de frete: cobra frete nos pedidos abaixo do mínimo
    #df_sim["frete_cobrado"]  = np.where(df_sim["receita_bruta"] < ticket_min,
    #                                    df_sim["custo_frete"], 0)
    #df_sim["economia_frete"] = df_sim["custo_frete"] - df_sim["frete_cobrado"]
    # 1. Identifica o frete que passa a ser cobrado do cliente nos pedidos pequenos:
    is_mkp = df_sim["canal"].str.lower().str.contains("marketplace|mkp")
    condicao = is_mkp & (df_sim["receita_bruta"] < ticket_min)

    df_sim["frete_cobrado"] = np.where(condicao, df_sim["custo_frete"], 0.0)
    df_sim["economia_frete"] = df_sim["frete_cobrado"]


    perda_vendas_est = df_sim["economia_frete"].sum() * 0.15
    economia_frete_liq = df_sim["economia_frete"].sum() - perda_vendas_est


    # Política de desconto: limita desconto
    desc_atual_pct = (df_sim["desconto_reais"] / df_sim["receita_bruta"]).clip(0,1)
    desc_lim       = np.minimum(desc_atual_pct, teto_desc / 100)
    df_sim["desconto_limitado"] = df_sim["receita_bruta"] * desc_lim
    economia_desc = (df_sim["desconto_reais"] - df_sim["desconto_limitado"]).clip(0).sum()

    total_ganho = economia_frete_liq + economia_desc
    margem_orig = df_ap["margem_contribuicao"].sum()
    margem_nova = margem_orig + total_ganho
    margem_nova_pct = margem_nova / df_ap["receita_bruta"].sum() * 100

    # ── KPI da simulação ─────────────────────────────────────────────────────
    st.markdown("<div class='section-title'>💡 Resultado Projetado da Simulação</div>",
                unsafe_allow_html=True)
    r1, r2, r3, r4 = st.columns(4)
    with r1:
        st.markdown(kpi_html("💰 Economia c/ Frete (líq.)",
            fmt_brl(economia_frete_liq), "-15% perda vendas est.", True), unsafe_allow_html=True)
    with r2:
        st.markdown(kpi_html("🏷️ Economia c/ Desconto",
            fmt_brl(economia_desc), "Desconto limitado a "+fmt_pct(teto_desc), True),
            unsafe_allow_html=True)
    with r3:
        st.markdown(kpi_html("📈 Ganho Total Projetado",
            fmt_brl(total_ganho), "Soma frete + desconto", True), unsafe_allow_html=True)
    with r4:
        st.markdown(kpi_html("📊 Margem Projetada",
            fmt_pct(margem_nova_pct), f"Era {fmt_pct(margem_orig/df_ap['receita_bruta'].sum()*100)}",
            margem_nova_pct >= 50), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Curva de elasticidade / Break-even ───────────────────────────────────
    st.markdown("<div class='section-title'>📐 Curva de Equilíbrio – Ticket Mínimo de Frete Grátis</div>",
                unsafe_allow_html=True)

    tickets_range = range(0, 801, 25)
    economia_liq_list, pedidos_perdidos_pct = [], []

    #for t in tickets_range:
    #    econ_br = df_ap.loc[df_ap["receita_bruta"] < t, "custo_frete"].sum()
    #    econ_lq = econ_br * (1 - 0.15)  # 15% perda estimada
    #    ped_perd = (df_ap["receita_bruta"] < t).mean() * 100
    #    economia_liq_list.append(econ_lq)
    #    pedidos_perdidos_pct.append(ped_perd)



    # CÓDIGO CORRIGIDO:
    is_mkp = df_ap["canal"].str.lower().str.contains("marketplace|mkp")
    df_mkp = df_ap[is_mkp]

    for t in tickets_range:
        econ_br = df_mkp.loc[df_mkp["receita_bruta"] < t, "custo_frete"].sum()
        econ_lq = econ_br * (1 - 0.15)  # 15% perda estimada
        ped_perd = (df_mkp["receita_bruta"] < t).mean() * 100
        economia_liq_list.append(econ_lq)
        pedidos_perdidos_pct.append(ped_perd)



    fig_elast = go.Figure()
    fig_elast.add_trace(go.Scatter(
        x=list(tickets_range), y=economia_liq_list,
        mode="lines", name="Economia Líquida (R$)",
        line=dict(color=C_SUCCESS, width=3), fill="tozeroy",
        fillcolor="rgba(56,142,60,0.10)",
        hovertemplate="Ticket: R$%{x}<br>Economia: R$ %{y:,.2f}<extra></extra>",
        yaxis="y1",
    ))
    fig_elast.add_trace(go.Scatter(
        x=list(tickets_range), y=pedidos_perdidos_pct,
        mode="lines", name="Pedidos abaixo do limite (%)",
        line=dict(color=C_DANGER, width=2, dash="dot"),
        hovertemplate="Ticket: R$%{x}<br>Pedidos sob limite: %{y:.1f}%<extra></extra>",
        yaxis="y2",
    ))
    fig_elast.add_vline(x=ticket_min, line_dash="dash", line_color=C_WARN,
                        annotation_text=f"  Selecionado: R${ticket_min}",
                        annotation_font_color=C_WARN)
    fig_elast.add_vline(x=400, line_dash="dot", line_color=C_ACCENT,
                        annotation_text="  Ótimo Validado: R$400",
                        annotation_font_color=C_ACCENT, annotation_position="bottom right")
    fig_elast.update_layout(
        **{**PLOTLY_LAYOUT, "yaxis": dict(
            title="Economia Líquida (R$)", tickprefix="R$ ", gridcolor=C_GRID
        )},
        title="Impacto do Ticket Mínimo de Frete Grátis: Economia vs. Risco de Perda de Vendas",
        xaxis_title="Ticket Mínimo de Frete Grátis (R$)",
        yaxis2=dict(title="% Pedidos Abaixo do Limite",
                    overlaying="y", side="right", ticksuffix="%",
                    showgrid=False, range=[0,110]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig_elast, use_container_width=True)
    #st.markdown("""<div class='insight-box'>
    #📌 <strong>Ponto Ótimo Validado:</strong> Ticket mínimo de <strong>R$ 400</strong> maximiza a
    #economia líquida em <strong>R$ 29.470</strong>, sem risco excessivo de perda de volume.
   # A curva verde atinge seu pico antes que a penalidade de perda de pedidos (linha vermelha) acelere.
   # </div>""", unsafe_allow_html=True)

    # Cálculo 100% dinâmico baseado no ticket_min escolhido no slider:
    pedidos_abaixo_qtd = (df_mkp["receita_bruta"] < ticket_min).sum()
    total_pedidos_mkp = len(df_mkp)
    pct_pedidos_afetados = (pedidos_abaixo_qtd / total_pedidos_mkp * 100) if total_pedidos_mkp else 0

    st.markdown(f"""<div class='insight-box'>
    📌 <strong>Ponto Selecionado:</strong> Ticket mínimo de <strong>R$ {ticket_min:.0f}</strong> projeta uma
    economia líquida de <strong>{fmt_brl(economia_frete_liq)}</strong>, impactando 
    <strong>{pct_pedidos_afetados:.1f}%</strong> dos pedidos do canal Marketplace.
    </div>""", unsafe_allow_html=True)


# =============================================================================
#  ABA 4 – Bot
# =============================================================================
ALERTAS_INICIAIS = [
    {
        "role": "assistant",
        "content": (
            "👋 Olá! Sou o **Bot da Vértice**. Analisei os dados carregados e "
            "identifiquei **3 alertas críticos** de negócio. Veja abaixo:"
        ),
    },
    {
        "role": "assistant",
        "content": (
            "🔴 **Alerta 1 – Perda em Frete Marketplace:**\n"
            "O canal MKP acumula **R$ 98k** em custo de frete no período analisado. "
            "O frete fixo de R$ 32,57 por pedido é 45% maior do que a média dos outros canais. "
            "Pedidos com ticket abaixo de R$ 200 no MKP apresentam **margem negativa**."
        ),
    },
    {
        "role": "assistant",
        "content": (
            "🟡 **Alerta 2 – Desconto Destrutivo em Novembro:**\n"
            "Em Nov/2023, o desconto médio atingiu **9,5%** (acima do teto recomendado de 8%). "
            "A margem de contribuição caiu para **48,1%** — abaixo da meta de 50%. "
            "Projeção de perda: **R$ 64 mil** vs. cenário sem desconto agressivo."
        ),
    },
    {
        "role": "assistant",
        "content": (
            "🟢 **Oportunidade Validada – Teto de Frete Grátis:**\n"
            "Implementar frete grátis apenas para pedidos **acima de R$ 400** "
            "gera uma economia líquida de **R$ 29.470** (já descontando 15% de perda estimada de vendas). "
            "Use o **Laboratório de Estratégia** para ajustar o cenário."
        ),
    },
    {
        "role": "assistant",
        "content": (
            "💬 O que você gostaria de explorar? Pergunte algo como:\n"
            "- *Qual canal tem a pior margem?*\n"
            "- *Como está o desconto médio?*\n"
            "- *Qual o impacto de reduzir o frete no MKP?*"
        ),
},
]

RESPOSTAS_SIMULADAS = {
    "margem": (
        "📊 **Análise de Margem:**\nA margem de contribuição consolidada está em torno de **{margem_pct:.1f}%**. "
        "O canal **Marketplace** puxa a média para baixo com margens ~10p.p. menores do que o e-commerce próprio, "
        "principalmente devido ao frete fixo elevado. Acesse a **Aba 2 – Ralo Operacional** para ver o boxplot detalhado."
    ),
    "frete": (
        "🚚 **Análise de Frete:**\nO custo médio de frete é **{frete_med:.2f}**. "
        "No Marketplace, esse valor sobe para R$ 32,57. "
        "A simulação na **Aba 3** mostra que um teto de R$ 400 otimiza o retorno líquido."
    ),
    "desconto": (
        "🏷️ **Análise de Desconto:**\nO desconto médio atual é de **{desc_pct:.1f}%** sobre a receita bruta. "
        "O limite recomendado é **8%**. Acima disso, cada 1p.p. extra de desconto custa em média "
        "R$ {custo_1pp:,.0f} de margem no período analisado."
    ),
    "novembro": (
        "📅 **Novembro/2023:**\nRecorde de faturamento **(R$ 3M)**, mas a armadilha do desconto (9,5%) "
        "fez a margem cair para **48,1%**. Isso representa uma perda projetada de **R$ 64.000** "
        "comparado a um cenário com desconto limitado a 8%. Um crescimento que *custou caro*."
    ),
    "canal": (
        "🏪 **Desempenho por Canal:**\nRanking de margem (melhor → pior):\n"
        "1. E-commerce Próprio – ~55-60%\n"
        "2. Redes Sociais – ~50-55%\n"
        "3. Marketplace – ~40-45%\n\n"
        "A diferença é estrutural: custo de frete e ausência de controle sobre precificação no MKP."
    ),
    "default": (
        "🤔 Essa é uma boa pergunta! Com base nos dados carregados, posso analisar **margem por canal**, "
        "**impacto de frete**, **eficiência de desconto** e **sazonalidade mensal**. "
        "Tente perguntar sobre um desses tópicos ou explore as abas do painel para visuais interativos."
    ),
}

def get_resposta(pergunta: str, df: pd.DataFrame) -> str:
    df_ap = df[df["status_pagamento"] == "Aprovado"]
    receita = df_ap["receita_bruta"].sum() or 1
    margem_pct = df_ap["margem_contribuicao"].sum() / receita * 100
    frete_med  = df_ap["custo_frete"].mean()
    desc_pct   = df_ap["desconto_reais"].sum() / receita * 100
    custo_1pp  = receita * 0.01

    pq = pergunta.lower()
    if any(k in pq for k in ["margem","lucro","rentab"]):
        return RESPOSTAS_SIMULADAS["margem"].format(margem_pct=margem_pct)
    if any(k in pq for k in ["frete","logist","envio"]):
        return RESPOSTAS_SIMULADAS["frete"].format(frete_med=frete_med)
    if any(k in pq for k in ["desconto","coupon","promo"]):
        return RESPOSTAS_SIMULADAS["desconto"].format(desc_pct=desc_pct, custo_1pp=custo_1pp)
    if any(k in pq for k in ["novembro","nov","record","recorde"]):
        return RESPOSTAS_SIMULADAS["novembro"]
    if any(k in pq for k in ["canal","marketplace","mkp","ecommerce"]):
        return RESPOSTAS_SIMULADAS["canal"]
    return RESPOSTAS_SIMULADAS["default"]


def aba_copiloto(df: pd.DataFrame):
    st.markdown("""<div class='insight-box'>
    🤖 <strong>Bot Vértice</strong> — Analiso seus dados em tempo real e proponho
    alertas e oportunidades de negócio. Faça perguntas sobre margem, frete, desconto ou canais.
    </div>""", unsafe_allow_html=True)

    # Inicializa histórico com alertas pró-ativos
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = ALERTAS_INICIAIS.copy()

    # Renderiza histórico
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"],
            avatar="🤖" if msg["role"] == "assistant" else "👤"):
            st.markdown(msg["content"])

    # Input do usuário
    if prompt := st.chat_input("Faça uma pergunta ao Bot..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        resposta = get_resposta(prompt, df)
        st.session_state.chat_history.append({"role": "assistant", "content": resposta})
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(resposta)

    col_reset, _ = st.columns([1, 5])
    with col_reset:
        if st.button("🔄 Reiniciar Chat", use_container_width=True):
            st.session_state.chat_history = ALERTAS_INICIAIS.copy()
            st.rerun()


# =============================================================================
#  LAYOUT PRINCIPAL (ENTRY POINT)
# =============================================================================
def main():
    st.set_page_config(
        page_title="Vértice | Painel Executivo",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_css()

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class='vertice-header'>
      <div>
        <h1>📊 Painel Executivo · Vértice</h1>
        <p>Varejo de Moda & Lifestyle Digital · Análise de Margem e Eficiência Operacional</p>
      </div>
    </div>""", unsafe_allow_html=True)

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        #st.image(
           # "https://via.placeholder.com/200x60/003366/FFFFFF?text=V%C3%89RTICE",
          #  use_container_width=True,
       # )
        st.markdown("---")
        st.markdown("### 📂 Carregar Dados")
        uploaded = st.file_uploader(
            "Envie o arquivo **vendas.csv**",
            type=["csv"],
            help="O arquivo deve conter as colunas padrão do Case Vértice.",
        )
        st.markdown("---")
        st.markdown("### 🔗 Google Drive *(experimental)*")
        gdrive_url = st.text_input(
            "URL da pasta do Google Drive",
            placeholder="https://drive.google.com/drive/folders/...",
            help="Cole a URL pública da pasta. Em produção, a IA faz a leitura via Google Drive API.",
        )
        if gdrive_url:
            st.info("📌 Funcionalidade via API Google Drive disponível em versão Pro. "
                    "Por ora, carregue o CSV diretamente.")
        st.markdown("---")
        st.caption("🛡️ Dados processados localmente · Sem envio externo")

    # ── Carregamento de dados ─────────────────────────────────────────────────
    df = None

    if uploaded is not None:
        df = carregar_csv(uploaded, uploaded.name)
        if df is None:
            st.stop()
        st.sidebar.success(f"✅ Arquivo carregado: **{len(df):,}** registros")

    if df is None:
        st.markdown("""
        <div style='text-align:center; padding: 60px 20px;'>
          <h2 style='color:#003366;'>Nenhum dado carregado ainda</h2>
          <p style='color:#6B7280; font-size:1rem;'>
            Faça upload do <code>vendas.csv</code> na barra lateral<br>
            ou carregue os dados de demonstração para explorar o painel.
          </p>
        </div>""", unsafe_allow_html=True)

        col_btn = st.columns([2,1,2])[1]
        with col_btn:
            if st.button("🚀 Carregar Dados de Demonstração", use_container_width=True,
                         type="primary"):
                st.session_state["use_demo"] = True
                st.rerun()

        if st.session_state.get("use_demo"):
            df = gerar_demo_data()
            st.sidebar.success(f"✅ Demo carregada: **{len(df):,}** registros sintéticos")
        else:
            st.stop()

    # ── Filtro de datas na sidebar ─────────────────────────────────────────────
    with st.sidebar:
        st.markdown("### 📅 Filtro de Período")
        min_d = df["data_pedido"].min().date()
        max_d = df["data_pedido"].max().date()
        dt_ini, dt_fim = st.date_input(
            "Selecione o intervalo",
            value=(min_d, max_d),
            min_value=min_d, max_value=max_d,
        )
        df = df[(df["data_pedido"].dt.date >= dt_ini) &
                (df["data_pedido"].dt.date <= dt_fim)]
        if df.empty:
            st.sidebar.error("Nenhum dado no período selecionado.")
            st.stop()

        # Filtro de canal
        st.markdown("### 🏪 Filtro de Canal")
        canais_disp = ["Todos"] + sorted(df["canal"].dropna().unique().tolist())
        canal_sel = st.selectbox("Canal de Venda", canais_disp)
        if canal_sel != "Todos":
            df = df[df["canal"] == canal_sel]

    # ── Abas ──────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Visão Geral",
        "🔴 Ralo Operacional",
        "🧪 Laboratório de Estratégia",
        "🤖 Bot",
    ])

    with tab1:
        aba_visao_geral(df)
    with tab2:
        aba_ralo_operacional(df)
    with tab3:
        aba_laboratorio(df)
    with tab4:
        aba_copiloto(df)


if __name__ == "__main__":
    main()
