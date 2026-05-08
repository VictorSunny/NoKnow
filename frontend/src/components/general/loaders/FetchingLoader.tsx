import { ReactComponent as PulseRingsAnimation } from "../../../assets/animations/rings.svg";
import { ReactComponent as WaitPalm } from "../../../assets/icons/wait-palm.svg";
import { ReactComponent as PendelumBeads } from "../../../assets/animations/pendulumn-beads.svg";
import "./styles/Loaders.css";

export default function FetchingLoader() {
  return (
    <div className="fading-line-loading-signal signal-modal">
      <div className="fetching-animations-container">
        <div className="icons-container double">
          <WaitPalm className="icon" aria-label="palm icon" />
          <PulseRingsAnimation
            className="icon loader-animation"
            aria-label="rings loading animation"
          />
        </div>
        <div className="icons-container">
          <PendelumBeads
            className="icon loader-animation"
            aria-label="pendulum beads loading animation"
          />
        </div>
      </div>
    </div>
  );
}
