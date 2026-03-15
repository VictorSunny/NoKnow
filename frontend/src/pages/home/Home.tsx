import { useAuthContext } from "../../contexts/AuthContext";
import "./Home.css";
import "../../components/general/speechBubble/SpeechBubble.css";
import { Link } from "react-router-dom";
import SpeechBubble from "../../components/general/speechBubble/SpeechBubble";
import useSetPageTitle from "../../hooks/useSetPageTitle";
import { ReactComponent as SiteLogoSVG } from "../../assets/site-logo.svg";
import { AnimatePresence } from "framer-motion";

function Home() {
  const { userDetails } = useAuthContext();
  const _ = useSetPageTitle("Home");

  return (
    <div className="page-container home-page-container">
      <div className="section hero-container">
        <div className="hero-site-logo-container">
          <SiteLogoSVG className="hero-site-logo" />
        </div>
        <AnimatePresence>
          <div className="hero-section primary">
            <SpeechBubble tickerPosition="left" to="/chat">
              enter
            </SpeechBubble>
            <div></div>
            <div></div>
            <SpeechBubble tickerPosition="right" to="/chat/create">
              start
            </SpeechBubble>
          </div>
          {(!userDetails && (
            <div className="hero-section secondary">
              <SpeechBubble tickerPosition="both" to="/auth/login">
                login
              </SpeechBubble>
            </div>
          )) || (
            <div className="hero-section secondary">
              <SpeechBubble tickerPosition="both" to="/auth/account">
                profile
              </SpeechBubble>
            </div>
          )}
        </AnimatePresence>
      </div>
      <Link to="/guide" id="guide-page-link">
        <span>?</span>
      </Link>
    </div>
  );
}

export default Home;
