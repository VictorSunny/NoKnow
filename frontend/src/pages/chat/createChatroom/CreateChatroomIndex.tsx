import useSetPageTitle from "../../../hooks/useSetPageTitle";
import { CHATROOM_PRIVACY_OPTIONS } from "../../../schemas/ChatSchemas";
import { Link } from "react-router-dom";

import "./CreateChatroom.css";

export default function CreateChatroomIndex() {
  const _ = useSetPageTitle("create chatroom");
  return (
    <div className="page-container create-chatroom-index-page">
      <div className="section util-container">
        {CHATROOM_PRIVACY_OPTIONS.map((roomType, index) => {
          return (
            <Link
              key={index}
              to={roomType}
              className="btn"
              aria-label={`create ${roomType} chatroom`}
            >
              {roomType}
            </Link>
          );
        })}
      </div>
    </div>
  );
}
