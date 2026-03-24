import { motion } from "framer-motion";
import { SingleChildrenProp } from "../types/types";
import { useLocation } from "react-router-dom";

function AnimatedPageWrapper({ children }: SingleChildrenProp) {
  //// WRAPPER TO ANIMATE PAGES ON NAVIGATION
  const location = useLocation()
  return (
    <motion.div
      key={location.pathname}
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
