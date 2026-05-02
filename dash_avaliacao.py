import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(
    page_title="Dashboard de Avaliações",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ======================================================
# TEMA VISUAL GLOBAL
# ======================================================

st.markdown("""
<style>
    /* Fundo geral */
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    }

    /* Títulos */
    h1 { font-size: 2.8rem !important; font-weight: 900 !important; color: #ffffff !important; }
    h2 { font-size: 2rem !important; font-weight: 800 !important; color: #e0e0ff !important; }
    h3 { font-size: 1.6rem !important; font-weight: 700 !important; color: #c0c0ff !important; }

    /* Texto geral maior */
    p, div, span, label { font-size: 1.05rem !important; }

    /* Cards de métricas */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #1a1a3e, #2d2d6b);
        border: 1px solid #4444aa;
        border-radius: 16px;
        padding: 20px !important;
        box-shadow: 0 0 20px rgba(100, 100, 255, 0.3);
    }
    [data-testid="metric-container"] label {
        font-size: 1rem !important;
        color: #aaaaff !important;
        font-weight: 700 !important;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 900 !important;
        color: #ffffff !important;
    }

    /* Selectbox */
    .stSelectbox label { font-size: 1.1rem !important; font-weight: 700 !important; color: #aaaaff !important; }

    /* Tabelas */
    .stDataFrame { border-radius: 12px; overflow: hidden; }

    /* Divisores */
    hr { border-color: #4444aa !important; opacity: 0.4; }

    /* Botões de download */
    .stDownloadButton button {
        background: linear-gradient(135deg, #6600cc, #9900ff) !important;
        color: white !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        font-size: 1rem !important;
        border: none !important;
    }

    /* Cards destacados de métricas principais */
    .metric-principal {
        background: linear-gradient(135deg, #2d1b69, #4a2c8e);
        border: 2px solid #7c5cdb;
        border-radius: 20px;
        padding: 30px !important;
        box-shadow: 0 0 30px rgba(124, 92, 219, 0.4);
        text-align: center;
    }
    
    .metric-principal-value {
        font-size: 3.5rem !important;
        font-weight: 900 !important;
        color: #FFE66D !important;
        margin: 10px 0;
    }
    
    .metric-principal-label {
        font-size: 1.3rem !important;
        color: #c0c0ff !important;
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)

# Paleta de cores vibrantes para os gráficos
CORES_VIBRANTES = [
    "#FF6B6B", "#FFE66D", "#4ECDC4", "#A855F7",
    "#F97316", "#22D3EE", "#10B981", "#F43F5E",
    "#6366F1", "#84CC16", "#EC4899", "#14B8A6",
    "#F59E0B", "#8B5CF6", "#06B6D4", "#EF4444"
]

TEMPLATE_GRAFICO = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(15,12,41,0.0)",
    plot_bgcolor="rgba(15,12,41,0.0)",
    font=dict(family="Inter, sans-serif", size=14, color="#e0e0ff"),
    title_font=dict(size=20, color="#ffffff", family="Inter, sans-serif"),
)

# ======================================================
# CARREGAMENTO DOS DADOS
# ======================================================

@st.cache_data
def load_data():
    paths = [
        ('arquivos_30_04_26/', 'Pasta arquivos'),
        ('arquivos/', 'Pasta arquivos'),
        ('', 'Raiz do repositório'),
    ]
    for path_prefix, _ in paths:
        try:
            avaliacoes = pd.read_excel(f'{path_prefix}avaliacoes.xlsx')
            vendedoras = pd.read_excel(f'{path_prefix}vendedoras.xlsx')
            lojas = pd.read_excel(f'{path_prefix}lojas.xlsx')
            supervisores = pd.read_excel(f'{path_prefix}supervisores.xlsx')
            supervisores_lojas = pd.read_excel(f'{path_prefix}supervisores_lojas.xlsx')
            return avaliacoes, vendedoras, lojas, supervisores, supervisores_lojas
        except Exception:
            continue
    raise FileNotFoundError("❌ Arquivos Excel não encontrados!")

try:
    avaliacoes, vendedoras, lojas, supervisores, supervisores_lojas = load_data()
except FileNotFoundError as e:
    st.error(str(e))
    st.stop()

# ======================================================
# PROCESSAMENTO
# ======================================================

for df in [avaliacoes, vendedoras, lojas, supervisores, supervisores_lojas]:
    df.columns = df.columns.str.lower().str.strip()

vendedoras   = vendedoras.rename(columns={'lojaid': 'loja_id', '_id': 'id'})
avaliacoes   = avaliacoes.rename(columns={'_id': 'id', 'vendedoraid': 'vendedora_id', 'supervisorid': 'supervisor_id', 'lojaid': 'loja_id'})
supervisores = supervisores.rename(columns={'_id': 'id'})
lojas        = lojas.rename(columns={'_id': 'id'})

avaliacoes['estrela_1_5']       = pd.to_numeric(avaliacoes['estrela_1_5'], errors='coerce')
avaliacoes['recomendacao_1_10'] = pd.to_numeric(avaliacoes['recomendacao_1_10'], errors='coerce')

aval_vendedoras  = avaliacoes[avaliacoes['tipo'] == 'vendedora'].copy()
aval_supervisores = avaliacoes[avaliacoes['tipo'] == 'supervisor'].copy()

# ======================================================
# HEADER
# ======================================================

st.markdown("""
<div style='text-align:center; padding: 2rem 0 1rem 0;'>
    <h1>⭐ Dashboard de Avaliações</h1>
    <p style='color:#aaaaff; font-size:1.2rem !important;'>Análise completa de Vendedoras, Supervisores e Lojas</p>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

# ======================================================
# 1. OVERVIEW - VERSÃO DESTACADA
# ======================================================

st.markdown("## 📊 Visão Geral da Empresa")

total_aval           = len(avaliacoes)
media_estrela        = avaliacoes['estrela_1_5'].mean()
media_recomendacao   = avaliacoes['recomendacao_1_10'].mean()
bem_atendimento_sim  = (avaliacoes['bem_atendimento'] == 'sim').sum() / len(avaliacoes) * 100
total_vendedoras_num = len(vendedoras)

# Primeira linha - Métricas principais em destaque
st.markdown("### 📈 Métricas Principais")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class='metric-principal'>
        <div class='metric-principal-label'>Total de Avaliações</div>
        <div class='metric-principal-value'>{total_aval:,}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class='metric-principal'>
        <div class='metric-principal-label'>Média de Estrelas</div>
        <div class='metric-principal-value'>{media_estrela:.2f}/5.0</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class='metric-principal'>
        <div class='metric-principal-label'>Taxa de Bem Atendimento</div>
        <div class='metric-principal-value'>{bem_atendimento_sim:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

# Segunda linha - Métricas complementares
st.markdown("### 📊 Métricas Complementares")
col4, col5, col6 = st.columns(3)

col4.metric("👍 Média de Recomendação", f"{media_recomendacao:.2f}/10")
col5.metric("👥 Total de Vendedoras", f"{total_vendedoras_num:,}")
col6.metric("🏪 Total de Lojas", f"{len(lojas):,}")

st.markdown("---")

# ======================================================
# 2. DISTRIBUIÇÃO DE ESTRELAS E ATENDIMENTO
# ======================================================

st.markdown("## 1️⃣  Distribuição Geral")

col_pizza1, col_pizza2 = st.columns(2)

with col_pizza1:
    dist_estrelas = avaliacoes['estrela_1_5'].value_counts().sort_index()

    fig = go.Figure(data=[go.Pie(
        labels=[f"{int(i)} estrela(s)" for i in dist_estrelas.index],
        values=dist_estrelas.values,
        hole=0.4,
        marker=dict(colors=CORES_VIBRANTES, line=dict(color="#0f0c29", width=3)),
        textfont=dict(size=16),
    )])
    fig.update_layout(
        **TEMPLATE_GRAFICO,
        title="⭐ Distribuição de Estrelas",
        height=420,
        legend=dict(font=dict(size=14)),
    )
    st.plotly_chart(fig, width='stretch', key="pizza_estrelas")

with col_pizza2:
    dist_atendimento = avaliacoes['bem_atendimento'].value_counts()

    fig2 = go.Figure(data=[go.Pie(
        labels=dist_atendimento.index,
        values=dist_atendimento.values,
        hole=0.4,
        marker=dict(colors=["#10B981", "#F97316", "#F43F5E"], line=dict(color="#0f0c29", width=3)),
        textfont=dict(size=16),
    )])
    fig2.update_layout(
        **TEMPLATE_GRAFICO,
        title="😊 Bem Atendimento",
        height=420,
        legend=dict(font=dict(size=14)),
    )
    st.plotly_chart(fig2, width='stretch', key="pizza_atendimento")

st.markdown("---")

# ======================================================
# 3. RANKING VENDEDORAS
# ======================================================

st.markdown("## 2️⃣  Ranking de Vendedoras")

aval_vend_completa = aval_vendedoras.merge(
    vendedoras[['id', 'vendedora', 'loja_id']],
    left_on='vendedora_id', right_on='id', how='left', suffixes=('', '_vend')
)
if 'loja_id_vend' in aval_vend_completa.columns:
    aval_vend_completa['loja_id'] = aval_vend_completa['loja_id_vend']

aval_vend_completa = aval_vend_completa.merge(
    lojas[['id', 'loja']], left_on='loja_id', right_on='id', how='left'
)

ranking_vend = aval_vend_completa.groupby(['vendedora', 'loja']).agg({
    'estrela_1_5': ['mean', 'count'],
    'recomendacao_1_10': 'mean',
    'bem_atendimento': lambda x: (x == 'sim').sum() / len(x) * 100
}).reset_index()

ranking_vend.columns = ['Vendedora', 'Loja', 'Média Estrelas', 'Total Avaliações', 'Média Recomendação', '% Bem Atendimento']

max_aval = ranking_vend['Total Avaliações'].max()
ranking_vend['Volume Normalizado'] = (ranking_vend['Total Avaliações'] / max_aval) * 5
ranking_vend['Score Final'] = ranking_vend['Média Estrelas'] * 0.7 + ranking_vend['Volume Normalizado'] * 0.3
ranking_vend = ranking_vend.sort_values('Score Final', ascending=False)

top15 = ranking_vend.head(15)

# Gradiente de cor por score
cores_ranking = px.colors.sample_colorscale("Viridis", [i / len(top15) for i in range(len(top15))])

fig_rank = go.Figure(data=[go.Bar(
    y=top15['Vendedora'],
    x=top15['Score Final'],
    orientation='h',
    text=top15['Score Final'].round(2),
    textposition='outside',
    textfont=dict(size=14, color="#ffffff"),
    marker=dict(
        color=top15['Score Final'],
        colorscale="Plasma",
        showscale=True,
        colorbar=dict(title="Score", tickfont=dict(size=13)),
        line=dict(color="rgba(255,255,255,0.1)", width=1)
    ),
)])

fig_rank.update_layout(
    **TEMPLATE_GRAFICO,
    title="🏆 Top 15 Vendedoras",
    height=550,
    xaxis=dict(title="Score Final", tickfont=dict(size=13)),
    yaxis=dict(tickfont=dict(size=13), autorange="reversed"),
)

st.plotly_chart(fig_rank, width='stretch', key="ranking_vendedoras")
st.dataframe(ranking_vend.round(2), width='stretch', hide_index=True)
st.markdown("---")

# ======================================================
# 4. DETALHES INDIVIDUAIS DE VENDEDORAS
# ======================================================

st.markdown("## 3️⃣  Detalhes por Vendedora")

lista_vendedoras_sel = sorted(ranking_vend['Vendedora'].dropna().unique().tolist())

if lista_vendedoras_sel:
    vendedora_selecionada = st.selectbox("Selecione uma vendedora:", lista_vendedoras_sel)
    aval_sel = aval_vend_completa[aval_vend_completa['vendedora'] == vendedora_selecionada]

    if len(aval_sel) > 0:
        loja_vend = aval_sel['loja'].iloc[0] if not aval_sel['loja'].isna().all() else "Sem Loja"

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("⭐ Média Estrelas",    f"{aval_sel['estrela_1_5'].mean():.2f}/5")
        col2.metric("👍 Média Rec.",        f"{aval_sel['recomendacao_1_10'].mean():.2f}/10")
        pct = (aval_sel['bem_atendimento'] == 'sim').sum() / len(aval_sel) * 100
        col3.metric("😊 Bem Atendimento",  f"{pct:.1f}%")
        col4.metric("📝 Total",             len(aval_sel))
        col5.metric("🏪 Loja",             loja_vend)

        st.markdown("---")
        c1, c2 = st.columns(2)

        with c1:
            dist = aval_sel['estrela_1_5'].value_counts().sort_index()
            fig = go.Figure(data=[go.Bar(
                x=dist.index, y=dist.values,
                text=dist.values, textposition='outside',
                textfont=dict(size=15),
                marker=dict(
                    color=dist.values,
                    colorscale="Turbo",
                    line=dict(color="rgba(255,255,255,0.2)", width=1)
                ),
            )])
            fig.update_layout(
                **TEMPLATE_GRAFICO,
                title=f"⭐ Estrelas — {vendedora_selecionada}",
                height=400,
                xaxis=dict(tickfont=dict(size=14)),
                yaxis=dict(tickfont=dict(size=14)),
            )
            st.plotly_chart(fig, width='stretch', key=f"dist_estrelas_{vendedora_selecionada}")

        with c2:
            dist2 = aval_sel['bem_atendimento'].value_counts()
            fig2 = go.Figure(data=[go.Pie(
                labels=dist2.index, values=dist2.values,
                hole=0.45,
                marker=dict(colors=["#10B981", "#F97316", "#F43F5E"], line=dict(color="#0f0c29", width=3)),
                textfont=dict(size=15),
            )])
            fig2.update_layout(
                **TEMPLATE_GRAFICO,
                title=f"😊 Atendimento — {vendedora_selecionada}",
                height=400,
                legend=dict(font=dict(size=14)),
            )
            st.plotly_chart(fig2, width='stretch', key=f"atend_{vendedora_selecionada}")

        st.markdown("**💬 Comentários:**")
        comentarios = aval_sel[aval_sel['comentario_cliente'].notna()]
        if len(comentarios) > 0:
            for _, row in comentarios.iterrows():
                st.markdown(f"""
                <div style='background:linear-gradient(135deg,#1a1a3e,#2d2d6b);border-left:4px solid #A855F7;
                            border-radius:10px;padding:14px 18px;margin-bottom:10px;'>
                    <span style='color:#FFE66D;font-size:1.1rem;font-weight:700;'>
                        {"⭐" * int(row['estrela_1_5'])} ({int(row['estrela_1_5'])}/5)
                    </span><br>
                    <span style='color:#e0e0ff;font-size:1rem;'>{row['comentario_cliente']}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Nenhum comentário encontrado.")

st.markdown("---")

# ======================================================
# 5. RANKING SUPERVISORES
# ======================================================

st.markdown("## 4️⃣  Ranking de Supervisores")

if len(aval_supervisores) > 0:
    aval_sup_completa = aval_supervisores.merge(
        supervisores[['id', 'nome_supervisor']],
        left_on='supervisor_id', right_on='id', how='left'
    )

    ranking_sup = aval_sup_completa.groupby('nome_supervisor').agg({
        'estrela_1_5': ['mean', 'count'],
        'recomendacao_1_10': 'mean',
        'bem_atendimento': lambda x: (x == 'sim').sum() / len(x) * 100
    }).reset_index()

    ranking_sup.columns = ['Supervisor', 'Média Estrelas', 'Total Avaliações', 'Média Recomendação', '% Bem Atendimento']

    max_sup = ranking_sup['Total Avaliações'].max()
    ranking_sup['Volume'] = (ranking_sup['Total Avaliações'] / max_sup) * 5
    ranking_sup['Score Final'] = ranking_sup['Média Estrelas'] * 0.7 + ranking_sup['Volume'] * 0.3
    ranking_sup = ranking_sup.sort_values('Score Final', ascending=False)

    fig_sup = go.Figure(data=[go.Bar(
        y=ranking_sup['Supervisor'],
        x=ranking_sup['Score Final'],
        orientation='h',
        text=ranking_sup['Score Final'].round(2),
        textposition='outside',
        textfont=dict(size=14, color="#ffffff"),
        marker=dict(
            color=ranking_sup['Score Final'],
            colorscale="Rainbow",
            showscale=True,
            colorbar=dict(title="Score", tickfont=dict(size=13)),
            line=dict(color="rgba(255,255,255,0.1)", width=1)
        ),
    )])

    fig_sup.update_layout(
        **TEMPLATE_GRAFICO,
        title="🏆 Ranking Supervisores",
        height=500,
        xaxis=dict(title="Score Final", tickfont=dict(size=13)),
        yaxis=dict(tickfont=dict(size=13), autorange="reversed"),
    )

    st.plotly_chart(fig_sup, width='stretch', key="ranking_supervisores")
    st.dataframe(ranking_sup.round(2), width='stretch', hide_index=True)
else:
    st.info("Nenhuma avaliação de supervisor encontrada.")

st.markdown("---")

# ======================================================
# 6. RANKING LOJAS
# ======================================================

st.markdown("## 5️⃣  Ranking de Lojas")

aval_loja_completa = avaliacoes.merge(
    lojas[['id', 'loja']], left_on='loja_id', right_on='id', how='left'
)

ranking_loja = aval_loja_completa.groupby('loja').agg({
    'estrela_1_5': ['mean', 'count'],
    'recomendacao_1_10': 'mean',
    'bem_atendimento': lambda x: (x == 'sim').sum() / len(x) * 100
}).reset_index()

ranking_loja.columns = ['Loja', 'Média Estrelas', 'Total Avaliações', 'Média Recomendação', '% Bem Atendimento']

max_loja = ranking_loja['Total Avaliações'].max()
ranking_loja['Volume'] = (ranking_loja['Total Avaliações'] / max_loja) * 5
ranking_loja['Score Final'] = ranking_loja['Média Estrelas'] * 0.7 + ranking_loja['Volume'] * 0.3
ranking_loja = ranking_loja.sort_values('Score Final', ascending=False)

fig_loja = go.Figure(data=[go.Bar(
    y=ranking_loja['Loja'].head(20),
    x=ranking_loja['Score Final'].head(20),
    orientation='h',
    text=ranking_loja['Score Final'].head(20).round(2),
    textposition='outside',
    textfont=dict(size=14, color="#ffffff"),
    marker=dict(
        color=ranking_loja['Score Final'].head(20),
        colorscale="Turbo",
        showscale=True,
        colorbar=dict(title="Score", tickfont=dict(size=13)),
        line=dict(color="rgba(255,255,255,0.1)", width=1)
    ),
)])

fig_loja.update_layout(
    **TEMPLATE_GRAFICO,
    title="🏪 Top 20 Lojas",
    height=600,
    xaxis=dict(title="Score Final", tickfont=dict(size=13)),
    yaxis=dict(tickfont=dict(size=13), autorange="reversed"),
)

st.plotly_chart(fig_loja, width='stretch', key="ranking_lojas")
st.dataframe(ranking_loja.round(2), width='stretch', hide_index=True)
st.markdown("---")

# ======================================================
# 7. VENDEDORAS SEM AVALIAÇÃO
# ======================================================

st.markdown("## 🚨 Vendedoras Sem Avaliação")

ids_avaliadas = aval_vendedoras['vendedora_id'].dropna().unique()
vendedoras_sem = vendedoras[~vendedoras['id'].isin(ids_avaliadas)].copy()
vendedoras_sem = vendedoras_sem.merge(lojas[['id', 'loja']], left_on='loja_id', right_on='id', how='left')

if len(vendedoras_sem) > 0:
    tabela_sem = vendedoras_sem[['vendedora', 'loja']].copy()
    tabela_sem.columns = ['Vendedora', 'Loja']
    st.error(f"⚠️ {len(tabela_sem)} vendedoras estão sem avaliação")
    st.dataframe(tabela_sem.sort_values(['Loja', 'Vendedora']), width='stretch', hide_index=True)
else:
    st.success("✅ Todas as vendedoras possuem avaliação.")

st.markdown("---")

# ======================================================
# 8. TODAS AS AVALIAÇÕES
# ======================================================

st.markdown("## 6️⃣  Todas as Avaliações")

colunas = ['nome_cliente', 'loja', 'tipo', 'estrela_1_5', 'bem_atendimento', 'recomendacao_1_10', 'createdat']
colunas_existentes = [c for c in colunas if c in aval_loja_completa.columns]
tabela_detalhes = aval_loja_completa[colunas_existentes].copy()

st.dataframe(tabela_detalhes, width='stretch', hide_index=True)
st.markdown("---")

# ======================================================
# 9. EXPORTAR
# ======================================================

st.markdown("## 💾 Exportar Dados")

c1, c2, c3 = st.columns(3)

with c1:
    st.download_button("📥 Ranking Vendedoras", ranking_vend.to_csv(index=False, encoding='utf-8-sig'), "ranking_vendedoras.csv", "text/csv")

with c2:
    st.download_button("📥 Ranking Lojas", ranking_loja.to_csv(index=False, encoding='utf-8-sig'), "ranking_lojas.csv", "text/csv")

with c3:
    st.download_button("📥 Todas Avaliações", tabela_detalhes.to_csv(index=False, encoding='utf-8-sig'), "todas_avaliacoes.csv", "text/csv")

st.markdown("---")
st.markdown("<p style='text-align:center;color:#6666aa;font-size:0.95rem;'>Dashboard de Avaliações · Atualize a página para recarregar</p>", unsafe_allow_html=True)