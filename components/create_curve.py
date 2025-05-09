import streamlit as st
import plotly.graph_objects as go

dev_color = '#7FE592'
prod_color = 'coral'

def show_graph(both_selected, curve_data, curve_data_dev: None, dev_or_prod):
    fig = go.Figure()

    if both_selected:
        fig_curve = go.Scatter(
            x=curve_data['points'].index,
            y=curve_data['points']['value'],
            mode='lines',
            name='Production',
            line=dict(color=prod_color)
        )
        fig_dev = go.Scatter(
            x=curve_data_dev['points'].index,
            y=curve_data_dev['points']['value'],
            mode='lines',
            name='Development',
            line=dict(color=dev_color, dash='dash', width=2)
        )
        fig.add_trace(fig_curve)
        fig.add_trace(fig_dev)
    else:
        if dev_or_prod == 'Development':
            line = dev_color
        else: line = prod_color
        fig_curve = go.Scatter(
            x=curve_data['points'].index,
            y=curve_data['points']['value'],
            mode='lines',
            name=f'{dev_or_prod}',
            line=dict(color=line)
        )
        fig.add_trace(fig_curve)

    fig.update_layout(
        xaxis=dict(
            showline=True
        ),
        yaxis=dict(
            showline=True
        ),
        xaxis_title="Date & Time",
        yaxis_title="Datapoints",
    )

    st.plotly_chart(fig, use_container_width=True,
                    key=curve_data['name'])
