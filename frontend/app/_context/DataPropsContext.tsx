"use client";
import React, { createContext, useContext, useState, ReactNode, useRef } from "react";
import { DataProps } from "@/lib/utils/types";

interface DataPropsContextType {
  result: DataProps;
  setResult: React.Dispatch<React.SetStateAction<DataProps>>;
}

export const DataPropsContext = createContext<DataPropsContextType | undefined>(
  undefined
);

export const DataPropsContextProvider: React.FC<{children: ReactNode}> = ({children}) => {
  const [result, setResult] = useState<DataProps>({ embeddings: [], docs: []}); 
  return (
    <DataPropsContext.Provider value={{ result, setResult }}>
        {children}
    </DataPropsContext.Provider>
  );
};

// Custom hook to access the context
export const useDataPropsContext = (): DataPropsContextType => {
  const context = useContext(DataPropsContext);
  if (!context) {
      throw new Error('DataPropsContext must be used within a Provider');
  }
  return context;
}