import "./FetchModals.css";
import { ReactComponent as LeftRightLoader } from "../../../assets/animations/motion-blur-2.svg";

function LeftRightLoadingSignal() {
  return (
    <div className="left-right-loading-signal signal-modal">
      <div>
        <LeftRightLoader className="loader-animation" aria-label="left right loading animation" />
      </div>
    </div>
  );
}

export default LeftRightLoadingSignal;
