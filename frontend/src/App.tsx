import React from 'react';
import ChatPage from './pages/ChatPage';
import {LocalStorageConversationRepository} from "./repositories/localStorage";
import {ConversationRepository} from "./repositories/abstractions";
import {AxiosChatbotService, ChatbotService, MockChatbotService} from "./api/chatbot";

const App: React.FC = () => {
    const repository: ConversationRepository = new LocalStorageConversationRepository()
    const chatbotService: ChatbotService = new AxiosChatbotService();
    return (
        <ChatPage repository={repository} chatbotService={chatbotService}/>
    )
}

export default App;
