import { useEffect, useRef, useState } from 'react';
import { useIsFetching, useQuery } from '@tanstack/react-query';
import { PageLayout } from '../components.jsx';
import { postJson } from '../helpers.js';

const SUGGESTED_QUESTIONS = [
    'Which role has the most postings?',
    'Which skill should I learn first?',
    'Where are most jobs located?',
    'How many jobs were posted in the last 10 days?',
];

// cache key for a question
function makeCacheKey(question) {
    let key = question.trim().toLowerCase();
    key = key.split(/\s+/).join(' ');
    while (key.endsWith('?')) {
        key = key.slice(0, -1).trim();
    }
    return key;
}

// fetch the answer from the ai
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

function AskAI({ questionFromOverview }) {
    // questions in the conversation
    const [questions, setQuestions] = useState([]);
    const [input, setInput] = useState('');
    const bottomRef = useRef(null);
    const lastOverviewQuestionId = useRef(null);

    // answers still loading
    const waitingCount = useIsFetching({ queryKey: ['askAI'] });
    const isWaiting = waitingCount > 0;

    // add the question sent from the overview
    useEffect(() => {
        if (questionFromOverview === null) {
            return;
        }
        if (questionFromOverview.id === lastOverviewQuestionId.current) {
            return;
        }
        lastOverviewQuestionId.current = questionFromOverview.id;
        setQuestions((current) => [...current, questionFromOverview.text]);
    }, [questionFromOverview]);

    // keep the newest message in view
    useEffect(() => {
        if (bottomRef.current) {
            bottomRef.current.scrollIntoView({ block: 'end' });
        }
    }, [questions, isWaiting]);

    function askQuestion(question) {
        const cleanQuestion = question.trim();
        if (cleanQuestion === '' || isWaiting) {
            return;
        }
        setQuestions((current) => [...current, cleanQuestion]);
        setInput('');
    }

    function handleSubmit(event) {
        event.preventDefault();
        askQuestion(input);
    }

    const sidebar = (
        <div className="filter-group">
            <span className="filter-label">Try asking</span>
            <div className="question-list">
                {SUGGESTED_QUESTIONS.map((question) => (
                    <button
                        key={question}
                        className="suggestion suggestion-block"
                        disabled={isWaiting}
                        onClick={() => askQuestion(question)}
                    >
                        {question}
                    </button>
                ))}
            </div>
        </div>
    );

    return (
        <PageLayout
            title="Ask AI"
            description="Ask about roles, skills, salaries and locations. Answers use InternIQ data."
            sidebar={sidebar}
            sidebarTitle="Questions"
        >
            <section className="panel chat">
                <div className="chat-thread">
                    {questions.length === 0 && (
                        <div className="chat-empty">
                            <strong>Ask your first question</strong>
                            <span>Type below, or pick a question from the list.</span>
                        </div>
                    )}

                    {questions.map((question, index) => (
                        <div key={index} className="exchange">
                            <p className="bubble bubble-user">{question}</p>
                            <Answer question={question} />
                        </div>
                    ))}

                    <div ref={bottomRef} />
                </div>

                <form className="ask-form chat-input" onSubmit={handleSubmit}>
                    <label htmlFor="chat-question" className="sr-only">Your question</label>
                    <input
                        id="chat-question"
                        placeholder="Ask a question about jobs or skills"
                        value={input}
                        onChange={(event) => setInput(event.target.value)}
                    />
                    <button className="btn btn-primary" type="submit" disabled={input.trim() === '' || isWaiting}>
                        Ask
                    </button>
                </form>
                <p className="chat-note">Answers come from InternIQ data and can be wrong. Check the posting before you apply.</p>
            </section>
        </PageLayout>
    );
}

// answer bubble
function Answer({ question }) {
    const { data, isPending, isError, error } = useQuery({
        queryKey: ['askAI', makeCacheKey(question)],
        queryFn: () => fetchAnswer(question),
        staleTime: Infinity,   // keep saved answers
        retry: false,          // do not retry slow ai calls
    });

    if (isPending) {
        return (
            <p className="bubble bubble-ai bubble-wait">
                <span className="spinner" />
                Thinking
            </p>
        );
    }

    if (isError) {
        return <p className="bubble bubble-ai bubble-muted">{error.message}</p>;
    }

    return <p className="bubble bubble-ai">{data}</p>;
}

export default AskAI;
