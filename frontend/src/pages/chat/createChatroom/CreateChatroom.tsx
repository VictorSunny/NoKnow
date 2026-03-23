import CreateChatroomForm from "../../../components/forms/CreateChatroomForm";
import useSetPageTitle from "../../../hooks/useSetPageTitle";
import { ChatroomPrivatePublicTypes } from "../../../types/chatroomTypes";

export default function CreateChatroom({chatroomType}: {chatroomType: ChatroomPrivatePublicTypes}) {
  const _ = useSetPageTitle(`create ${chatroomType} chatroom`);

  return (
    <div className="page-container create-chatroom-page">
      <div className="section grow">
        <CreateChatroomForm chatroomType={chatroomType} />
      </div>
    </div>
  );
}
