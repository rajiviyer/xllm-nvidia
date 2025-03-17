export interface FormType {
  useStem: boolean;
  beta: number;
  nresults: number;
  distill: boolean;
  maxTokenCount: number;
  queryText: string;
}

export interface OptionButtonProps {
  handleOptionButtonClick: (option: boolean) => void;
  selectedOption: boolean;
  option1: string;
  option2: string;
}

// export interface CardProps {
//   category: string;
//   title: string;
//   tags: string;
//   description: string;
// }

export interface CardProps {
  doc: Doc;
  onClick: () => void; // Prop for handling card clicks
}

interface DocContent {
  title_text: string;
  description_text: string;
  doc_ID: number;
  pn: number;
  type: string;
  fc?: number;
  fs?: number;
  ft?: string;
  item_ID?: number;
  sub_ID?: number;
}
export interface Doc {
  id: string;
  agents: string;
  content: DocContent;
  rank: number;
  size: number;
  hash_id: string;
}

export interface Embeddings {
  // n: number;
  pmi: number;
  // f: string;
  embedding: string;
  word: string;
}

// Define the interface for the function argument
export interface DataProps {
  embeddings: Embeddings[];
  docs: Doc[];
  complete_content: string;
}
export interface ResultDocProps {
  setResult: (result: DataProps) => void;
}

export type GraphNode = {
  id: string;
  label: string;
  isParent?: boolean; // New property to mark parent nodes
};

export type GraphLink = {
  source: GraphNode;
  target: GraphNode;
  weight: number;
};

export type GraphData = {
  nodes: GraphNode[];
  links: GraphLink[];
};

export interface GraphProps {
  embeddings: Embeddings[];
};