import {useEffect, useState} from "react";
import {Conversation} from "../types/conversation";
import {ConversationRepository} from "../repositories/abstractions";
import {Message} from "../types/message";
import {ChatbotService, ChatMessage} from "../api/chatbot";

export function useConversationsViewModel(
    repostiory: ConversationRepository,
    chatbotService: ChatbotService
) {

    const [currentConversation, setCurrentConversation] = useState<Conversation | undefined>(undefined);
    const [conversationSelections, setConversationSelections] = useState<Pick<Conversation, "id" | "name">[] | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    function sort(conversations: Conversation[]): Conversation[] {
        return [...conversations].sort((a, b) => b.timestamp.localeCompare(a.timestamp));
    }

    function updateCurrentConversion(messages: Message[], context: any | undefined) {
        console.log("Updating current conversation with context:", context);
        const conversation = currentConversation
        if (!conversation) {
            throw new Error("Current conversation not found");
        }
        if (conversation) {
            console.log("oldContext:", conversation.context)
            console.log("newContent:", context)
            const updatedConversation: Conversation = {
                ...conversation,
                messages: messages,
                context: context
            }
            try {
                repostiory.save(updatedConversation)
                setCurrentConversation(updatedConversation);
            } catch (error) {
                console.error("Error saving conversation:", error);
                setError(`Failed to save conversation. ${error}`);
            }
        }
    }

    async function loadLatestConversation() {
        try {
            const conversations = await repostiory.loadAll();
            if (conversations.length > 0) {
                const sortedConversations = sort(conversations);
                setCurrentConversation(sortedConversations[0]);
            } else {
                setCurrentConversation(undefined);
            }
        } catch (error) {
            console.error("Error loading conversations:", error);
            setError(`Failed to load conversations. ${error}`);
        }
    }

    useEffect(() => {
        startNewConversation()
    }, [])

    const addMessage = (message: Message) => {
        if (!currentConversation) {
            return;
        }
        const updatedConversation = { ...currentConversation, messages: [...currentConversation.messages, message] };
        setCurrentConversation(updatedConversation);
    }

    const startNewConversation = async () => {
        try {
            const conversation = await repostiory.create("Welcome! I’m Pocket Pharmacist. Ask me anything about drugs, interactions, or side effects.");
            setCurrentConversation(conversation)
        } catch (error) {
            console.error("Error starting new conversation:", error);
            setError(`Failed to start new conversation. ${error}`);
        }
    };

    const selectConversation = async (id: string) => {
        try {
            const conversation = await repostiory.load(id);
            if (conversation) {
                setCurrentConversation(conversation);
            } else {
                throw new Error(`Conversation with ID ${id} not found`);
            }
        } catch (error) {
            console.error("Error selecting conversation:", error);
            setError(`Failed to load conversation id: ${id}. ${error}`);
        }
    };

    const sendMessage = async (text: string) => {
        console.log("Sending message:", text);
        const conversation = currentConversation
        if (!conversation) {
            setError("Current conversation not found.");
            return
        }
        const conversationId = conversation.id
        const message: Message = {
            sender: "user",
            text: text,
            timestamp: new Date().toISOString(),
            sequence: conversation.messages.length + 1
        }
        updateCurrentConversion([...conversation.messages, message], conversation.context)
        setLoading(true)
        try {
            const requestChatMessage: ChatMessage = {
                sessionId: conversationId,
                timestamp: message.timestamp,
                text: message.text,
                context: conversation.context
            }
            const responseChatMessage: ChatMessage = await chatbotService.sendMessage(requestChatMessage)
            const responseMessage: Message = {
                sender: "bot",
                text: responseChatMessage.text,
                timestamp: new Date().toISOString(),
                sequence: message.sequence + 1,
            }
            const context = responseChatMessage["context"]
            console.log("Response chat message context:", context);
            updateCurrentConversion([...conversation.messages, message, responseMessage], context)
        } catch (error) {
            console.error("Error sending message:", error);
            setError(`Failed to send message. ${error}`);
        } finally {
            setLoading(false)
        }
    }

    const deleteConversation = async (id: string) => {
        try {
            console.log("Deleting conversation:", id);
            await repostiory.delete(id)
            loadLatestConversation()
        } catch (error) {
            console.error("Error deleting conversation:", error);
            setError(`Failed to delete conversation ${id}. ${error}`);
        }
    }

    const activeConversationSelections = async (activate: boolean) => {
        console.log("Active conversation selections:", activate);
        if (!activate) {
            setConversationSelections(null)
            return;
        }
        try {
            const conversations = await repostiory.loadAll();
            const selections: Pick<Conversation, "id" | "name">[] = conversations.map((conversation) => {
                return {
                    id: conversation.id,
                    name: conversation.name
                };
            });
            setConversationSelections(selections);
        } catch (error) {
            console.error("Error loading conversations:", error);
            setError(`Failed to load conversations. ${error}`);
        }
    }

    const clearError = () => {
        setError(null);
    }

    const clearLoading = () => {
        setLoading(false);
    }

    return {
        currentConversation: currentConversation,
        conversationSelections,
        activeConversationSelections,
        addMessage,
        sendMessage,
        selectConversation,
        deleteConversation,
        startNewConversation,
        loading,
        clearLoading,
        error,
        clearError
    };
}
