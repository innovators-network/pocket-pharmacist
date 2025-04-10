import axios, {AxiosResponse} from "axios";

export interface ChatMessage {
    sessionId: string;
    timestamp: string;
    text: string;
    language?: string;
    context?: any;
}

export interface ChatbotService {

    sendMessage(chatMessage: ChatMessage): Promise<ChatMessage>;
}

export class AxiosChatbotService implements ChatbotService {

    private baseUrl: string;

    constructor(baseUrl: string = "") {
        this.baseUrl = baseUrl;
    }

    async sendMessage(chatMessage: ChatMessage): Promise<ChatMessage> {
        try {
            const response: AxiosResponse<ChatMessage, ChatMessage> = await axios.post<ChatMessage>(`${this.baseUrl}/api/chat`, chatMessage);
            const responseData = response.data;
            const sessionId = responseData["sessionId"]
            const timestamp = responseData["timestamp"]
            const text = responseData["text"]
            const context = responseData["context"]
            console.log("Response chat message context:", context);
            const responseMessage: ChatMessage = {
                sessionId: sessionId,
                timestamp: timestamp,
                text: text,
                context: context,
            }
            return responseMessage;
        } catch (error) {
            console.error("Error sending message:", error);
            throw error;
        }
    }
}

export class MockChatbotService implements ChatbotService {
    async sendMessage(chatMessage: ChatMessage): Promise<ChatMessage> {
        return new Promise<ChatMessage>((resolve, reject) => {
            setTimeout(() => {
                const response: ChatMessage = {
                    ...chatMessage,
                    text: "This is a mock response to your message: " + chatMessage.text,
                    context: chatMessage.context,
                };
                // resolve(response);
                reject(new Error("Failed to send to Chatbot service"));
            }, 1000);
        });
    }
}