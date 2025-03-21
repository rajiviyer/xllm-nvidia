"use client";
import React, { useContext } from 'react';
import Graph from "@/components/Graph";
import { DataPropsContext } from "@/app/_context/DataPropsContext";
import { FormDataContext } from '@/app/_context/FormDataContext';

export default function GraphPage() {

    const formDataContext = useContext(FormDataContext);
    if (!formDataContext) {
    throw new Error('formDataContext is not available');
    }
    
    const { formDataGlobal, setFormDataGlobal } = formDataContext;

    const dataPropsContext = useContext(DataPropsContext);
    if (!dataPropsContext) {
    throw new Error('dataPropsContext is not available');
    }
    
    const { result, setResult } = dataPropsContext;       

    console.log("embeddings in GraphPage", result.embeddings);
      

    return (
        <div className="w-full h-screen flex flex-col">
            <h1 className="text-xl font-bold text-center p-4 bg-white">Graph Visualization</h1>
            <Graph embeddings={result.embeddings} formDataGlobal={formDataGlobal} />
        </div>
    );
}