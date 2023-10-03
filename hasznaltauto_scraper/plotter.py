
import re

import pandas as pd
import plotly.graph_objs as go
from plotly.offline import plot


class PredictedPricePlot():

    def __call__(self, predicted_df: pd.DataFrame):
        plot_html_str = self.create_plot(predicted_df)

        return plot_html_str


    def create_plot(self, df):

        data = [
            go.Scatter(
                x=df["price"],
                y=df['predicted_price'],
                mode='markers',
                name='',
                text=df["title"],
                customdata=df["link"],
                marker=dict(
                    color=df["age"],
                    colorscale = "plotly3_r",
                    colorbar=dict(
                        title="Autó életkora <br> (év)",
                        # orientation='h'
                        # colorscale = "viridis_r"
                    ),
                    showscale=True,
                    size=df["mileage_km"],
                    sizeref=2.*max(df["mileage_km"])/(50.**1),
                    sizemin=4,
                ),
                hovertemplate =
                    'Hirdetés címe: %{text}<br>'+
                    'Becsült ár: %{y:.3s} Ft <br>'+
                    'Valós ár: %{x:.3s} Ft <br>' + 
                    'Autó életkora: %{marker.color:.1f} years <br>' +
                    'Kilométeróra: %{marker.size:,.0f} km'
                
            ),
        ]

        line_trace = go.Scatter(
            x=[min(df["price"]), max(df["price"])],
            y=[min(df["price"]), max(df["price"])],
            mode='lines',
            name='x=y'
        )

        data.append(line_trace)

        # Build layout
        layout = go.Layout(
            hovermode='closest',
            showlegend=False,
            xaxis=dict(title="Valós ár", tickfont=dict(size=14)),
            yaxis=dict(title="Becsült ár", tickfont=dict(size=14)),
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=16),
            margin={"l": 50,
                    "r": 50,
                    "b": 50,
                    "t": 20,
                    "pad": 4}
        )

        # Build Figure
        fig = go.Figure(
            data=data,
            layout=layout,
        )

        # Get HTML representation of plotly.js and this figure
        plot_div = plot(fig, output_type='div', include_plotlyjs=True, config={'displayModeBar': False})

        # Get id of html div element that looks like
        # <div id="301d22ab-bfba-4621-8f5d-dc4fd855bb33" ... >
        res = re.search('<div id="([^"]*)"', plot_div)
        div_id = res.groups()[0]

        # Build JavaScript callback for handling clicks
        # and opening the URL in the trace's customdata 
        js_callback = """
        <script>
        var plot_element = document.getElementById("{div_id}");
        plot_element.on('plotly_click', function(data){{
            console.log(data);
            var point = data.points[0];
            if (point) {{
                console.log(point.customdata);
                window.open(point.customdata);
            }}
        }})
        </script>
        """.format(div_id=div_id)

        # Build HTML string
        plot_html_str = """
        {plot_div}
        {js_callback}
        """.format(plot_div=plot_div, js_callback=js_callback)

        return plot_html_str