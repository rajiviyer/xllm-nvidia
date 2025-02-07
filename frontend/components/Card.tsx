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
      {title_text && ( <div className="title"><span className="text-viridian font-bold">TITLE: </span>{title_text}</div> ) }
      {rank && ( <div className="rank"><span className="text-mahogany font-bold">Rank: </span>{rank}</div> ) }
      { size && ( <div className="size"><span className="text-rosewood font-bold">Size: </span>{size}</div> ) }
      { 
        agents && (
          <div>
            <div className="text-midnightgreen font-bold text-center">
              Tag(s): 
            </div>
            <div className="tags">
              {agents.split(",").slice(0, 5).map(
                (agent) =>
                  agent.trim() !== "" && (
                    <span key={agent} className="tag">
                      {agent}
                    </span>
                  )
              )}
            </div>
          </div> 
        ) 
      }      
      {isTooltipVisible && <div className="tooltip">{description_text.substring(0, 500) + "..."}</div>}
    </div>
  );
};
export default Card;
