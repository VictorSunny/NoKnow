import { ReactComponent as CloseIcon } from "../../../../assets/icons/close-icon.svg";
import "../popups.css";

type noDataSignalProps = {
  expectedData: string;
  setModalDisplayState?: React.Dispatch<React.SetStateAction<boolean>>;
};

function NoDataSignal({ expectedData, setModalDisplayState }: noDataSignalProps) {
  const handleClick = () => {
    if (setModalDisplayState) {
      setModalDisplayState(false);
    }
  };
  return (
    <div className="no-data-signal signal-modal">
      <div>
        <span>no {expectedData}. looks empty here.</span>
      </div>
      {setModalDisplayState && (
        <button className="btn return-btn" onClick={handleClick}>
          <CloseIcon className="signal-modal-icon-med" />
        </button>
      )}
    </div>
  );
}

export default NoDataSignal;
