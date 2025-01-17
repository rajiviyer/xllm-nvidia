import React from "react";
function Button({
  children,
  buttonType,
  onClick,
}: {
  children: React.ReactNode;
  buttonType: "reset" | "button" | "submit";
  onClick?: React.MouseEventHandler<HTMLButtonElement>;
}) {
  return (
    <div>
      <button
        type={buttonType}
        onClick={onClick}
        className="p-2 bg-bondingai_secondary hover:bg-yellow-400 text-black text-sm rounded-md"
      >
        {children}
      </button>
    </div>
  );
}
export default Button;
