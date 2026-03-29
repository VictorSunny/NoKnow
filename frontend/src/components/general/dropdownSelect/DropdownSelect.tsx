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

/**
 * Returns a div container with a button element which can trigger a dropdown list for updating a state value with provided options.
 * 
 * @param title
 * string - label title for dropdown button
 * @param selectedValue
 * string | number - current/default state value
 * @param optionsList
 * string | number - array of options for updating state value. should be supported type.
 * @param optionTexts
 * object - each respective key matching an option in `optionsList`, with it's value being a text representation for that option.
 * the set of keys of optionTexts, and the set of `optionsList` values must be equal sets to one another, meaning each option in `optionsList` must have a text representation.
 * @param setStateValue
 * callable - React useState's dispatch callable for setting state value
 * @param buttonsDisabled
 * boolean - If true, the dropdown button is disabled. value is dynamic
 * @returns HTMLDivElement
 */
export default function DropdownSelect({
  title,
  selectedValue,
  optionsList,
  optionTexts,
  setStateValue,
  buttonsDisabled,
}: dropdownSelectProps) {

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
