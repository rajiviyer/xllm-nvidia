"use client";
import React, { createContext, useContext, useState, ReactNode, useRef } from "react";
import { FormData } from "@/lib/utils/types";
import { queries } from "@/lib/utils/data";

interface FormDataContextType {
  formDataGlobal: FormData;
  setFormDataGlobal: React.Dispatch<React.SetStateAction<FormData>>;
}

export const FormDataContext = createContext<FormDataContextType | undefined>(
  undefined
);

export const FormDataContextProvider: React.FC<{children: ReactNode}> = ({children}) => {
  const [formDataGlobal, setFormDataGlobal] = useState<FormData>( {
    useStem: true,
    beta: 1.0,
    queryText: queries[0],
    distill: true,
    maxTokenCount: 500,
    nresults: 15
  }); 
  return (
    <FormDataContext.Provider value={{ formDataGlobal, setFormDataGlobal }}>
        {children}
    </FormDataContext.Provider>
  );
};

// Custom hook to access the context
export const useFormDataContext = (): FormDataContextType => {
  const context = useContext(FormDataContext);
  if (!context) {
      throw new Error('FormDataContext must be used within a Provider');
  }
  return context;
}