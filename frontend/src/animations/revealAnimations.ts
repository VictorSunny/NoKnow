import { Variants } from "framer-motion";
import { TRANSITION } from "./Transitions";

export const REVEAL_EXPAND_FROM_LEFT: Variants = {
  initial: {
    width: "0%",
    transformOrigin: "left",
  },
  animate: {
    width: "100%",
    transition: TRANSITION.springFast,
  },
  exit: {
    width: "0%",
    transition: TRANSITION.springFastest,
  },
};
