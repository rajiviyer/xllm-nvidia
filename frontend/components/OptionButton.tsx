"use client";
import React from "react";
import { OptionButtonProps } from "@/lib/utils/types";

const OptionButton: React.FC<OptionButtonProps> = ({
  handleOptionButtonClick,
  selectedOption,
  option1,
  option2,
}) => {
  const handleButtonClick = (
    event: React.MouseEvent<HTMLButtonElement, MouseEvent>
  ) => {
    // console.log(`Current option: ${event.currentTarget.value}`);

    if (["Seeded", "Yes"].includes(event.currentTarget.value)) {
      handleOptionButtonClick(true);
    } else {
      handleOptionButtonClick(false);
    }
  };
  return (
    <div>
      <div className="flex flex-wrap border border-bondingai_input_border/[0.60] items-center gap-x-2 bg-bondingai_primary rounded-md">
        <button
          type="button"
          onClick={(event) => handleButtonClick(event)}
          value={option1}
          className={`flex-auto px-2 py-1 mx-2 my-2 rounded text-white text-xs ${
            selectedOption ? "bg-bondingai_secondary/[0.25]" : "bg-bondingai_primary"
          }`}
        >
          {option1}
        </button>
        <button
          type="button"
          onClick={(event) => handleButtonClick(event)}
          value={option2}
          className={`flex-auto px-2 py-1 mx-2 my-2 rounded text-white text-xs ${
            !selectedOption ? "bg-bondingai_secondary/[0.25]" : "bg-bondingai_primary"
          }`}
        >
          {option2}
        </button>
      </div>
    </div>
  );
};
export default OptionButton;
