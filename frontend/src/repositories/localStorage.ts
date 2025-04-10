import { ConversationRepository } from "./abstractions";
import { v4 as uuidv4 } from "uuid";
import { Message } from "../types/message";
import { Conversation } from "../types/conversation";

export class LocalStorageConversationRepository implements ConversationRepository {
    private storageKeyPrefix = "conversation_";

    async getAllKeys(): Promise<string[]> {
        const keys: string[] = [];
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key && key.startsWith(this.storageKeyPrefix)) {
                keys.push(key);
            }
        }
        return keys
    }

    async loadAll(): Promise<Conversation[]> {
        const keys =await this.getAllKeys();
        const conversations: Conversation[] = [];
        for (const key of keys) {
            const data = localStorage.getItem(key);
            if (data) {
                const conversation: Conversation = JSON.parse(data);
                conversations.push(conversation);
            }
        }
        return conversations;
    }

    async load(id: string): Promise<Conversation | undefined> {
        const data = localStorage.getItem(this.storageKeyPrefix + id);
        if (data) {
            return JSON.parse(data);
        }
        return undefined;
    }

    async save(conversation: Conversation): Promise<void> {
        const id = conversation.id;
        localStorage.setItem(this.storageKeyPrefix + id, JSON.stringify(conversation));
    }

    async create(greeting?: String): Promise<Conversation> {
        const time = new Date();
        const greetingMessage: Message | undefined = greeting !== undefined ? {
            sender: "bot",
            text: greeting,
            timestamp: time.toISOString(),
            sequence: 0,
        } as Message : undefined
        const conversation: Conversation = {
            id: uuidv4(),
            timestamp: time.toISOString(),
            name: time.toLocaleString(),
            messages: greetingMessage ? [greetingMessage] : [],
        };
        await this.save(conversation);
        return conversation;
    }

    async delete(id: string): Promise<void> {
        localStorage.removeItem(this.storageKeyPrefix + id);
    }
}