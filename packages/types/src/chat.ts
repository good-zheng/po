export type ChatMessage = {
  role: string;
  content: string;
};

export type ChatRequestParams = {
  messages: ChatMessage[];
};

export type ChatInFrame = {
  type: "message" | "ping";
  content?: string;
};

export type ChatWSFrame = {
  type: "token" | "done" | "pong" | "error";
  content?: string;
};
