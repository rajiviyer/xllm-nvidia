import GraphPageContent from "./GraphPageContent";
import { Suspense } from "react";
import { GraphLink } from "@/lib/utils/types";

export default function GraphPage() {

    return (
        <div className="w-full h-screen flex flex-col">
            <h1 className="text-xl font-bold text-center p-4">Graph Visualization</h1>
            <Suspense fallback={<div>Loading Graph...</div>}>
                <GraphPageContent />
            </Suspense>
        </div>
    );
}