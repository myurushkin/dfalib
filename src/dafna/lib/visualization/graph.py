import networkx as nx
import plotly.graph_objects as go


def create_graph(nucleotide_string, picture):
    G = nx.Graph()
    G.add_edges_from(picture)
    
    nucleotide_string = nucleotide_string.upper()
    mapping = {i: {"nucleotide": nucleotide_string[i], "index": i} for i in range(len(nucleotide_string))}
    nx.set_node_attributes(G, mapping, "nucleotide")
    
    return G
    

def show_graph(G):
    n = G.number_of_nodes()
    print(G.edges())

    mapping = nx.get_node_attributes(G, "nucleotide")
    nucleotide_colors = {"A": "red", "C": "green", "G": "blue", "T": "orange"}


    # Use spring layout to position nodes
    pos = nx.spring_layout(G, dim=3)

    # Create position lists
    # Xn=[pos[k][0] for k in pos]
    # Yn=[pos[k][1] for k in pos]
    # Zn=[pos[k][2] for k in pos]
    Xn=[pos[k][0] for k in range(n)]
    Yn=[pos[k][1] for k in range(n)]
    Zn=[pos[k][2] for k in range(n)]

    Xe=[]
    Ye=[]
    Ze=[]
    for e in G.edges():
        Xe+=[pos[e[0]][0],pos[e[1]][0], None]# x-coordinates of edge ends
        Ye+=[pos[e[0]][1],pos[e[1]][1], None]
        Ze+=[pos[e[0]][2],pos[e[1]][2], None]

    # Create a trace for the edges
    trace_edges=go.Scatter3d(x=Xe,
                y=Ye,
                z=Ze,
                mode='lines',
                line=dict(color='rgb(125,125,125)', width=1),
                hoverinfo='none')

    # Create a trace for the nodes
    # trace_nodes=go.Scatter3d(x=Xn,
    #                y=Yn,
    #                z=Zn,
    #                mode='markers',
    #                name='nucleotide',
    #                marker=dict(symbol='circle',
    #                              size=6,
    #                              color='rgb(255, 0,0)',
    #                              colorscale='Viridis',
    #                              line=dict(color='rgb(50,50,50)', width=0.5)),
    #                text=[mapping[i] for i in range(n)],
    #                hoverinfo='text')

    unique_nucleotides = set(list(map(lambda x: x['nucleotide'], mapping.values())))

    trace_nodes = []
    for nucleotide in unique_nucleotides:
        indices = [i for i, n in mapping.items() if n['nucleotide'] == nucleotide]
        Xn_nucleotide = [Xn[i] for i in indices]
        Yn_nucleotide = [Yn[i] for i in indices]
        Zn_nucleotide = [Zn[i] for i in indices]

        node_trace = go.Scatter3d(
            x=Xn_nucleotide,
            y=Yn_nucleotide,
            z=Zn_nucleotide,
            mode="markers",
            name=nucleotide,
            marker=dict(
                symbol="circle",
                size=6,
                color=nucleotide_colors[nucleotide],
                line=dict(color="rgb(50,50,50)", width=0.5),
            ),
            text=[f"Nucleotide: {nucleotide} {i}" for i in indices],
            hoverinfo="text",
        )
        trace_nodes.append(node_trace)

    axis=dict(showbackground=False,
            showline=False,
            zeroline=False,
            showgrid=False,
            showticklabels=False,
            title=''
            )

    layout = go.Layout(
            title="3D visualization of a complete graph with {} nodes".format(n),
            width=1000,
            height=1000,
            showlegend=False,
            scene=dict(
                xaxis=dict(axis),
                yaxis=dict(axis),
                zaxis=dict(axis),
            ),
        margin=dict(
            t=100
        ),
        hovermode='closest',
        annotations=[
            dict(
            showarrow=False,
                text="",
                xref='paper',
                yref='paper',
                x=0,
                y=0.1,
                xanchor='left',
                yanchor='bottom',
                font=dict(
                size=14
                )
                )
            ],)

    data=[trace_edges] + trace_nodes
    fig=go.Figure(data=data, layout=layout)

    fig.update_layout(
        title="3D visualization of a complete graph with {} nodes".format(n),
        width=1860,
        height=1080,
        showlegend=True,
        scene=dict(
            xaxis=dict(showbackground=False, showline=False, zeroline=False, showgrid=False),
            yaxis=dict(showbackground=False, showline=False, zeroline=False, showgrid=False),
            zaxis=dict(showbackground=False, showline=False, zeroline=False, showgrid=False),
            camera=dict(
                eye=dict(x=0, y=0, z=0.1),  # Adjust the z-value for zooming in or out
                center=dict(x=0, y=0, z=0),
            ),
        ),
        hovermode="closest",
        margin=dict(t=100),
    )


    fig.show()