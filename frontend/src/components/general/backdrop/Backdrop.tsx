import React, { useEffect, useRef, useState } from "react";
import { useLocation } from "react-router-dom";
import "./Backdrop.css";

type backdropProps = {
  setModalDisplayState: React.Dispatch<React.SetStateAction<boolean>>;
  dimmed?: boolean;
};

function Backdrop({ setModalDisplayState, dimmed }: backdropProps) {
  //// ADD BACKROP UPON DISPLAY OF POPOVER ELEMENT

  // function for closing modal on special keypresses for improved accessibility
  const handleKeyClick = (e: KeyboardEvent): void => {
    (e.key == "Escape") && setModalDisplayState(false);
  };

  useEffect(() => {
    // add event listener for escape
    document.addEventListener("keydown", handleKeyClick);
    return () => {
      // reset modifications to page
      document.removeEventListener("keydown", handleKeyClick);
    };
  }, []);

  const closePopover = () => {
    // close popover and backdrop when user clicks on backdrop outside popover e.g dropdown, popup...
    return setModalDisplayState(false);
  };

  return (
    <div
      onClick={closePopover}
      className={`backdrop ${(dimmed && "dimmed") || "transparent"}`}
    ></div>
  );
}

export default Backdrop;
