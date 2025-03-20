"use client";
import React, { createContext, useContext, useState, ReactNode, useRef } from "react";
import { Embedding } from "@/lib/utils/types";

interface EmbeddingsContextType {
  embeddings: Embedding[];
  setEmbeddings: React.Dispatch<React.SetStateAction<Embedding[]>>;
}

export const EmbeddingsContext = createContext<EmbeddingsContextType | undefined>(
  undefined
);

export const EmbeddingsContextProvider: React.FC<{children: ReactNode}> = ({children}) => {
  const [embeddings, setEmbeddings] = useState<Embedding[]>([]); 
  return (
    <EmbeddingsContext.Provider value={{ embeddings, setEmbeddings }}>
        {children}
    </EmbeddingsContext.Provider>
  );
};

// Custom hook to access the context
export const useEmbeddingsContext = (): EmbeddingsContextType => {
  const context = useContext(EmbeddingsContext);
  if (!context) {
      throw new Error('EmbeddingsContext must be used within a Provider');
  }
  return context;
}