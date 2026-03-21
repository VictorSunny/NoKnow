import { motion } from "framer-motion";
import { SingleChildrenProp } from "../types/types";

function AnimatedWindowWrapper({ children }: SingleChildrenProp) {
  //// WRAPPER TO ANIMATE PAGES ON NAVIGATION

  return (
    <motion.div
      initial={{
        x: "100%",
        display: "flex",
        flexDirection: "column",
        height: "100%",
      }}
      animate={{
        x: 0,
      }}
      exit={{
        opacity: 0,
        x: "-100%",
      }}
      transition={{
        duration: 0.4,
      }}
      className="window-container"
    >
      {children}
    </motion.div>
  );
}

export default AnimatedWindowWrapper;
