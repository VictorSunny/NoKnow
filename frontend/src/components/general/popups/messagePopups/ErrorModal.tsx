import { useNavigate, useLocation } from "react-router-dom";
import { ReactComponent as ErrorIcon } from "../../../../icons/fall-accident-icon.svg";
import SiteLogo from "../../siteLogo/SiteLogo";

import "../popups.css";

function ErrorSignal() {
  const navigator = useNavigate();
  const location = useLocation();
  const goHome = (): void => {
    navigator("");
  };
  const refreshPage = () => {
    navigator(location.pathname, { replace: true });
  };

  return (
    <div className="reload-signal signal-modal">
      <SiteLogo />
      <div>
        <ErrorIcon className="signal-icon signal-action-response-icon" aria-label="error image" />
        <p>Sorry. An unexpected error occured.</p>
        <div className="error-btn-container">
          <button
            className="btn signal-btn"
            type="button"
            aria-label="go to homepage"
            onClick={goHome}
          >
            Go Home
          </button>
          <button
            className="btn signal-btn"
            type="button"
            aria-label="try reload"
            onClick={refreshPage}
          >
            Refresh
          </button>
        </div>
      </div>
    </div>
  );
}

export default ErrorSignal;
