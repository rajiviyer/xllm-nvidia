"use client";
import { useSearchParams } from "next/navigation";
import Graph from "@/components/Graph";
import { Embedding } from "@/lib/utils/types";

export default function GraphPageContent() {
    const searchParams = useSearchParams();
    const embeddingsParam = searchParams.get("embeddings");

    // ✅ Decode and parse embeddings
    let embeddings: Embedding[] = [];
    if (embeddingsParam) {
        try {
            embeddings = JSON.parse(decodeURIComponent(embeddingsParam));
        } catch (error) {
            console.error("❌ Error parsing embeddings from URL:", error);
        }
    }   

    console.log("embeddings in GraphPageContent", embeddings);
    

    return (
        <div className="w-full h-screen flex flex-col">
            <h1 className="text-xl font-bold text-center p-4">Graph Visualization</h1>
            {/* ✅ Pass rawLinks to the Graph component */}
            <Graph embeddings={embeddings} />
        </div>
    );
}
