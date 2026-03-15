import TwoFactorAuthForm from "../../../components/forms/TwoFactorAuthForm";

export default function TwoFactorAuthWindow() {
  return (
    <div className="window two-factor-auth-window">
      <div className="window-section grow">
        <TwoFactorAuthForm />
      </div>
    </div>
  );
}
