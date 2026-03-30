import { ReactComponent as FadingCircles } from "../../../assets/animations/fade-stagger-circles.svg";
import { SingleChildrenProp } from "../../../types/types";
import "./styles/Loaders.css";

export default function FadingSpinnerLoader({ children }: SingleChildrenProp) {
  return (
    <div className="fading-line-loading-signal signal-modal">
      <div>
        <span className="signal-modal-title">{(children && children) || "loading"}</span>
        <FadingCircles className="loader-animation" aria-label="fading line loading animation" />
      </div>
    </div>
  );
}
