"use client";
import "./Card.css";
import React from "react";
import { CardProps } from "@/lib/utils/types";
import Button from "./Button";
import Link from "next/link";
import { useState } from "react";
const Card: React.FC<CardProps> = ({ doc, onClick }) => {
  const [isTooltipVisible, setIsTooltipVisible] = useState(false);
  console.log("doc", doc);
  
  // const { category, title, tags, description } = doc;
  const { id, agents, content, rank, size, hash_id } = doc;
  console.log(`content: ${content}`);
  const { title_text, description_text } = content;
  console.log(`title_text: ${title_text}, description_text: ${description_text}`);
  
  // console.log(`id: ${id}, content: ${content}, rank: ${rank}, size: ${size}, hash_id: ${hash_id}`);
  
  // Function to open the modal
  return (
    // <div className="text-white">Card</div>
    <div
      className="card"
      onMouseEnter={() => setIsTooltipVisible(true)}
      onMouseLeave={() => setIsTooltipVisible(false)}
      onClick={onClick} // Clicking the card opens the modal
    >
      {/* {title_text && ( <div className="title">{title_text}</div> ) } */}
      {rank && ( <div className="rank"><span className="text-mahogany font-bold">Rank: </span>{rank}</div> ) }
      { size && ( <div className="size"><span className="text-rosewood font-bold">Size: </span>{size}</div> ) }
      { 
        agents && ( 
          <div className="agents"><span className="text-midnightgreen font-bold">Agent(s): </span>
            <div className="agents">
              {agents.split(",").slice(0, 5).map(
                (agent) =>
                  agent.trim() !== "" && (
                    <span key={agent} className="agent">
                      {agent}
                    </span>
                  )
              )}
            </div>
          </div> 
        ) 
      }      
      {isTooltipVisible && <div className="tooltip">{description_text}</div>}
    </div>
  );
};
export default Card;
