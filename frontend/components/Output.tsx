import Card from "./Card";
import { Doc, Embedding, DataProps } from "@/lib/utils/types";
import React, {useState} from 'react';
import ReactMarkdown from "react-markdown";
import Button from "./Button";
import "./Output.css";
import { useRouter } from "next/navigation";
function Output({ result }: { result: DataProps }) {

  const docs: Doc[] = result["docs"];
  const router = useRouter();

  const nResult: number = docs.length;
  const embeddingsData: Embedding[] = result["embeddings"];

  const nEmbeddings: number = embeddingsData.length;
  console.log("nEmbeddings", nEmbeddings);
  console.log("nResult", nResult);

  console.log("embeddingsData", embeddingsData);

  const [selectedDoc, setSelectedDoc] = useState<Doc | null>(null);
  const [isContentExpanded, setIsContentExpanded] = useState(false);

  // Embeddings toggle state
  const [isEmbeddingsExpanded, setIsEmbeddingsExpanded] = useState(false);

  const openModal = (doc: Doc) => {
    console.log("clicked");

    setSelectedDoc(doc);

    // Reset description state when a new modal is opened
    setIsContentExpanded(false);
  };

  // Function to close the modal
  const closeModal = () => {
    setSelectedDoc(null);
  };

  // Toggle description expansion
  const toggleContent = () => {
    setIsContentExpanded(!isContentExpanded);
  };

  // Toggle embeddings container
  const toggleEmbeddings = () => {
    setIsEmbeddingsExpanded(!isEmbeddingsExpanded);
  };

  const openGraphPage = () => {
    // Encode `embeddingsData` into a URL-safe JSON string
    // const encodedEmbeddings = encodeURIComponent(JSON.stringify(embeddingsData));
    // window.open(`/graph`, "_blank"); // Opens graph page in a new tab
    router.push("/graph");
  };

  return (
    <div>
      {nResult > 0 && (
        <div>        
          <h2 className="text-slate-100 mb-3 text-center mt-6">Docs</h2>
          {/* Button to toggle embeddings container */}
          {nEmbeddings > 0 && (
            <div className="flex justify-left columns-2 gap-4">
              <Button buttonType="button" onClick={toggleEmbeddings}>
                {isEmbeddingsExpanded ? "Hide Embeddings" : "Show Embeddings"}
              </Button>              
              {/* <button onClick={toggleEmbeddings} className="embeddings-btn">
                {isEmbeddingsExpanded ? "Hide Embeddings" : "Show Embeddings"}
              </button> */}
              {/* ✅ Button to open graph page */}
              <Button buttonType="button" onClick={openGraphPage}>
                View Graph
              </Button>
            </div>
          )}
          {/* Expandable container for embeddings data */}
          {nEmbeddings > 0 && isEmbeddingsExpanded && (
            <div className="embeddings-container">
              <table className="embeddings-table">
                <thead>
                  <tr>
                    <th>Word [from prompt]</th>                    
                    <th>Token [from embeddings]</th>
                    <th>PMI</th>
                  </tr>
                </thead>
                <tbody>
                  {embeddingsData.map((embedding, index) => (
                    <tr key={index}>
                      <td>{embedding.word}</td>                      
                      <td>{embedding.embedding}</td>
                      <td>{embedding.pmi.toFixed(2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}                
          <p className="text-slate-100 mb-6 text-center text-xs italic mt-4">
            * Click on a card to see more details
          </p>
        </div>
      )}
      <div className="flex flex-wrap gap-4 align-middle relative z-[1]">
        {docs.map((doc, index) => {
          return <Card key={index} doc={doc} onClick={() => openModal(doc)} />;
        })}
        {selectedDoc && (
          <div className="modal-overlay">
            <div className="modal">
              <p className="modal-content">
                <span className="text-sunset font-bold">ID: </span>
                {selectedDoc.id}
              </p>
              <p className="modal-content">
                <span className="text-sunset font-bold">Rank: </span>
                {selectedDoc.rank}
              </p>
              <p className="modal-content">
                <span className="text-sunset font-bold">Size: </span>
                {selectedDoc.size}
              </p>
              {selectedDoc.content?.title_text && (
                <p className="modal-content">
                  <span className="text-sunset font-bold">Title: </span>
                  {selectedDoc.content?.title_text}
                </p>
              )}
              <p className="modal-content">
                <span className="text-sunset font-bold">Content: </span>
                {/* Display partial or full description based on state */}
                {isContentExpanded
                  ? selectedDoc.content?.description_text
                  : selectedDoc.content?.description_text.substring(0, 50) + "..."}
                <a
                  href="#"
                  onClick={toggleContent}
                  style={{
                    color: "#0891B2",
                    fontSize: "1rem",
                  }}
                >
                  {isContentExpanded ? " -" : " +"}
                </a>
              </p>
              <button id="close-card-btn" className="mt-4" onClick={closeModal}>
                Close
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
export default Output;
