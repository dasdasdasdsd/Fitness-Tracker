import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

def render_weight(df_weight):
    st.subheader("⚖️ Andamento Peso")

    # Inizializza session state per il mese
    if 'selected_month' not in st.session_state:
        st.session_state.selected_month = datetime.now().replace(day=1)

    # Navigazione mese pulita
    col_prev, col_month, col_next = st.columns([0.5, 3, 0.5])

    with col_prev:
        if st.button("◀", key="prev_month"):
            st.session_state.selected_month = (st.session_state.selected_month - pd.DateOffset(months=1)).replace(day=1)
            st.rerun()

    with col_month:
        mese_display = st.session_state.selected_month.strftime('%B %Y')
        st.markdown(f"<h4 style='text-align: center; margin: 0;'>{mese_display}</h4>", unsafe_allow_html=True)

    with col_next:
        if st.button("▶", key="next_month"):
            st.session_state.selected_month = (st.session_state.selected_month + pd.DateOffset(months=1)).replace(day=1)
            st.rerun()

    st.markdown("---")

    # Carica e filtra dati per il mese selezionato
    if not df_weight.empty:
        if 'Date' in df_weight.columns and 'Weight' in df_weight.columns:
            date_col = 'Date'
            weight_col = 'Weight'

            df_weight[date_col] = pd.to_datetime(df_weight[date_col])
            df_weight = df_weight.sort_values(date_col)




            # Filtra per mese selezionato
# Converti a Timestamp e normalizza solo quando filtri
            selected_month = pd.Timestamp(st.session_state.selected_month.replace(hour=0, minute=0, second=0, microsecond=0))
            next_month = selected_month + pd.DateOffset(months=1)
            df_filtered = df_weight[(df_weight[date_col] >= selected_month) & 
                                    (df_weight[date_col] < next_month)]



            # Range asse X: tutto il mese
            primo_giorno = selected_month
            if selected_month.month == 12:
                ultimo_giorno = selected_month.replace(year=selected_month.year+1, month=1, day=1)
            else:
                ultimo_giorno = selected_month.replace(month=selected_month.month+1, day=1)

            # Padding visivo: mezzogiorno del primo e ultimo giorno
            range_start = primo_giorno - pd.Timedelta(hours=12)
            range_end = ultimo_giorno - pd.Timedelta(hours=1)


            # Crea il grafico
            fig = go.Figure()

            if not df_filtered.empty:
                n_layers = 20
                start_rgb = [255, 179, 128]
                end_rgb = [255, 69, 0]

                for i in range(n_layers):
                    ratio = i / n_layers
                    r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * ratio)
                    g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * ratio)
                    b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * ratio)
                    color = f'rgb({r},{g},{b})'

                    layer_height = df_filtered[weight_col] * (1 - i/n_layers)

                    fig.add_trace(go.Bar(
                        x=df_filtered[date_col],
                        y=layer_height,
                        marker=dict(color=color, line_width=0),
                        showlegend=False,
                        hoverinfo='skip',
                        width=2*24*60*60*400
                    ))

                # Label sopra
                fig.add_trace(go.Scatter(
                    x=df_filtered[date_col],
                    y=df_filtered[weight_col],
                    mode='text',
                    text=df_filtered[weight_col].apply(lambda x: f"{x:.1f}"),
                    textposition='top center',
                    textfont=dict(size=10, color='#FF6B35'),
                    showlegend=False,
                    hoverinfo='skip'
                ))

            # Layout
            fig.update_layout(
                title="",
                xaxis_title="",
                yaxis_title="",
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                hovermode='x',
                margin=dict(t=40, b=40, l=40, r=40),
                barmode='overlay'
            )

            fig.update_xaxes(
                showgrid=False,
                showline=False,
                showticklabels=True,
                color='gray',
                tickformat='%d',
                dtick=86400000,
                tickangle=0,
                range=[range_start, range_end]
            )

            max_weight = df_weight[weight_col].max()
            fig.update_yaxes(
                showgrid=False,
                showline=False,
                showticklabels=False,
                range=[0, max_weight+5]
            )

            st.plotly_chart(fig, use_container_width=True)

            # Statistiche
            df_stats = df_filtered if not df_filtered.empty else df_weight

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Weight Attuale", f"{df_stats[weight_col].iloc[-1]:.1f} kg")
            with col2:
                weight_iniziale = df_stats[weight_col].iloc[0]
                variazione = df_stats[weight_col].iloc[-1] - weight_iniziale
                st.metric("Weight Iniziale", f"{weight_iniziale:.1f} kg", f"{variazione:+.1f} kg")
            with col3:
                st.metric("Weight Max", f"{df_stats[weight_col].max():.1f} kg")
            with col4:
                st.metric("Weight Min", f"{df_stats[weight_col].min():.1f} kg")
        else:
            st.warning("⚠️ Colonne 'Date' e 'Weight' non trovate nel sheet")
    else:
        st.warning("⚠️ Nessun dato Weight disponibile")

    st.markdown("---")

    if not df_weight.empty:
        st.dataframe(df_weight, use_container_width=True)
    else:
        st.warning("⚠️ Nessun dato disponibile")
