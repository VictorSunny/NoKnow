import { Transition } from "framer-motion";

export const TRANSITION: Record<string, Transition> = {
  springSlow: { delay: 0.2, duration: 0.9, type: "tween", repeat: 0, damping: 32, stiffness: 80 },
  springFast: { delay: 0.2, duration: 0.6, type: "tween", repeat: 0, damping: 32, stiffness: 80 },
  springFastest: {
    duration: 0.1,
    type: "tween",
    repeat: 0,
    damping: 6,
    stiffness: 100,
  },
};
