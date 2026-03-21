import { motion } from "framer-motion";
import { SingleChildrenProp } from "../types/types";

function AnimatedPageWrapper({ children }: SingleChildrenProp) {
  //// WRAPPER TO ANIMATE PAGES ON NAVIGATION

  return (
    <motion.div
      initial={{
        opacity: 0,
        display: "flex",
        flexDirection: "column",
        height: "inherit",
      }}
      animate={{
        opacity: 1,
        x: 0,
      }}
      exit={{
        opacity: 0,
      }}
      transition={{
        duration: 0.15,
        delay: 0.15,
      }}
    >
      {children}
    </motion.div>
  );
}

export default AnimatedPageWrapper;
