import "./styles/FormErrorModal.css";

function FormErrorModal({ errorMessage }: { errorMessage: string }) {
  return (
    <div className="error-modal">
      <p>{errorMessage}</p>
    </div>
  );
}

export default FormErrorModal;
