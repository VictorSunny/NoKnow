import React from "react";
import { motion } from "framer-motion";
import "./LoadMoreButton.css";

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
      {(isFetchingNextPage && "loading") ||
        (isFetchNextPageError && "retry") ||
        (allFetched && "end of list") ||
        `load more ${itemName}s`}
    </motion.button>
  );
}
