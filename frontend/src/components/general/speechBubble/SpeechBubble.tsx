import "./SpeechBubble.css";
import { Link } from "react-router-dom";
import { motion, Variants } from "framer-motion";

import {
  ENGAGE_BOTTOM_LEFT,
  ENGAGE_BOTTOM_RIGHT,
  ZOOM_TO_FULL_SIZE,
} from "../../../animations/ModuleOpenAnimations";
import { ChatMessageType } from "../../../types/chatroomTypes";

type TickerPosition = "left" | "right" | "both";
type SpeechBubbleProps = {
  children: React.ReactNode;
  to?: string;
  animate?: boolean;
  messageType?: ChatMessageType;
  tickerPosition: TickerPosition;
  className?: string;
};

function SpeechBubble({
  children,
  to,
  tickerPosition,
  messageType,
  animate,
  className,
}: SpeechBubbleProps) {
  const VARIANT: Variants =
    (tickerPosition == "left" && ENGAGE_BOTTOM_LEFT) ||
    (tickerPosition == "right" && ENGAGE_BOTTOM_RIGHT) ||
    ZOOM_TO_FULL_SIZE;

  if (to) {
    return (
      <Link to={to!} className={`speech-bubble ${tickerPosition} ${className ?? ""}`}>
        {children}
      </Link>
    );
  }

  if (animate) {
    return (
      <motion.div
        variants={VARIANT}
        initial={"initial"}
        animate={"animate"}
        exit={"exit"}
        className={`speech-bubble ${tickerPosition} ${messageType ?? ""} ${className ?? ""}`}
      >
        {children}
      </motion.div>
    );
  }

  return (
    <div className={`speech-bubble ${tickerPosition} ${messageType} ${className ?? ""}`}>
      {children}
    </div>
  );
}

export default SpeechBubble;
