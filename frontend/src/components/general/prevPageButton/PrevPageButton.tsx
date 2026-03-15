import { useNavigate, useNavigationType } from "react-router-dom";
import { ReactComponent as BackArrowIcon } from "../../assets/icons/back-arrow-curved.svg";
import "./PrevPageButton.css";

export default function PrevPageButton({ children }: SingleChildrenProp) {
  ////    BUTTON FOR NAVIGATING TO PREVIOUS PAGE

  // if no previous page, navigates to all home page

  const navigator = useNavigate();
  const navigationType = useNavigationType();

  const goBack = (): void => {
    // check if any previous page has been visited on current tab
    // if no previous page, navigate to home page
    if (Number(window.history.length) > 2 && navigationType == "POP") {
      navigator(-1);
    } else {
      navigator("/");
    }
  };

  return (
    <button
      className="btn prev-page-btn fetch-more-btn"
      onClick={goBack}
      type="button"
      aria-label="previous page"
    >
      <BackArrowIcon className="icon btn-icon" aria-label="back arrow icon" />
      {children}
    </button>
  );
}
