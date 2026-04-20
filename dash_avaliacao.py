import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Dashboard de Avaliações", layout="wide")

# ======================================================
# CARREGAMENTO DOS DADOS
# ======================================================

@st.cache_data
def load_data():
    """Carrega os arquivos Excel"""
    paths = [
        ('arquivos_15_04_26/', 'Pasta arquivos'),
        ('', 'Raiz do repositório'),
    ]
    
    for path_prefix, desc in paths:
        try:
            avaliacoes = pd.read_excel(f'{path_prefix}avaliacoes.xlsx')
            vendedoras = pd.read_excel(f'{path_prefix}vendedoras.xlsx')
            lojas = pd.read_excel(f'{path_prefix}lojas.xlsx')
            supervisores = pd.read_excel(f'{path_prefix}supervisores.xlsx')
            supervisores_lojas = pd.read_excel(f'{path_prefix}supervisores_lojas.xlsx')
            return avaliacoes, vendedoras, lojas, supervisores, supervisores_lojas
        except (FileNotFoundError, Exception):
            continue
    
    raise FileNotFoundError("❌ Arquivos Excel não encontrados em nenhum caminho!")

try:
    avaliacoes, vendedoras, lojas, supervisores, supervisores_lojas = load_data()
except FileNotFoundError as e:
    st.error(str(e))
    st.stop()

# ======================================================
# PROCESSAMENTO
# ======================================================

# Normaliza nomes de colunas
avaliacoes.columns = avaliacoes.columns.str.lower().str.strip()
vendedoras.columns = vendedoras.columns.str.lower().str.strip()
lojas.columns = lojas.columns.str.lower().str.strip()
supervisores.columns = supervisores.columns.str.lower().str.strip()

# Converte tipos de dados
avaliacoes['estrela_1_5'] = pd.to_numeric(avaliacoes['estrela_1_5'], errors='coerce')
avaliacoes['recomendacao_1_10'] = pd.to_numeric(avaliacoes['recomendacao_1_10'], errors='coerce')

# Separa avaliações por tipo
aval_vendedoras = avaliacoes[avaliacoes['tipo'] == 'vendedora'].copy()
aval_supervisores = avaliacoes[avaliacoes['tipo'] == 'supervisor'].copy()

# ======================================================
# DASHBOARD
# ======================================================

st.title("⭐ Dashboard de Avaliações de Atendimento")
st.markdown("Análise Completa de Vendedoras, Supervisores e Lojas")
st.markdown("---")

# ======================================================
# 1. OVERVIEW GERAL
# ======================================================

st.subheader("📊 Visão Geral da Empresa")

col1, col2, col3, col4, col5 = st.columns(5)

total_aval = len(avaliacoes)
media_estrela = avaliacoes['estrela_1_5'].mean()
media_recomendacao = avaliacoes['recomendacao_1_10'].mean()
bem_atendimento_sim = (avaliacoes['bem_atendimento'] == 'sim').sum() / len(avaliacoes) * 100
total_vendedoras = len(vendedoras)

col1.metric("📈 Total de Avaliações", total_aval)
col2.metric("⭐ Média de Estrelas", f"{media_estrela:.2f}/5.0")
col3.metric("👍 Média de Recomendação", f"{media_recomendacao:.2f}/10")
col4.metric("😊 Bem Atendidas", f"{bem_atendimento_sim:.1f}%")
col5.metric("👥 Total Vendedoras", total_vendedoras)

st.markdown("---")

# ======================================================
# 2. DISTRIBUIÇÃO DE ESTRELAS (Pizza)
# ======================================================

col_pizza1, col_pizza2 = st.columns(2)

with col_pizza1:
    st.subheader("1️⃣ Distribuição de Estrelas (Empresa)")
    dist_estrelas = avaliacoes['estrela_1_5'].value_counts().sort_index()
    
    fig_pizza_estrela = go.Figure(data=[go.Pie(
        labels=[f"{'⭐'*int(i)} {int(i)} Estrela(s)" for i in dist_estrelas.index],
        values=dist_estrelas.values,
        marker=dict(colors=['#d73027', '#fc8d59', '#fee090', '#91bfdb', '#4575b4']),
        hovertemplate='<b>%{label}</b><br>Quantidade: %{value}<br>%{percent}<extra></extra>'
    )])
    
    fig_pizza_estrela.update_layout(height=400, template='plotly_dark')
    st.plotly_chart(fig_pizza_estrela, use_container_width=True)

with col_pizza2:
    st.subheader("2️⃣ Bem Atendimento (Empresa)")
    dist_atendimento = avaliacoes['bem_atendimento'].value_counts()
    cores_atendimento = {'sim': '#4575b4', 'parcialmente': '#fee090', 'nao': '#d73027'}
    
    fig_pizza_atend = go.Figure(data=[go.Pie(
        labels=dist_atendimento.index,
        values=dist_atendimento.values,
        marker=dict(colors=[cores_atendimento.get(x, '#gray') for x in dist_atendimento.index]),
        hovertemplate='<b>%{label}</b><br>Quantidade: %{value}<br>%{percent}<extra></extra>'
    )])
    
    fig_pizza_atend.update_layout(height=400, template='plotly_dark')
    st.plotly_chart(fig_pizza_atend, use_container_width=True)

st.markdown("---")

# ======================================================
# 3. RANKING DE VENDEDORAS
# ======================================================

st.subheader("3️⃣ Ranking de Vendedoras")

# Merge para pegar nomes das vendedoras
aval_vend_completa = aval_vendedoras.merge(
    vendedoras[['id', 'vendedora']], 
    left_on='vendedora_id', 
    right_on='id', 
    how='left'
)

# Agrupa por vendedora
ranking_vend = aval_vend_completa.groupby('vendedora').agg({
    'estrela_1_5': ['mean', 'count'],
    'recomendacao_1_10': 'mean',
    'bem_atendimento': lambda x: (x == 'sim').sum() / len(x) * 100
}).reset_index()

ranking_vend.columns = ['Vendedora', 'Média Estrelas', 'Total Avaliações', 'Média Recomendação', '% Bem Atendimento']
ranking_vend = ranking_vend.sort_values('Média Estrelas', ascending=False)

# Gráfico de barras
fig_ranking_vend = go.Figure(data=[
    go.Bar(
        y=ranking_vend['Vendedora'].head(15),
        x=ranking_vend['Média Estrelas'].head(15),
        orientation='h',
        marker=dict(
            color=ranking_vend['Média Estrelas'].head(15),
            colorscale='RdYlGn',
            cmin=1,
            cmax=5,
            colorbar=dict(title="Média")
        ),
        text=ranking_vend['Média Estrelas'].head(15).round(2),
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Média: %{x:.2f}<br>Avaliações: %{customdata[0]}<br>Recomendação: %{customdata[1]:.2f}<extra></extra>',
        customdata=ranking_vend[['Total Avaliações', 'Média Recomendação']].head(15).values
    )
])

fig_ranking_vend.update_layout(
    title='Top 15 Vendedoras por Média de Estrelas',
    xaxis_title='Média de Estrelas',
    yaxis_title='Vendedora',
    height=500,
    xaxis_range=[0, 5.1],
    template='plotly_dark'
)

st.plotly_chart(fig_ranking_vend, use_container_width=True)

st.markdown("---")

# ======================================================
# 4. DETALHES INDIVIDUAIS DE VENDEDORAS
# ======================================================

st.subheader("4️⃣ Avaliações Individuais de Vendedoras")

vendedora_selecionada = st.selectbox(
    "Selecione uma vendedora:",
    sorted(ranking_vend['Vendedora'].unique())
)

aval_vendedora_sel = aval_vend_completa[aval_vend_completa['vendedora'] == vendedora_selecionada]

if len(aval_vendedora_sel) > 0:
    col_ind1, col_ind2, col_ind3, col_ind4 = st.columns(4)
    
    with col_ind1:
        st.metric("⭐ Média Estrelas", f"{aval_vendedora_sel['estrela_1_5'].mean():.2f}/5.0")
    
    with col_ind2:
        st.metric("👍 Média Recomendação", f"{aval_vendedora_sel['recomendacao_1_10'].mean():.2f}/10")
    
    with col_ind3:
        bem_atend_pct = (aval_vendedora_sel['bem_atendimento'] == 'sim').sum() / len(aval_vendedora_sel) * 100
        st.metric("😊 % Bem Atendimento", f"{bem_atend_pct:.1f}%")
    
    with col_ind4:
        st.metric("📝 Total Avaliações", len(aval_vendedora_sel))
    
    # Distribuição de estrelas dessa vendedora
    col_dist1, col_dist2 = st.columns(2)
    
    with col_dist1:
        dist_est_vend = aval_vendedora_sel['estrela_1_5'].value_counts().sort_index()
        fig_dist_vend = go.Figure(data=[go.Bar(
            x=[f"{'⭐'*int(i)} {int(i)}" for i in dist_est_vend.index],
            y=dist_est_vend.values,
            marker_color=['#d73027', '#fc8d59', '#fee090', '#91bfdb', '#4575b4'][:len(dist_est_vend)],
            text=dist_est_vend.values,
            textposition='outside'
        )])
        fig_dist_vend.update_layout(title=f"Distribuição de Estrelas - {vendedora_selecionada}", height=400, template='plotly_dark')
        st.plotly_chart(fig_dist_vend, use_container_width=True)
    
    with col_dist2:
        dist_atend_vend = aval_vendedora_sel['bem_atendimento'].value_counts()
        fig_atend_vend = go.Figure(data=[go.Pie(
            labels=dist_atend_vend.index,
            values=dist_atend_vend.values,
            marker=dict(colors=[cores_atendimento.get(x, '#gray') for x in dist_atend_vend.index])
        )])
        fig_atend_vend.update_layout(title=f"Bem Atendimento - {vendedora_selecionada}", height=400, template='plotly_dark')
        st.plotly_chart(fig_atend_vend, use_container_width=True)
    
    # Comentários da vendedora
    st.write(f"**Comentários recebidos por {vendedora_selecionada}:**")
    comentarios = aval_vendedora_sel[aval_vendedora_sel['comentario_cliente'].notna()]
    if len(comentarios) > 0:
        st.markdown("---")
        for idx, row in comentarios.iterrows():
            st.write(f"⭐ {int(row['estrela_1_5'])} estrelas - {row['comentario_cliente']}")
            st.markdown("---")
    else:
        st.info("Nenhum comentário registrado")

st.markdown("---")

# ======================================================
# 5. RANKING DE SUPERVISORES
# ======================================================

st.subheader("5️⃣ Ranking de Supervisores")

if len(aval_supervisores) > 0:
    aval_sup_completa = aval_supervisores.merge(
        supervisores[['id', 'nome_supervisor']], 
        left_on='supervisor_id', 
        right_on='id', 
        how='left'
    )
    
    ranking_sup = aval_sup_completa.groupby('nome_supervisor').agg({
        'estrela_1_5': ['mean', 'count'],
        'recomendacao_1_10': 'mean',
        'bem_atendimento': lambda x: (x == 'sim').sum() / len(x) * 100
    }).reset_index()
    
    ranking_sup.columns = ['Supervisor', 'Média Estrelas', 'Total Avaliações', 'Média Recomendação', '% Bem Atendimento']
    ranking_sup = ranking_sup.sort_values('Média Estrelas', ascending=False)
    
    fig_ranking_sup = go.Figure(data=[
        go.Bar(
            y=ranking_sup['Supervisor'],
            x=ranking_sup['Média Estrelas'],
            orientation='h',
            marker=dict(
                color=ranking_sup['Média Estrelas'],
                colorscale='RdYlGn',
                cmin=1,
                cmax=5,
                colorbar=dict(title="Média")
            ),
            text=ranking_sup['Média Estrelas'].round(2),
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Média: %{x:.2f}<extra></extra>'
        )
    ])
    
    fig_ranking_sup.update_layout(
        title='Ranking de Supervisores',
        xaxis_title='Média de Estrelas',
        yaxis_title='Supervisor',
        height=400,
        xaxis_range=[0, 5.1],
        template='plotly_dark'
    )
    
    st.plotly_chart(fig_ranking_sup, use_container_width=True)
else:
    st.info("Nenhuma avaliação de supervisor encontrada")

st.markdown("---")

# ======================================================
# 6. AVALIAÇÕES POR LOJA
# ======================================================

st.subheader("6️⃣ Avaliações por Loja")

aval_loja_completa = avaliacoes.merge(
    lojas[['id', 'loja']], 
    left_on='loja_id', 
    right_on='id', 
    how='left'
)

ranking_loja = aval_loja_completa.groupby('loja').agg({
    'estrela_1_5': ['mean', 'count'],
    'recomendacao_1_10': 'mean',
    'bem_atendimento': lambda x: (x == 'sim').sum() / len(x) * 100
}).reset_index()

ranking_loja.columns = ['Loja', 'Média Estrelas', 'Total Avaliações', 'Média Recomendação', '% Bem Atendimento']
ranking_loja = ranking_loja.sort_values('Média Estrelas', ascending=False)

fig_ranking_loja = go.Figure(data=[
    go.Bar(
        y=ranking_loja['Loja'].head(20),
        x=ranking_loja['Média Estrelas'].head(20),
        orientation='h',
        marker=dict(
            color=ranking_loja['Média Estrelas'].head(20),
            colorscale='RdYlGn',
            cmin=1,
            cmax=5
        ),
        text=ranking_loja['Média Estrelas'].head(20).round(2),
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Média: %{x:.2f}<br>Avaliações: %{customdata}<extra></extra>',
        customdata=ranking_loja['Total Avaliações'].head(20)
    )
])

fig_ranking_loja.update_layout(
    title='Top 20 Lojas por Média de Estrelas',
    xaxis_title='Média de Estrelas',
    yaxis_title='Loja',
    height=500,
    xaxis_range=[0, 5.1],
    template='plotly_dark'
)

st.plotly_chart(fig_ranking_loja, use_container_width=True)

st.markdown("---")

# ======================================================
# 7. TABELA DETALHADA
# ======================================================

st.subheader("7️⃣ Tabela Detalhada de Todas as Avaliações")

tabela_detalhes = aval_loja_completa[['nome_cliente', 'loja', 'tipo', 'estrela_1_5', 'bem_atendimento', 'recomendacao_1_10', 'createdat']].copy()
tabela_detalhes.columns = ['Cliente', 'Loja', 'Tipo', 'Estrelas', 'Bem Atendido', 'Recomendação', 'Data']
tabela_detalhes = tabela_detalhes.sort_values('Data', ascending=False)

st.dataframe(tabela_detalhes, use_container_width=True, hide_index=True)

st.markdown("---")

# ======================================================
# 8. EXPORTAR
# ======================================================

st.subheader("💾 Exportar Dados")

col_exp1, col_exp2, col_exp3 = st.columns(3)

with col_exp1:
    csv_vend = ranking_vend.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label="📥 Ranking Vendedoras",
        data=csv_vend,
        file_name="ranking_vendedoras.csv",
        mime="text/csv"
    )

with col_exp2:
    csv_loja = ranking_loja.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label="📥 Ranking Lojas",
        data=csv_loja,
        file_name="ranking_lojas.csv",
        mime="text/csv"
    )

with col_exp3:
    csv_all = tabela_detalhes.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label="📥 Todas as Avaliações",
        data=csv_all,
        file_name="todas_avaliacoes.csv",
        mime="text/csv"
    )

st.markdown("---")
st.caption("Dashboard de Avaliações - Atualizar página para recarregar dados")