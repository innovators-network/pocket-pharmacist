import {Message} from "./message";

export interface Conversation {
    id: string;
    timestamp: string;
    name: string;
    messages: Message[];
    context?: string;
}
