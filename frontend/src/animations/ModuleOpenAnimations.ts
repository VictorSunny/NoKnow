import { animate, Variants } from "framer-motion";
import { TRANSITION } from "./Transitions";

export const ENGAGE_BOTTOM_LEFT: Variants = {
  initial: {
    scale: 0,
    transformOrigin: "bottom left",
  },
  animate: {
    x: 0,
    y: 0,
    transition: TRANSITION.springFastest,
    scale: 1,
  },
  exit: {
    transition: TRANSITION.springFastest,
    scale: 0,
  },
};

export const ENGAGE_BOTTOM_RIGHT: Variants = {
  initial: {
    scale: 0,
    transformOrigin: "bottom right",
  },
  animate: {
    scale: 1,
    transition: TRANSITION.springFastest,
  },
  exit: {
    scale: 0,
    transition: TRANSITION.springFastest,
  },
};
export const ENGAGE_TOP_LEFT: Variants = {
  initial: {
    scale: 0,
    transformOrigin: "top left",
  },
  animate: {
    scale: 1,
    transition: TRANSITION.springFastest,
  },
  exit: {
    scale: 0,
    transition: TRANSITION.springFastest,
  },
};

export const ZOOM_TO_FULL_SIZE: Variants = {
  initial: {
    scale: 0,
    transformOrigin: "center",
  },
  animate: {
    scale: 1,
    transition: TRANSITION.springFastest,
  },
  exit: {
    scale: 0,
    transition: TRANSITION.springFastest,
  },
};

export const OPEN_FROM_TOP_TO_BOTTOM: Variants = {
  initial: {
    height: 0,
    transformOrigin: "top",
    overflow: "hidden"
  },
  animate: {
    height: "initial",
    transition: TRANSITION.springFastest,
  },
  exit: {
    height: 0,
    transition: TRANSITION.springFastest,
  },
};

export const SLIDE_UP: Variants = {
  initial: {
    position: "fixed",
    top: "3.2rem",
    left: "0",
    right: "0",
    translateY: "-100vh"
  },
  animate: {
    translateY: "0",
    transition: TRANSITION.springFast
  },
  exit: {
    translateY: "-100vh",
    transition: TRANSITION.slow
  },
}