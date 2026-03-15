import React, { useState } from "react";
import "./DropdownSelect.css";
import Backdrop from "../backdrop/Backdrop";
import useResetStates from "../../../hooks/useResetStates";
import { KeyText } from "../../../types/types";

type dropdownSelectProps = {
  title: string;
  selectedValue: string | number;
  optionsList: string[] | number[];
  optionTexts: KeyText<any>;
  setStateValue: React.Dispatch<React.SetStateAction<any>>;
  buttonsDisabled: boolean;
};

export default function DropdownSelect({
  title,
  selectedValue,
  optionsList,
  optionTexts,
  setStateValue,
  buttonsDisabled,
}: dropdownSelectProps) {
  ////   DROPDOWN WITH OPTIONS TO CHANGE CONTEXT STATE VALUE FROM SUPPORTED CONTEXT OPTIONS

  const [dropdownIsActive, setDropdownIsActive] = useState<boolean>(false);
  const _ = useResetStates([setDropdownIsActive]);

  const openCloseDropDown = () => {
    return setDropdownIsActive((prev) => !prev);
  };

  const changeDropdownValue = (e: React.MouseEvent<HTMLButtonElement>) => {
    const newSelectedValue = e.currentTarget.value;
    setStateValue(newSelectedValue);
    return setDropdownIsActive(false);
  };

  return (
    <div
      className={`dropdown-container filter-container ${dropdownIsActive && "no-scroll-exempt"}`}
    >
      {dropdownIsActive && <Backdrop dimmed setModalDisplayState={setDropdownIsActive} />}
      <span className="filter-title">{title}</span>
      <button
        className="btn filter-btn"
        onClick={openCloseDropDown}
        type="button"
        aria-label="dropdown"
        disabled={buttonsDisabled}
      >
        {optionTexts[selectedValue]}
      </button>
      <div className={`filter-options-container ${dropdownIsActive && "show-dropdown"}`}>
        {optionsList.map((option, index) => {
          return (
            <button
              key={index}
              id={`option-${title}-${option}`}
              value={option}
              onClick={changeDropdownValue}
              className={`option ${(option === selectedValue && "active") || ""}`}
              disabled={buttonsDisabled}
            >
              {optionTexts[option]}
            </button>
          );
        })}
      </div>
    </div>
  );
}
