"use client";
import React, { useRef, useState, useEffect } from "react";
import dynamic from "next/dynamic";
import { GraphData, GraphNode, GraphLink, Embeddings } from "@/lib/utils/types";

const ForceGraph2D = dynamic(() => import("@/lib/utils/NoSSRForceGraph"), { ssr: false });

interface GraphProps {
    embeddings: Embeddings[];
}

// ✅ Convert embeddings to graph format
const generateGraphData = (embeddings: Embeddings[]): GraphData => {
    const nodesMap = new Map<string, GraphNode>();
    const links: GraphLink[] = [];

    embeddings.forEach(({ word, embedding, pmi }) => {
        // ✅ Ensure both source and target nodes exist in nodesMap
        if (!nodesMap.has(word)) {
            nodesMap.set(word, { id: word, label: word, isParent: true });
        }
        if (!nodesMap.has(embedding)) {
            nodesMap.set(embedding, { id: embedding, label: embedding, isParent: false });
        }

        // ✅ Retrieve the actual GraphNode objects
        const sourceNode = nodesMap.get(word) as GraphNode;
        const targetNode = nodesMap.get(embedding) as GraphNode;

        // ✅ Push the correct GraphLink structure
        links.push({ source: sourceNode, target: targetNode, weight: pmi });
    });

    return { nodes: Array.from(nodesMap.values()), links };
};


const Graph = ({ embeddings }: GraphProps) => {
    const fgRef = useRef<any>(null);
    const [graphData, setGraphData] = useState<GraphData>(generateGraphData(embeddings));

    return (
        <div className="w-full h-screen flex flex-col">
            {/* Graph Visualization */}
            <ForceGraph2D
                ref={fgRef}
                graphData={graphData}
                nodeRelSize={5}
                nodeAutoColorBy="group"
                linkDirectionalArrowLength={5}
                nodeCanvasObject={(node, ctx, globalScale) => {
                    const fontSize = Math.max(10 / globalScale, 3);
                    ctx.font = `${fontSize}px Sans-Serif`;
                    ctx.textAlign = "center";
                    ctx.textBaseline = "middle";

                    const graphNode = node as GraphNode;
                    const label = graphNode.label ?? graphNode.id ?? "Unknown";

                    // ✅ Draw node circle
                    ctx.fillStyle = graphNode.isParent ? "#ff5733" : "#3498db";
                    ctx.beginPath();
                    ctx.arc(node.x ?? 0, node.y ?? 0, 10, 0, 2 * Math.PI, false);
                    ctx.fill();

                    // ✅ Draw centered text
                    ctx.fillStyle = "#ffffff";
                    ctx.fillText(label, node.x ?? 0, node.y ?? 0);
                }}
            />
        </div>
    );
};

export default Graph;
