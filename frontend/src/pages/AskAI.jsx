import { useEffect, useRef, useState } from 'react';
import { useIsFetching, useQuery } from '@tanstack/react-query';
import { Icon } from '../components.jsx';
import { postJson } from '../helpers.js';
import './AskAI.css';

// Sends questions to /api/chatwith_ai and caches each answer by question, so repeats are instant.

const SUGGESTED_QUESTIONS = [
    'Which role has the most postings?',
    'Which skill is most in demand?',
    'Where are most internships located?',
    'How many jobs were posted in the last 10 days?',
];

// Normalises a question into a cache key, ignoring case and punctuation differences.
function makeCacheKey(question) {
    let key = question.trim().toLowerCase();

    // Replace repeated spaces with a single space.
    key = key.split(/\s+/).join(' ');

    // Remove question marks at the end.
    while (key.endsWith('?')) {
        key = key.slice(0, -1).trim();
    }

    return key;
}

// Sends one question to the backend and returns the answer; errors are thrown so they are not cached.
async function fetchAnswer(question) {
    const result = await postJson('/api/chatwith_ai', { question: question });

    if (result.answer) {
        return result.answer;
    }
    if (result.error) {
        throw new Error(result.error);
    }
    throw new Error('The AI did not return an answer. Please try again.');
}

function AskAI() {
    // The conversation only stores the questions; each answer is loaded by AnswerMessage.
    const [questions, setQuestions] = useState([]);
    const [input, setInput] = useState('');
    const bottomRef = useRef(null);

    // Number of Ask AI requests still waiting for the backend.
    const waitingCount = useIsFetching({ queryKey: ['askAI'] });
    const isWaiting = waitingCount > 0;

    // Keep the newest message in view.
    useEffect(() => {
        if (bottomRef.current) {
            bottomRef.current.scrollIntoView({ behavior: 'smooth', block: 'end' });
        }
    }, [questions, isWaiting]);

    function askQuestion(question) {
        const cleanQuestion = question.trim();
        if (cleanQuestion === '' || isWaiting) {
            return;
        }

        const newQuestions = [...questions];
        newQuestions.push(cleanQuestion);
        setQuestions(newQuestions);
        setInput('');
    }

    function handleSubmit(event) {
        event.preventDefault();
        askQuestion(input);
    }

    // Enter sends the message, Shift + Enter adds a new line.
    function handleKeyDown(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            askQuestion(input);
        }
    }

    // Starts a new conversation. Cached answers are kept by React Query.
    function startNewConversation() {
        setQuestions([]);
    }

    return (
        <div className="ask-page">
            <div className="ask-header">
                <div>
                    <h1 className="page-title">Ask AI</h1>
                    <p className="page-description">Ask questions about the internship market.</p>
                </div>
                {questions.length > 0 && (
                    <button className="btn btn-outline" onClick={startNewConversation} disabled={isWaiting}>
                        New conversation
                    </button>
                )}
            </div>

            <div className="ask-thread">
                {questions.length === 0 && (
                    <div className="ask-start">
                        <p className="ask-start-title">Start with a question</p>
                        <div className="ask-suggestions">
                            {SUGGESTED_QUESTIONS.map((question) => (
                                <button
                                    key={question}
                                    className="ask-suggestion"
                                    onClick={() => askQuestion(question)}
                                >
                                    {question}
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                {questions.map((question, index) => (
                    <div key={index} className="ask-exchange">
                        <div className="message message-user">
                            <div className="message-bubble">
                                <p>{question}</p>
                            </div>
                        </div>
                        <AnswerMessage question={question} />
                    </div>
                ))}

                <div ref={bottomRef} />
            </div>

            <form className="ask-input" onSubmit={handleSubmit}>
                <textarea
                    rows={1}
                    placeholder="Ask a question about the market"
                    value={input}
                    onChange={(event) => setInput(event.target.value)}
                    onKeyDown={handleKeyDown}
                />
                <button
                    className="btn btn-primary ask-send"
                    type="submit"
                    disabled={input.trim() === '' || isWaiting}
                    aria-label="Send"
                >
                    <Icon name="send" size={18} />
                </button>
            </form>
            <p className="ask-note">
                Answers are generated by AI from InternIQ data and may be inaccurate. Check postings before applying.
            </p>
        </div>
    );
}

// Loads and shows the answer to one question.
function AnswerMessage({ question }) {
    const answerQuery = useQuery({
        queryKey: ['askAI', makeCacheKey(question)],
        queryFn: () => fetchAnswer(question),
        staleTime: Infinity,   // a saved answer never needs to be fetched again
        retry: false,          // AI calls are slow; let the user decide to ask again
    });

    if (answerQuery.isPending) {
        return (
            <div className="message message-assistant">
                <span className="message-author">InternIQ</span>
                <div className="message-bubble message-thinking">
                    <span className="spinner" />
                    Thinking...
                </div>
            </div>
        );
    }

    if (answerQuery.isError) {
        return (
            <div className="message message-assistant message-error">
                <span className="message-author">InternIQ</span>
                <div className="message-bubble">
                    <p>{answerQuery.error.message}</p>
                </div>
            </div>
        );
    }

    // isFetchedAfterMount is false when the answer came from the cache.
    const isSavedAnswer = !answerQuery.isFetchedAfterMount;

    return (
        <div className="message message-assistant">
            <span className="message-author">InternIQ</span>
            <div className="message-bubble">
                <p>{answerQuery.data}</p>
                {isSavedAnswer && <p className="message-source">Saved answer from an earlier question</p>}
            </div>
        </div>
    );
}

export default AskAI;
