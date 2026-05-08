import React from "react";
import { motion } from "framer-motion";
import "./LoadMoreButton.css";

import { ReactComponent as FadingDotsAnimation } from "../../../assets/animations/loader-wifi.svg";
import { ReactComponent as ErrorIcon } from "../../../assets/icons/alert-error-icon.svg";
import { ReactComponent as DoubleStrokeDownArrows } from "../../../assets/icons/down-double-stroke-icon.svg";
import { ReactComponent as WaitPalmIcon } from "../../../assets/icons/wait-palm.svg";

type Props = {
  itemName: string;
  isFetchingNextPage: boolean;
  isFetchNextPageError: boolean;
  allFetched: boolean;
  onClick: (e: React.MouseEvent<HTMLButtonElement> | undefined) => void;
};
export default function LoadMoreButton({
  itemName,
  isFetchingNextPage,
  isFetchNextPageError,
  allFetched,
  onClick,
}: Props) {
  return (
    <motion.button
      className={`btn fetch-more-btn ${isFetchingNextPage && "load"}`}
      type="button"
      aria-label={`load more ${itemName}s`}
      onClick={onClick}
      disabled={isFetchingNextPage || allFetched}
      layout
    >
      {/* change button value while fetching next page */}
      {(isFetchingNextPage && (
        <div className="text-icon-container">
          <FadingDotsAnimation className="icon" aria-label="fading dots vector animation" />
        </div>
      )) ||
        (isFetchNextPageError && (
          <div className="text-icon-container">
            <ErrorIcon className="icon" aria-label="attention icon" />
            <span>retry</span>
          </div>
        )) ||
        (allFetched && (
          <div className="text-icon-container">
            <WaitPalmIcon className="icon" aria-label="home icon" />
            <span>end of list</span>
          </div>
        )) || (
          <div className="text-icon-container">
            <DoubleStrokeDownArrows className="icon" aria-label="home icon" />
            <span>load more {itemName}s</span>
          </div>
        )}
    </motion.button>
  );
}
