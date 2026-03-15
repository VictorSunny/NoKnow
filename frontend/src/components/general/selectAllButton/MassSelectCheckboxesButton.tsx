import React, { SetStateAction } from "react";
import {
  deselectAllCheckBoxes,
  selectAllCheckBoxes,
} from "../../../utilities/formCheckboxHandlers";
import { APIModelName, SetBoolState } from "../../../types/types";

type Props = {
  setSelectAll: SetBoolState;
  selectAll: boolean;
  modelName: APIModelName;
};
export default function MassSelectCheckboxesButton({ selectAll, setSelectAll, modelName }: Props) {
  const handleSelectAllClick = () => {
    setSelectAll((prev) => !prev);
    selectAllCheckBoxes(modelName);
  };
  const handleDeselectAllClick = () => {
    setSelectAll((prev) => !prev);
    deselectAllCheckBoxes(modelName);
  };

  return (
    <button
      onClick={(selectAll && handleDeselectAllClick) || handleSelectAllClick}
      className={`toggle-btn btn ${(selectAll && "active") || ""}`}
      type="button"
    >.
    </button>
  );
}
