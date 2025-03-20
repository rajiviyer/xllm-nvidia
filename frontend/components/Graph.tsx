import React, { useRef, useState, useEffect } from "react";
import dynamic from "next/dynamic";
import { GraphData, GraphNode, GraphLink, Embedding } from "@/lib/utils/types";

const ForceGraph2D = dynamic(
  () => import("@/lib/utils/NoSSRForceGraph"),
  { ssr: false, loading: () => <div>Loading Graph...</div> }
);

const getNodeColor = (node: GraphNode) => {
  if (node.isParent) {
    return "#ff5733";
  }
  const colors = ["#3498db", "#2ecc71", "#f1c40f", "#9b59b6", "#e74c3c", "#1abc9c"];
  const hash = node.id.split("").reduce((acc, char) => acc + char.charCodeAt(0), 0);
  return colors[hash % colors.length];
};

interface DocumentCard {
  id: string;
  rank: number;
  size: string;
  content: string;
}

interface GraphProps {
  embeddings: Embedding[];
}

const updateGraphData = (embeddings: Embedding[], sourceFilter: string, pmiThreshold: number): GraphData => {
  let filteredEmbeddings: Embedding[] = [];
  if (sourceFilter === "") {
    filteredEmbeddings = embeddings.filter(
      (embedding) => embedding.pmi >= pmiThreshold
    );
  } else {
    filteredEmbeddings = embeddings.filter(
      (embedding) => embedding.word === sourceFilter && embedding.pmi >= pmiThreshold
    );
  }
  return generateGraphData(filteredEmbeddings);
};

const generateGraphData = (embeddings: Embedding[]): GraphData => {
  const nodesMap = new Map<string, GraphNode>();
  const links: GraphLink[] = [];

  embeddings.forEach(({ word, embedding, pmi }) => {
    if (!nodesMap.has(word)) {
      nodesMap.set(word, { id: word, label: word, isParent: true });
    }
    if (!nodesMap.has(embedding)) {
      nodesMap.set(embedding, { id: embedding, label: embedding, isParent: false });
    }

    const sourceNode = nodesMap.get(word) as GraphNode;
    const targetNode = nodesMap.get(embedding) as GraphNode;

    links.push({ source: sourceNode, target: targetNode, weight: pmi });
  });

  return { nodes: Array.from(nodesMap.values()), links };
};

const Graph = ({ embeddings }: GraphProps) => {
  const fgRef = useRef<any>(null);
  const [graphData, setGraphData] = useState<GraphData>(updateGraphData(embeddings, "", 0.3));
  const [sourceFilter, setSourceFilter] = useState<string>("");
  const [pmiThreshold, setPmiThreshold] = useState<number>(0.2);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [documents, setDocuments] = useState<DocumentCard[]>([]);
  const [currentDocIndex, setCurrentDocIndex] = useState<number>(0);

  useEffect(() => {
    const updatedData = updateGraphData(embeddings, sourceFilter, pmiThreshold);
    setGraphData(updatedData);
  }, [embeddings, sourceFilter, pmiThreshold]);

  useEffect(() => {
    if (fgRef.current && graphData.links.length > 0 && typeof fgRef.current.d3Force === 'function') {
      const linkForce = fgRef.current.d3Force("link");
      if (linkForce) {
        linkForce.distance((link: any) => {
          const weight = link.weight ?? 0;
          const minDist = 50;
          const maxDist = 300;
          const normalizedWeight = Math.max(0, Math.min(1, weight));
          return maxDist - normalizedWeight * (maxDist - minDist);
        });
        fgRef.current.d3ReheatSimulation();
      }
    }
  }, [graphData]);

  const handleNodeClick = (node: any) => {
    const nodeId = node.id as string;
    const isLeafNode = !graphData.links.some(link => (link.source as GraphNode).id === nodeId);
    if (isLeafNode) {
      setSelectedNode({ id: nodeId, label: node.label ?? nodeId, isParent: node.isParent ?? false });
      // Simulate document retrieval
      const dummyDocs: DocumentCard[] = [
        { id: "1", rank: 1, size: "1.2MB", content: `Content for ${nodeId} doc 1` },
        { id: "2", rank: 2, size: "2.3MB", content: `Content for ${nodeId} doc 2` },
        { id: "3", rank: 3, size: "1.5MB", content: `Content for ${nodeId} doc 3` },
      ];
      setDocuments(dummyDocs);
      setCurrentDocIndex(0);
    }
  };

  return (
    <div className="w-full h-screen flex flex-col bg-white">
      <div className="mt-2 mb-4 space-y-2">
        <div className="text-sm">
          <label>Filter by Source: </label>
          <input
            type="text"
            className="text-black p-1 border-2 border-black"
            value={sourceFilter}
            onChange={(e) => setSourceFilter(e.target.value ?? "")}
          />
        </div>
        <div className="text-sm">
          <label>PMI Threshold: </label>
          <input
            type="number"
            className="text-black p-1 border-2 border-black"
            value={pmiThreshold}
            onChange={(e) => setPmiThreshold(Number(e.target.value) || 0)}
            step="0.01"
            min="0"
          />
        </div>
      </div>
      <ForceGraph2D
        ref={fgRef}
        graphData={graphData}
        nodeRelSize={5}
        nodeAutoColorBy="group"
        linkDirectionalArrowLength={5}
        onNodeClick={handleNodeClick}
        nodeCanvasObject={(node, ctx, globalScale) => {
          const fontSize = Math.max(10 / globalScale, 3);
          ctx.font = `${fontSize}px Sans-Serif`;
          ctx.textAlign = "center";
          ctx.textBaseline = "middle";

          const label = node.label ?? node.id ?? "Unknown";

          ctx.fillStyle = getNodeColor(node as GraphNode);
          ctx.beginPath();
          ctx.arc(node.x ?? 0, node.y ?? 0, 10, 0, 2 * Math.PI, false);
          ctx.fill();

          ctx.fillStyle = (node.isParent ? "#ff5733" : "#000");
          ctx.fillText(label, (node.x ?? 0) + 12, (node.y ?? 0) + 4);
        }}
        d3VelocityDecay={0.2}
        d3AlphaDecay={0.03}
        d3AlphaMin={0.001}
      />

      {selectedNode && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center">
          <div className="bg-white p-4 rounded shadow-md w-96 text-black">
            <h2 className="text-lg font-bold mb-2">Documents for {selectedNode.label}</h2>
            {documents.length > 0 && (
              <div className="border p-4 rounded shadow-sm">
                <p><strong>ID:</strong> {documents[currentDocIndex].id}</p>
                <p><strong>Rank:</strong> {documents[currentDocIndex].rank}</p>
                <p><strong>Size:</strong> {documents[currentDocIndex].size}</p>
                <p><strong>Content:</strong> {documents[currentDocIndex].content}</p>
              </div>
            )}
            <div className="flex justify-between mt-4">
              <button
                className="bg-gray-400 text-white px-3 py-1 rounded disabled:opacity-50"
                disabled={currentDocIndex === 0}
                onClick={() => setCurrentDocIndex((prev) => Math.max(prev - 1, 0))}
              >
                Previous
              </button>
              <button
                className="bg-blue-500 text-white px-3 py-1 rounded disabled:opacity-50"
                disabled={currentDocIndex === documents.length - 1}
                onClick={() => setCurrentDocIndex((prev) => Math.min(prev + 1, documents.length - 1))}
              >
                Next
              </button>
            </div>
            <button
              className="mt-4 bg-red-500 text-white px-4 py-2 rounded w-full"
              onClick={() => setSelectedNode(null)}
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Graph;
