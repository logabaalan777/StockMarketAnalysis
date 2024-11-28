import plotly.express as px

def create_interactive_chart(data, x_column, y_column, title):
    fig = px.line(data, x=x_column, y=y_column, title=title, labels={x_column: "Date", y_column: y_column})
    fig.update_traces(hoverinfo="x+y", mode="lines+markers")
    fig.update_layout(hovermode="x unified")
    return fig.show()
