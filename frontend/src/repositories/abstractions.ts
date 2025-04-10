import { Conversation } from "../types/conversation";

export interface ConversationRepository {
    getAllKeys(): Promise<string[]>;
    loadAll(): Promise<Conversation[]>;
    load(id: string): Promise<Conversation | undefined>;
    save(conversation: Conversation): Promise<void>;
    delete(id: string): Promise<void>;
    create(greeting?: string): Promise<Conversation>;
}

