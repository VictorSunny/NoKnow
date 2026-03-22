import sleep from "../../../utilities/sleep";

import { ReactComponent as ErrorIcon } from "../../../assets/icons/browser-error-icon.svg";
import { ReactComponent as SuccessIcon } from "../../../assets/icons/approve-accept-icon.svg";
import { useEffect } from "react";
import { motion } from "framer-motion";
import { SLIDE_UP } from "../../../animations/ModuleOpenAnimations";

import "./styles/Minimal.css";
import { SetOptionalTextState } from "../../../types/types";

type Props = {
  popupType: "success" | "fail";
  setMessage: SetOptionalTextState;
  message: string;
  successAction?: () => void;
  speed?: "slow" | "fast" | "fastest";
};
/**
 *
 * popup modal displaying api response message.
 * modal to be displayed on condition that modal message is not undefined.
 * modal auto closes after 2 seconds by default
 *
 * @param popupType
 * string literal - takes values "fail" or "success" to display the correct popup icon
 * @param message
 * string - message for modal to display
 * @param successAction
 * callable[optional] - function to be triggered once modal is closed
 * @returns
 */
function APIResponsePopup({ popupType, message, successAction, setMessage }: Props) {
  ////    POPUP MODAL TO SIGNAL USER ON REQUEST RESPONSE.

  useEffect(() => {
    const autoCloseModal = async () => {
      await sleep((popupType == "fail" && 4000) || 1500);
      (successAction && successAction()) || setMessage(undefined);
    };
    autoCloseModal();

    () => {
      setMessage(undefined);
    };
  }, []);

  return (
    <>
      <motion.div
        variants={SLIDE_UP}
        initial={"initial"}
        animate={"animate"}
        exit={"exit"}
        className={`minimal-modal signal-modal ${popupType}`}
      >
        <div className="main-message-content-container">
          <div className="icon-container">
            {(popupType == "fail" && (
              <ErrorIcon
                className="signal-icon signal-action-response-icon"
                aria-label="error icon"
              />
            )) ||
              (popupType == "success" && (
                <SuccessIcon
                  className="signal-icon signal-action-response-icon"
                  aria-label="success icon"
                />
              ))}
          </div>
          <p>{message}</p>
        </div>
      </motion.div>
    </>
  );
}

export default APIResponsePopup;
