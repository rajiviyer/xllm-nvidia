import React, { useRef, useState, useEffect, forwardRef } from "react";
import dynamic from "next/dynamic";
import { GraphData, GraphNode, GraphLink, Embedding, FormData, Doc } from "@/lib/utils/types";
import Button from "./Button";

const ForceGraph2D = dynamic(() => import("@/lib/utils/NoSSRForceGraph"), { ssr: false });

// const ForceGraph2D = dynamic(
//   () => import("react-force-graph-2d"),
//   { ssr: false, loading: () => <div>Loading Graph...</div> }
// );

// const NoSSRForceGraph = forwardRef((props: any, ref: any) => (
//   <ForceGraph2D ref={ref} {...props} />
// ));

const getNodeColor = (node: GraphNode) => {
  if (node.isParent) {
    // return "#ff5733";
    // return "#616a6b";
    return "#7f8c8d"
  }
  // const colors = ["#3498db", "#2ecc71", "#f1c40f", "#9b59b6", "#e74c3c", "#1abc9c"];
  const colors = ["#b7950b"];
  const hash = node.id.split("").reduce((acc, char) => acc + char.charCodeAt(0), 0);
  return colors[hash % colors.length];
};

interface GraphProps {
  embeddings: Embedding[];
  formDataGlobal: FormData;
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

const Graph = ( { embeddings, formDataGlobal }: GraphProps) => {
  const fgRef = useRef<any>(null);
  const [graphData, setGraphData] = useState<GraphData>(updateGraphData(embeddings, "", 0.3));
  const [sourceFilter, setSourceFilter] = useState<string>("");
  const [pmiThreshold, setPmiThreshold] = useState<number>(0.2);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [documents, setDocuments] = useState<Doc[]>([]);
  const [currentDocIndex, setCurrentDocIndex] = useState<number>(0);
  const URL = process.env.NEXT_PUBLIC_API_URL;


  useEffect(() => {
    const updatedData = updateGraphData(embeddings, sourceFilter, pmiThreshold);
    setGraphData(updatedData);
  }, [embeddings, sourceFilter, pmiThreshold]);


  useEffect(() => {
    console.log(`fgRef.current: ${fgRef.current}`);
    
    if (!fgRef.current) return;

    fgRef.current.d3Force("link")?.distance((link: GraphLink) => {
        const minDist = 30;  // Minimum distance for high weight
        const maxDist = 200; // Maximum distance for low weight

        // ✅ Normalize weight (assuming weights are between 0 and 1)
        const normalizedWeight = Math.max(0, Math.min(1, link.weight));

        // ✅ Calculate distance (higher weight = closer distance)
        return maxDist - (normalizedWeight * (maxDist - minDist));
    });

    fgRef.current.d3ReheatSimulation(); // ✅ Restart simulation to apply changes
  }, [graphData]); // ✅ Re-run effect when graph data changes

  const checkRef = () => {
    console.log(`fgRef.current: ${fgRef.current}`);
  }

  const handleNodeClick = (node: any) => {
    const nodeId = node.id as string;
    const isLeafNode = !graphData.links.some(link => (link.source as GraphNode).id === nodeId);
    if (isLeafNode) {
      setSelectedNode({ id: nodeId, label: node.label ?? nodeId, isParent: node.isParent ?? false });
      const formParams = {
          ...formDataGlobal,
        queryText: nodeId
      }
      console.log(`formParams in Graph Page: ${JSON.stringify(formParams)}`);
      
      fetch(`${URL}/api/docs`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formParams),
      })
        .then((response) => response.json())
        .then((data) => {
          setDocuments(data.docs);
          setCurrentDocIndex(0);
        })
        .catch((error) => {
          console.error("Error fetching documents:", error);
        }); 
    }
  };

  return (
    <div className="w-full h-screen flex flex-col bg-white">
      <div className="mx-4 mt-2 mb-4 space-y-2 flex flex-wrap items-center gap-4">
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
        {/* <div className="text-sm">
          <Button buttonType="button" onClick={checkRef}>Debug</Button>
        </div> */}
      </div>
      <ForceGraph2D
        ref={fgRef}
        graphData={graphData}
        nodeRelSize={5}
        nodeAutoColorBy="group"
        linkDirectionalArrowLength={5}
        // linkDirectionalArrowLength={(link: any) => {
        //   const normalizedPmi = link.weight ?? 0;
        //   const minArrow = 5;
        //   const maxArrow = 20;
        //   return minArrow + normalizedPmi * (maxArrow - minArrow);
        // }}        
        onNodeClick={handleNodeClick}
        nodeLabel={(node: any) => {
          const linkForNode = graphData.links.find(link => (link.target as GraphNode).id === node.id);
          // return linkForNode ? `${node.label} (PMI: ${linkForNode.weight.toFixed(2)})` : node.label;
          return linkForNode ? `PMI: ${linkForNode.weight.toFixed(2)}` : node.label;
        }}        
        nodeCanvasObject={(node: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
          const fontSize = Math.max(10 / globalScale, 3);
          ctx.font = `${fontSize}px Sans-Serif`;
          ctx.textAlign = "center";
          ctx.textBaseline = "middle";

          const label = node.label ?? node.id ?? "Unknown";
          const linkForNode = graphData.links.find(link => (link.target as GraphNode).id === node.id);
          const normalizedPmi = linkForNode ? linkForNode.weight : 0;
          const minNodeSize = 5;
          const maxNodeSize = 10;
          const nodeSize = minNodeSize + normalizedPmi * (maxNodeSize - minNodeSize);         

          ctx.fillStyle = getNodeColor(node as GraphNode);
          ctx.beginPath();
          // ctx.arc(node.x ?? 0, node.y ?? 0, 10, 0, 2 * Math.PI, false);
          ctx.arc(node.x ?? 0, node.y ?? 0, nodeSize, 0, 2 * Math.PI, false);
          ctx.fill();

          // ctx.fillStyle = (node.isParent ? "#3498db" : "#000");
          // ctx.fillStyle = (node.isParent ? " #616a6b " : "#000");
          ctx.fillStyle = "#000";
          // ctx.fillText(label, (node.x ?? 0) + 12, (node.y ?? 0) + 4);
          ctx.fillText(label, (node.x ?? 0) + nodeSize + 5, (node.y ?? 0) + 4);
        }}
      />

      {selectedNode && documents.length > 0 && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center">
          <div className="bg-white p-4 rounded shadow-md w-96 text-black">
            <h2 className="text-lg font-bold mb-2">Documents for: {selectedNode.label}</h2>
            <div className="border p-2 mb-4">
              <p><strong>ID:</strong> {documents[currentDocIndex].id}</p>
              <p><strong>Rank:</strong> {documents[currentDocIndex].rank}</p>
              <p><strong>Size:</strong> {documents[currentDocIndex].size}</p>
              <p><strong>Content:</strong> {documents[currentDocIndex].content?.description_text.substring(0, 100) + "..."}</p>
            </div>
            <div className="flex justify-between">
              <button
                disabled={currentDocIndex === 0}
                className="bg-gray-300 text-black px-4 py-2 rounded disabled:opacity-50"
                onClick={() => setCurrentDocIndex(currentDocIndex - 1)}
              >
                Previous
              </button>
              <button
                disabled={currentDocIndex === documents.length - 1}
                className="bg-blue-500 text-white px-4 py-2 rounded disabled:opacity-50"
                onClick={() => setCurrentDocIndex(currentDocIndex + 1)}
              >
                Next
              </button>
            </div>
            <button
              className="mt-4 w-full bg-bondingai_secondary text-black px-4 py-2 rounded"
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
