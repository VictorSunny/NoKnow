import Backdrop from "../backdrop/Backdrop";
import { motion } from "framer-motion";
import { ZOOM_TO_FULL_SIZE } from "../../../animations/ModuleOpenAnimations";
import "./styles/ConfirmActionDialogue.css";

type Props = {
  children: React.ReactNode;
  setModalDisplayState: React.Dispatch<React.SetStateAction<boolean>>;
};
export default function ConfirmActionDialogue({ children, setModalDisplayState }: Props) {
  const animationVariant = ZOOM_TO_FULL_SIZE;
  return (
    <>
      <motion.div
        variants={animationVariant}
        initial={"initial"}
        animate={"animate"}
        exit={"exit"}
        className="modal confirm-action-dialogue-modal"
        layout
      >
        {children}
        <button
          type="button"
          name="button"
          aria-label="cancel action"
          className="btn cancel-btn"
          onClick={() => {
            setModalDisplayState(false);
          }}
        >
          cancel
        </button>
      </motion.div>
      <Backdrop dimmed={true} setModalDisplayState={setModalDisplayState} />
    </>
  );
}
