import { MessageListResponse } from "../schemas/ChatSchemas";

export default function getMessagesLength(messagesPages: MessageListResponse[]): number {
  let total = 0;
  messagesPages.map((page) => {
    total += page.messages.length;
  });
  return total;
}
