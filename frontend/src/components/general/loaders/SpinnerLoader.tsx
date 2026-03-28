import { ReactComponent as LeftRightLoader } from "../../../assets/animations/infinite-spinner.svg";
import "./styles/Loaders.css"

export default function SpinnerLoader() {
  return (
    <div className="left-right-loading-signal signal-modal">
      <div>
        <LeftRightLoader className="loader-animation" aria-label="left right loading animation" />
      </div>
    </div>
  );
}
