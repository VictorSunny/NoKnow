import "./FetchModals.css";
import { ReactComponent as BouncingCircles } from "../../../assets/animations/bouncing-circles.svg";
import { SingleChildrenProp } from "../../../types/types";

function LineLoadingSignal({ children }: SingleChildrenProp) {
  return (
    <div className="line-loading-signal signal-modal">
      <div>
        <span className="signal-modal-title">{(children && children) || "loading"}</span>
        <BouncingCircles className="signal-icon" aria-label="line loading animation" />
      </div>
    </div>
  );
}

export default LineLoadingSignal;
