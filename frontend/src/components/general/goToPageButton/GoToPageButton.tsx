import { Link } from "react-router-dom";

type GoToPageButtonProps = {
  children: React.ReactNode;
  toUrlPath: string;
};

export default function GoToPageButton({ children, toUrlPath }: GoToPageButtonProps) {
  ////    BUTTON FOR NAVIGATING PAGES USING URL PATH

  return (
    <button className="btn fetch-more-btn" type="button" aria-label="load more content">
      <Link className="btn-a page-nav-link" to={toUrlPath}>
        {children}
      </Link>
    </button>
  );
}
