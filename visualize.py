"""Script de visualisation du graphe de session."""
import json
import sys
from pathlib import Path


def visualize_graph_json(graph_file: str = "./workspace/graph.json"):
    """Affiche le graphe au format texte."""
    graph_path = Path(graph_file)
    
    if not graph_path.exists():
        print(f"❌ Fichier de graphe introuvable: {graph_file}")
        print("💡 Exécutez d'abord le système pour générer un graphe.")
        return
    
    with open(graph_path, "r", encoding="utf-8") as f:
        graph = json.load(f)
    
    print("=" * 60)
    print("📊 GRAPHE DE SESSION")
    print("=" * 60)
    print(f"Session ID: {graph.get('session_id', 'N/A')}\n")
    
    # Afficher les nœuds
    print("🔵 NŒUDS:")
    for node in graph.get("nodes", []):
        node_type = node.get("type", "unknown")
        label = node.get("label", node.get("id", "Unknown"))
        print(f"  • {node['id']}: {label} [{node_type}]")
    
    print()
    
    # Afficher les arêtes
    print("🔗 ARÊTES:")
    for edge in graph.get("edges", []):
        source = edge.get("source", "?")
        target = edge.get("target", "?")
        label = edge.get("label", "")
        print(f"  {source} --[{label}]--> {target}")
    
    print("=" * 60)
    
    # Statistiques
    print(f"\n📈 Statistiques:")
    print(f"  • Nombre de nœuds: {len(graph.get('nodes', []))}")
    print(f"  • Nombre d'arêtes: {len(graph.get('edges', []))}")
    
    # Détecter les cycles (simplifié)
    edges = graph.get("edges", [])
    if edges:
        print(f"\n🔄 Profondeur maximale détectée: {_calculate_max_depth(graph)}")
    
    print("=" * 60)


def _calculate_max_depth(graph: dict) -> int:
    """Calcule la profondeur maximale du graphe."""
    edges = graph.get("edges", [])
    nodes = {node["id"]: node for node in graph.get("nodes", [])}
    
    # Trouver la racine (nœud sans arête entrante)
    targets = {edge["target"] for edge in edges}
    roots = [node_id for node_id in nodes.keys() if node_id not in targets]
    
    if not roots:
        return 0
    
    def dfs(node_id: str, visited: set, depth: int) -> int:
        if node_id in visited:
            return depth
        visited.add(node_id)
        
        max_child_depth = depth
        for edge in edges:
            if edge["source"] == node_id:
                child_depth = dfs(edge["target"], visited.copy(), depth + 1)
                max_child_depth = max(max_child_depth, child_depth)
        
        return max_child_depth
    
    max_depth = 0
    for root in roots:
        depth = dfs(root, set(), 0)
        max_depth = max(max_depth, depth)
    
    return max_depth


def generate_html_visualization(graph_file: str = "./workspace/graph.json", output_file: str = "./workspace/graph.html"):
    """Génère une visualisation HTML interactive du graphe."""
    graph_path = Path(graph_file)
    
    if not graph_path.exists():
        print(f"❌ Fichier de graphe introuvable: {graph_file}")
        return
    
    with open(graph_path, "r", encoding="utf-8") as f:
        graph = json.load(f)
    
    html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SYNERGOS-MCP - Graphe de Session</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            margin-bottom: 10px;
        }}
        .info {{
            color: #666;
            margin-bottom: 20px;
        }}
        svg {{
            border: 1px solid #ddd;
            border-radius: 4px;
        }}
        .node {{
            cursor: pointer;
        }}
        .node circle {{
            fill: #4A90E2;
            stroke: #2E5C8A;
            stroke-width: 2px;
        }}
        .node.manager circle {{
            fill: #E94B3C;
        }}
        .node.worker circle {{
            fill: #50C878;
        }}
        .node.input circle {{
            fill: #9B59B6;
        }}
        .link {{
            fill: none;
            stroke: #999;
            stroke-width: 2px;
        }}
        .link-label {{
            font-size: 12px;
            fill: #666;
        }}
        .node-label {{
            font-size: 12px;
            font-weight: bold;
            fill: #333;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 SYNERGOS-MCP - Graphe de Session</h1>
        <div class="info">
            <strong>Session ID:</strong> {graph.get('session_id', 'N/A')}<br>
            <strong>Nœuds:</strong> {len(graph.get('nodes', []))} | 
            <strong>Arêtes:</strong> {len(graph.get('edges', []))}
        </div>
        <svg id="graph"></svg>
    </div>
    
    <script>
        const graphData = {json.dumps(graph, ensure_ascii=False)};
        
        const width = 1200;
        const height = 800;
        
        const svg = d3.select("#graph")
            .attr("width", width)
            .attr("height", height);
        
        const simulation = d3.forceSimulation(graphData.nodes)
            .force("link", d3.forceLink(graphData.edges).id(d => d.id).distance(150))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collision", d3.forceCollide().radius(50));
        
        const link = svg.append("g")
            .selectAll("line")
            .data(graphData.edges)
            .enter().append("line")
            .attr("class", "link");
        
        const linkLabels = svg.append("g")
            .selectAll("text")
            .data(graphData.edges)
            .enter().append("text")
            .attr("class", "link-label")
            .text(d => d.label || "");
        
        const node = svg.append("g")
            .selectAll("g")
            .data(graphData.nodes)
            .enter().append("g")
            .attr("class", d => `node ${{d.type}}`)
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));
        
        node.append("circle")
            .attr("r", 20);
        
        node.append("text")
            .attr("class", "node-label")
            .attr("dy", 35)
            .text(d => d.label || d.id);
        
        simulation.on("tick", () => {{
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);
            
            linkLabels
                .attr("x", d => (d.source.x + d.target.x) / 2)
                .attr("y", d => (d.source.y + d.target.y) / 2);
            
            node
                .attr("transform", d => `translate(${{d.x}},${{d.y}})`);
        }});
        
        function dragstarted(event) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            event.subject.fx = event.subject.x;
            event.subject.fy = event.subject.y;
        }}
        
        function dragged(event) {{
            event.subject.fx = event.x;
            event.subject.fy = event.y;
        }}
        
        function dragended(event) {{
            if (!event.active) simulation.alphaTarget(0);
            event.subject.fx = null;
            event.subject.fy = null;
        }}
    </script>
</body>
</html>
"""
    
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"✅ Visualisation HTML générée: {output_file}")
    print(f"💡 Ouvrez le fichier dans votre navigateur pour voir le graphe interactif.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--html":
        graph_file = sys.argv[2] if len(sys.argv) > 2 else "./workspace/graph.json"
        output_file = sys.argv[3] if len(sys.argv) > 3 else "./workspace/graph.html"
        generate_html_visualization(graph_file, output_file)
    else:
        graph_file = sys.argv[1] if len(sys.argv) > 1 else "./workspace/graph.json"
        visualize_graph_json(graph_file)
