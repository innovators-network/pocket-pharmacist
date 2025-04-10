import React, {useEffect, useRef, useState} from "react";
import * as Icons from "react-bootstrap-icons";
import {Button, Container, Dropdown, Form, InputGroup, ListGroup, Spinner, Modal} from "react-bootstrap";
import {useConversationsViewModel} from "../models/viewModels";
import {Message} from "../types/message";
import {ConversationRepository} from "../repositories/abstractions";
import {ChatbotService} from "../api/chatbot";

interface ChatPageProps {
    repository: ConversationRepository;
    chatbotService: ChatbotService;
}

const ChatPage: React.FC<ChatPageProps> = ({ repository, chatbotService}) => {

    const {
        currentConversation,
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
    } = useConversationsViewModel(repository, chatbotService);

    const [input, setInput] = useState<string>('');
    const messagesEndRef = useRef<HTMLDivElement | null>(null);

    useEffect(() => {
        if (messagesEndRef.current) {
            messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
        }
    }, [currentConversation?.messages]);

    const handleStartNewConversation = () => {
        startNewConversation();
    };

    const handleSendMessage = async () => {
        if (input.trim()) {
            await sendMessage(input.trim());
            setInput('');
        }
    };

    const handleSelectConversation = (id: string) => {
        console.log("Selected conversation ID:", id);
        selectConversation(id);
        activeConversationSelections(false);
    };

    const handleDeleteConversation = (id: string | undefined) => {
        if (id) {
            deleteConversation(id);
        }
    }

    function loadingSpinner() {
        return (
            <div
                className="d-flex justify-content-center align-items-center position-absolute top-0 start-0 w-100 h-100"
                style={{ backgroundColor: "rgba(255, 255, 255, 0.8)", zIndex: 10 }}>
                <Spinner animation="border" variant="primary" />
            </div>
        );
    }

    function titleBar() {
        return (
            <h4
                className="text-center flex-grow-0 p-2 m-0 bg-primary bg-gradient text-bg-primary display-7"
                style={{boxShadow: "0 4px 8px rgba(0, 0, 0, 0.1)"}}>
                Pocket Pharmacist
            </h4>
        )
    }

    function menuBar() {
        return (
            <div className="m-1 d-flex justify-content-between align-items-center">
                {dropdownMenu()}
                <div className="text-center flex-grow-1">{currentConversation?.name ?? ""}</div>
                <Icons.PlusLg onClick={handleStartNewConversation} className="me-1"/>
                <Icons.Trash className="me-1" onClick={() => {
                    if (currentConversation) {
                        handleDeleteConversation(currentConversation.id)
                    }
                }}/>
            </div>
        )
    }

    function dropdownMenu() {
        return (
            <Dropdown
                show={conversationSelections !== null}
                onToggle={(show) => activeConversationSelections(show)}
                onClick={() => {
                    activeConversationSelections(conversationSelections === null);
                }}>
                <Icons.ListTask/>
                <Dropdown.Menu>
                    {conversationSelections && conversationSelections.map((selection) => {
                        return (
                            <Dropdown.Item
                                key={selection.id}
                                onClick={() => handleSelectConversation(selection.id)}>
                                <div className="d-flex justify-content-between align-items-center">
                                    <div className="d-flex align-items-center">
                                        {selection.id === currentConversation?.id ? <Icons.CheckSquare/> : <Icons.Square/>}
                                        <span className="ms-2 me-2">{selection.name}</span>
                                    </div>
                                </div>
                            </Dropdown.Item>
                        )
                    })}
                </Dropdown.Menu>
            </Dropdown>
        );
    }

    function conversationBody() {
        const rounded = "4"
        return (
            <ListGroup
                className="flex-grow-1 overflow-auto"
                style={{height: "400px", overflowY: "auto"}}>
                {currentConversation?.messages.map((message: Message) => (
                    <ListGroup.Item
                        key={message.sequence}
                        className="border-0 d-flex p-2">
                        <div
                            className={`p-2 ps-3 pe-3 ${
                                message.sender === "user" ? 
                                    `bg-info  text-bg-info  bg-gradient rounded-0 rounded-top-${rounded} rounded-start-${rounded}` : 
                                    `bg-light text-bg-light bg-gradient rounded-0 rounded-end-${rounded} rounded-top-${rounded}`} ${
                                message.sender === "user" ? "ms-auto" : "me-auto"}
                            `}
                            style={{
                                maxWidth: "75%",
                                border: `${message.sender === "user" ? "1px solid #e0e0e0" : "1px solid #e0e0e0"}`,
                                boxShadow: "0 4px 8px rgba(0, 0, 0, 0.1)",
                            }}>
                            <small className={"p-0 m-0"}>
                                {new Date(message.timestamp).toLocaleDateString() === new Date().toLocaleDateString()
                                    ? new Date(message.timestamp).toLocaleTimeString()
                                    : new Date(message.timestamp).toLocaleString()}
                            </small>
                            <p className={"p-0 m-0"}>{message.text}</p>
                        </div>
                    </ListGroup.Item>))
                }
                <div ref={messagesEndRef} />
            </ListGroup>
        )
    }

    function inputBar() {
        return (
            <Form className="m-0"
                onSubmit={(e) => {
                    e.preventDefault();
                    handleSendMessage();
                }}>
                <InputGroup style={{border: "1px solid lightgray"}}>
                    <Form.Control
                        className={"border-0"}
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Type your query..."/>
                    <Button variant="light" onClick={handleSendMessage}>
                        <Icons.SendArrowUp/>
                    </Button>
                </InputGroup>
            </Form>
        )
    }

    function errorDialog() {
        return (
            <Modal show={!!error} onHide={clearError} centered>
                <Modal.Header closeButton>
                    <Modal.Title>Error</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <p>{error}</p>
                </Modal.Body>
                <Modal.Footer>
                    <Button variant="primary" onClick={clearError}>
                        OK
                    </Button>
                </Modal.Footer>
            </Modal>
        );
    }

    return (
        <Container
            className="d-flex flex-column vh-100 p-1"
            style={{maxWidth: "400px", border: "1px solid lightgray"}}>
            {loading && loadingSpinner()}
            {error && errorDialog()}
            {titleBar()}
            {menuBar()}
            {conversationBody()}
            {inputBar()}
        </Container>
    );
};

export default ChatPage;
