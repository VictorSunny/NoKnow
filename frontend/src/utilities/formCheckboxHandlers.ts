export function selectAllCheckBoxes(targetName: string) {
  const allSelectedNodes = document.querySelectorAll(`input[type=checkbox][name=${targetName}]`);
  allSelectedNodes.forEach((node) => {
    if (node instanceof HTMLInputElement) {
      node.checked = true;
    }
  });
}

export function deselectAllCheckBoxes(targetName: string) {
  const allSelectedNodes = document.querySelectorAll(`input[type=checkbox][name=${targetName}]`);
  allSelectedNodes.forEach((node) => {
    if (node instanceof HTMLInputElement) {
      node.checked = false;
    }
  });
}

export function getSelectedCheckboxes(targetName: string): {
  length: number;
  value: string;
} {
  const selectedChechboxes = Array.from(
    document.querySelectorAll(`input[type=checkbox][name=${targetName}]:checked`)
  );
  const valueString = selectedChechboxes
    .map((selectedNode) => {
      if (selectedNode instanceof HTMLInputElement) {
        return selectedNode.value;
      }
    })
    .join(",");
  return {
    length: selectedChechboxes.length,
    value: valueString,
  };
}

/**
 * Removes items in the document with matching IDs.
 * @param targetStringList
 * comma seperated list of target IDs
 * @param prefix
 * id prefix to be attached on document select query. needed when target ID is a UUID e.g uuid4 which start with an integer
 * @returns
 */
export function removeItemsbyIDS(targetStringList: string, prefix?: string) {
  const IDsArray = targetStringList.split(",");
  Array.from(IDsArray).map((ID) => {
    const selector = (prefix && `${prefix}-${ID}`) || ID;
    const selectedChatroom = document.getElementById(selector);
    selectedChatroom && selectedChatroom.remove();
  });
  return;
}
