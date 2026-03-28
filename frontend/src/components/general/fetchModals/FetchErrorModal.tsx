import "./FetchModals.css";
import { ReactComponent as CloseIcon } from "../../../assets/icons/close-icon.svg";

type Props = {
  errorMessage: string;
  setModalDisplayState?: React.Dispatch<React.SetStateAction<boolean>>;
  children?: React.ReactNode;
};

function FetchErrorSignal({ errorMessage, setModalDisplayState, children }: Props) {
  const handleClick = () => {
    if (setModalDisplayState) {
      setModalDisplayState(false);
    }
  };
  return (
    <div className="no-data-signal signal-modal">
      <div>
        <span>{errorMessage}</span>
      </div>
      {children && children}
      {setModalDisplayState && (
        <button className="btn return-btn" onClick={handleClick}>
          <CloseIcon className="signal-modal-icon-med" />
        </button>
      )}
    </div>
  );
}

export default FetchErrorSignal;
