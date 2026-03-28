import useSetPageTitle from "../../hooks/useSetPageTitle";
import "./Guide.css";

export default function Guide() {
  const _ = useSetPageTitle("guide");
  return (
    <div className="page-container guide-page-container">
      <div className="section">
        <h1 className="title">NoKnow</h1>
        <p>A web app for easy animate messaging with, no signup required</p>
      </div>
      <div className="section">
        <h2 className="title">User</h2>
        <div className="sub-section">
          <p>
            User is either a guest, or signed in
            <br />
            Signed in users can choose to stay hidden and use anonymous usernames when engaging in
            chats
          </p>
          <p>
            On signup, user must provide a valid email which will be confirmed via OTP verification.
          </p>
          <p>User can activate two factor authentication for future logins to be OTP protected.</p>
        </div>
        <div className="sub-section">
          <ul>
            <h3>Guest user</h3>
            <li>create and engage public chatrooms only</li>
            <li>switch anonymous username.</li>
          </ul>
          <ul>
            <h3>Signed in user</h3>
            <li>Create and engage public chatrooms, as well as private chatrooms</li>
            <li>Switch anonymous username.</li>
            <li>Send, recieve, accept, and reject friend requests</li>
            <li>View sent friend requests</li>
            <li>Update bio information, email, username, and password</li>
            <li>Recover account via email if password is forgotten</li>
            <li>Choose stay hidden like a guest</li>
            <li>
              In `hidden` status, all messages sent in private and public chatrooms will use set
              anonymous username except for friend chats
            </li>
            <li>
              In `hidden` status, user cannot be seen by fellow chatroom members except for
              moderators and chatroom creator
            </li>
          </ul>
        </div>
      </div>
      <div className="section">
        <h2 className="title">Chat</h2>
        <div className="sub-section">
          There are three type of chats namely; Public chatroom, private chatroom, and personal
          chatroom(for friends).
          <br />
          Public chatrooms can be created and engaged with no signup required.
          <br />
          Private chatroooms require user to be signed. To engaged a private chatroom, user must
          first join by providing the correct password for the chatroom.
          <br />
          Friend/Personal chatrooms require user to be signed in. user can only engage another user
          in personal chat if they are already friends.
          <br />
          All users, anonymous and signed in, can create only 3 chatrooms per hour.
          <br />
          Message broadcasts are sent to chat on certain events e.g user leaves chatroom, user
          becomes a moderator, etc.
        </div>
        <div className="sub-section">
          <ul>
            <h3>Public chatroom</h3>
            <li>Standard messaging</li>
            <li>No login required to create and engage</li>
            <li>Members and non members can engage. Free for all.</li>
            <li>Join and leave chatroom if signed in</li>
            <li>Users cannot be added or removed</li>
            <li>The chatroom creator cannot assign moderators</li>
            <li>
              if logged in, user who creates chatroom automatically becomes creator and member
            </li>
          </ul>

          <ul>
            <h3>Private chatroom</h3>
            <li>Standard messaging</li>
            <li>Login required to create and engaged</li>
            <li>Only members can engaged</li>
            <li>Password required to join and create</li>
            <li>User who creates chatroom automatically becomes creator and member</li>
            <li>
              Messages recording can be turned off (`secret mode`) to stop messages being saved in
              the database for extra privacy
            </li>
            <li>
              `Secret mode` is turned off automatically after the last active user in chatroom
              disconnects
            </li>
            <li>The chatroom creator can make members into moderators</li>
            <li>
              Only the chatroom creator can remove moderators. a moderator cannot remove a moderator
            </li>
            <li>The chatroom creator and moderators can add their friends to members</li>
            <li>The chatroom creator and moderators can remove members</li>
            <li>Chatroom can have a maximum of nine (9) moderators, plus creator (10 in total)</li>
            <li>
              Removing a member automatically bans them from re-entering chatroom even with password
              provided until they are re-added/unbanned by a moderator or creator
            </li>
            <li>
              Removed users are banned and restricted from joining chatroom unless re-added by a
              moderator or creator
            </li>
            <li>
              The chatroom creator cannot leave chatroom without assigning a successor first only a
              moderator can be made into a successor
            </li>
            <li>
              Unlike the creator, the successor is allowed to leave the chatroom. on leaving, they
              forfeit the role of successor
            </li>
            <li>
              If a successor is demoted from moderator to regular member, they automatically lose
              the title of successor
            </li>
            <li>
              When creator leaves chatroom, the successor automatically gets assigned the role of
              creator along with all privileges attached
            </li>
            <li>
              Chatroom members can view fellow members except for those with their `hidden` status
              active
            </li>
            <li>
              Members with `hidden` status active can be viewed only by moderators and creator
            </li>
          </ul>

          <ul>
            <h3>Friend chat</h3>
            <li>Standard messaging</li>
            <li>Login required to engage</li>
            <li>Only 2 members can engage; User and friend</li>
            <li>Second-party user must currently be a friend to be engaged</li>
            <li>
              Messages recording can be turned off (secret mode) to stop messages being saved in the
              database for extra privacy
            </li>
            <li>
              Secret mode is turned off automatically after the last active user in chatroom
              disconnects
            </li>
            <li>Chat history can be deleted for both parties</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
