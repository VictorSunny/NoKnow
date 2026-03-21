import { ReactComponent as LargeUpArrow } from "../../assets/icons/caret-up-icon.svg";
import "./ScrollToTopButton.css";

export default function ScrollToTopButton() {
  ////    BUTTON FOR SCROLLING TO TOP OF PAGE. FOR EASE OF NAVIGATION

  const scrollToTop = () => {
    return window.scrollTo({ top: 0, left: 0, behavior: "smooth" });
  };

  return (
    <div className="scroll-top-btn-container">
      <button
        className="btn scroll-top-btn"
        onClick={scrollToTop}
        aria-label="scroll up button"
        name="button"
      >
        <LargeUpArrow className="icon btn-icon" />
      </button>
    </div>
  );
}
