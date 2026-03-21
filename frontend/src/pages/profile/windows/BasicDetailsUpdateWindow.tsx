import useSetPageTitle from "../../../hooks/useSetPageTitle";
import BasicDetailsUpdateForm from "../../../components/forms/BasicDetailsUpdateForm";

export default function BasicDetailsUpdateWindow() {
  const _ = useSetPageTitle("basic details");
  return (
    <div className="window basic-details-update-window">
      <div className="window-section grow">
        <BasicDetailsUpdateForm />
      </div>
    </div>
  );
}
