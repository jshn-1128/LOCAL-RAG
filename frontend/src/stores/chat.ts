import { create } from "zustand";
import type { ChatMessage, Conversation } from "@/types";

interface ChatState {
  conversations: Conversation[];
  activeConversationId: string | null;
  isStreaming: boolean;
  streamingContent: string;
  setConversations: (conversations: Conversation[]) => void;
  setActiveConversation: (id: string | null) => void;
  addConversation: (conversation: Conversation) => void;
  addMessage: (conversationId: string, message: ChatMessage) => void;
  setIsStreaming: (isStreaming: boolean) => void;
  setStreamingContent: (content: string) => void;
  appendStreamingContent: (content: string) => void;
  removeConversation: (id: string) => void;
  updateConversationId: (oldId: string, newId: string) => void;
}

export const useChatStore = create<ChatState>()((set) => ({
  conversations: [],
  activeConversationId: null,
  isStreaming: false,
  streamingContent: "",

  setConversations: (conversations) =>
    set((state) => {
      const backendIds = new Set(conversations.map((c) => c.id));
      const merged = conversations.map((backendConv) => {
        const existing = state.conversations.find(
          (c) => c.id === backendConv.id,
        );
        return existing
          ? { ...backendConv, messages: existing.messages }
          : backendConv;
      });
      const preserved = state.conversations.filter(
        (c) => !backendIds.has(c.id) && c.messages.length > 0,
      );
      return { conversations: [...merged, ...preserved] };
    }),
  setActiveConversation: (id) => set({ activeConversationId: id }),
  addConversation: (conversation) =>
    set((state) => ({
      conversations: [conversation, ...state.conversations],
      activeConversationId: conversation.id,
    })),
  addMessage: (conversationId, message) =>
    set((state) => ({
      conversations: state.conversations.map((c) =>
        c.id === conversationId
          ? { ...c, messages: [...c.messages, message] }
          : c,
      ),
    })),
  setIsStreaming: (isStreaming) => set({ isStreaming }),
  setStreamingContent: (content) => set({ streamingContent: content }),
  appendStreamingContent: (content) =>
    set((state) => ({
      streamingContent: state.streamingContent + content,
    })),
  removeConversation: (id) =>
    set((state) => ({
      conversations: state.conversations.filter((c) => c.id !== id),
      activeConversationId:
        state.activeConversationId === id ? null : state.activeConversationId,
    })),
  updateConversationId: (oldId, newId) =>
    set((state) => ({
      conversations: state.conversations.map((c) =>
        c.id === oldId ? { ...c, id: newId } : c,
      ),
      activeConversationId:
        state.activeConversationId === oldId
          ? newId
          : state.activeConversationId,
    })),
}));
