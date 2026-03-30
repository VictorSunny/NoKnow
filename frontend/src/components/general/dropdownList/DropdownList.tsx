import React, { useState } from "react";
import "./DropdownList.css";

type dropdownProps = {
  dropdownItems: {
    heading: string;
    show: boolean;
    sectionLinks: React.ReactNode[];
  }[];
};

export default function DropdownList({ dropdownItems }: dropdownProps) {
  ////    DROPDOWN LIST OF ELEMENTS

  const [activeDropdownID, setActiveDropdownID] = useState<number | null>();

  // on click of dropdown item, expand and display subitems
  // if any other dropdown item is already expanded, close that dropdown
  const handleDropdownClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    if (typeof e.currentTarget.value == "number") {
      const dropdownItemID = e.currentTarget.value;
      activeDropdownID != dropdownItemID
        ? setActiveDropdownID(dropdownItemID)
        : setActiveDropdownID(null);
    }
  };

  return (
    <>
      <div className="dropdown-list-container">
        {dropdownItems.map((dropdownObj, index) => {
          return (
            <div
              key={index}
              className={`drop-list ${((index == activeDropdownID || dropdownObj.show) && "active-drop-list") || null}`}
            >
              <button
                value={index}
                className="drop-list-btn"
                onClick={handleDropdownClick}
                type="button"
                aria-label="dropdown"
              >
                {dropdownObj.heading}
              </button>
              <ul className="drop-list-content">
                {dropdownObj.sectionLinks!.map((listItem, listItemIndex) => {
                  return <li key={listItemIndex}>{listItem}</li>;
                })}
              </ul>
            </div>
          );
        })}
      </div>
    </>
  );
}
