from IPython.display import Image, display

def save_graph(graph, path):
    img = graph.get_graph(xray=True).draw_mermaid_png()

    with open(path, "wb") as f:
        f.write(img)

def visualize_graph(graph):
    img = graph.get_graph(xray=True).draw_mermaid_png()
    display(Image(img))