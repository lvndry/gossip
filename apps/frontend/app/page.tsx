'use client';

import { ChevronLeft, ChevronRight, Search, Sparkles, User } from "lucide-react";
import NextImage from "next/image";
import { useEffect, useRef, useState } from "react";

interface Article {
  title: string;
  url: string;
  source: string;
  description?: string;
  categories?: string[];
  image_url?: string;
  publication_date?: string;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  text: string;
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [articles, setArticles] = useState<Article[]>([]);
  const [loadingArticles, setLoadingArticles] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const showResults = messages.length > 0;

  // Fetch articles on mount
  useEffect(() => {
    async function fetchArticles() {
      try {
        const response = await fetch('/api/articles');
        const data = await response.json();
        if (data.status === 'success' && data.articles) {
          setArticles(data.articles);
        }
      } catch (error) {
        console.error('Error fetching articles:', error);
      } finally {
        setLoadingArticles(false);
      }
    }
    fetchArticles();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const sources = messages
    .filter(m => m.role === 'assistant')
    .flatMap(() => {
      const sourceMap = new Map<string, number>();
      articles.forEach(article => {
        sourceMap.set(article.source, (sourceMap.get(article.source) || 0) + 1);
      });
      return Array.from(sourceMap.entries()).map(([source, count]) => ({ source, count }));
    });

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      text: input,
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: input }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data = await response.json();
      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        text: data.answer,
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        text: 'Sorry, I encountered an error. Please try again.',
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }

  function handleArticleClick(article: Article) {
    setInput(article.title);
    inputRef.current?.focus();
  }

  function handleNewSearch() {
    setInput('');
    inputRef.current?.focus();
  }

  return (
    <div className="flex min-h-screen flex-col bg-white dark:bg-black">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-800">
        <div className="flex items-center gap-2">
          <Sparkles className="h-6 w-6 text-gray-900 dark:text-white" />
          <span className="text-xl font-semibold text-gray-900 dark:text-white">Gossip 🤗</span>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex flex-col">
        {!showResults ? (
          <div className="flex-1 flex flex-col items-center justify-center px-4 py-12">
            <div className="w-full max-w-4xl space-y-8">
              <div className="text-center space-y-2">
                <h1 className="text-4xl md:text-5xl font-semibold text-gray-900 dark:text-white">
                  What are you curious about ? 👀
                </h1>
              </div>

              <form onSubmit={handleSubmit} className="relative">
                <div className="relative flex items-center">
                  <Search className="absolute left-4 h-5 w-5 text-gray-400 pointer-events-none" />
                  <input
                    ref={inputRef}
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Search..."
                    className="w-full pl-12 pr-4 py-4 text-lg border border-gray-300 dark:border-gray-700 rounded-2xl bg-white dark:bg-gray-900 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-gray-900 dark:focus:ring-white focus:border-transparent transition-all"
                    onKeyDown={(event) => {
                      if (event.key === 'Enter' && !event.shiftKey) {
                        event.preventDefault();
                        handleSubmit(event as unknown as React.FormEvent<HTMLFormElement>);
                      }
                    }}
                  />
                </div>
              </form>

              {/* Articles Grid */}
              <div className="space-y-4">
                <h2 className="text-lg font-medium text-gray-700 dark:text-gray-300">Recent Articles</h2>
                {loadingArticles ? (
                  <div className="text-center py-8 text-gray-500">Loading articles...</div>
                ) : articles.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {articles.map((article, index) => (
                      <button
                        key={index}
                        onClick={() => handleArticleClick(article)}
                        className="group text-left p-4 border border-gray-200 dark:border-gray-800 rounded-xl hover:border-gray-300 dark:hover:border-gray-700 hover:shadow-md transition-all bg-white dark:bg-gray-900"
                      >
                        {article.image_url && (
                          <div className="mb-3 overflow-hidden rounded-lg relative h-32">
                            <NextImage
                              src={article.image_url}
                              alt={article.title}
                              fill
                              className="object-cover group-hover:scale-105 transition-transform"
                            />
                          </div>
                        )}
                        <div className="space-y-2">
                          <div className="flex items-center gap-2">
                            <span className="text-xs px-2 py-1 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400">
                              {article.source}
                            </span>
                          </div>
                          <h3 className="font-medium text-gray-900 dark:text-white line-clamp-2 group-hover:text-gray-700 dark:group-hover:text-gray-300">
                            {article.title}
                          </h3>
                          {article.description && (
                            <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
                              {article.description}
                            </p>
                          )}
                        </div>
                      </button>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-500">No articles available</div>
                )}
              </div>
            </div>
          </div>
        ) : (
          /* Results View with Sidebar */
          <div className="flex-1 flex">
            {/* Main Content Area */}
            <div className={`flex-1 flex flex-col transition-all ${sidebarOpen ? 'mr-0 md:mr-80' : 'mr-0'}`}>
              <div className="max-w-4xl mx-auto w-full px-4 py-8">
                {/* Search Bar at Top */}
                <div className="mb-6">
                  <form onSubmit={handleSubmit} className="relative">
                    <div className="relative flex items-center">
                      <Search className="absolute left-4 h-5 w-5 text-gray-400 pointer-events-none" />
                      <input
                        ref={inputRef}
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Search..."
                        className="w-full pl-12 pr-4 py-3 text-base border border-gray-300 dark:border-gray-700 rounded-xl bg-white dark:bg-gray-900 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-gray-900 dark:focus:ring-white focus:border-transparent transition-all"
                        onKeyDown={(e) => {
                          if (e.key === 'Enter' && !e.shiftKey) {
                            e.preventDefault();
                            handleSubmit(e as unknown as React.FormEvent<HTMLFormElement>);
                          }
                        }}
                      />
                      <button
                        type="button"
                        onClick={handleNewSearch}
                        className="absolute right-4 text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200"
                      >
                        New Search
                      </button>
                    </div>
                  </form>
                </div>

                {/* Messages */}
                <div className="flex-1 overflow-y-auto space-y-6 pb-8">
                  {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex gap-4 ${
                      message.role === 'user' ? 'justify-end' : 'justify-start'
                    }`}
                  >
                    {message.role === 'assistant' && (
                      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gray-900 dark:bg-white">
                        <Sparkles className="h-4 w-4 text-white dark:text-gray-900" />
                      </div>
                    )}
                    <div
                      className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                        message.role === 'user'
                          ? 'bg-gray-900 text-white dark:bg-gray-100 dark:text-gray-900'
                          : 'bg-gray-100 text-gray-900 dark:bg-gray-800 dark:text-gray-100'
                      }`}
                    >
                      <div className="prose prose-sm dark:prose-invert max-w-none">
                        <p className="whitespace-pre-wrap leading-relaxed">
                          {message.text}
                        </p>
                      </div>
                      </div>
                    {message.role === 'user' && (
                      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gray-200 dark:bg-gray-700">
                        <User className="h-4 w-4 text-gray-600 dark:text-gray-300" />
                      </div>
                    )}
                  </div>
                ))}

                  {isLoading && (messages.length === 0 || messages[messages.length - 1]?.role === 'user') && (
                    <div className="flex gap-4 justify-start">
                      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gray-900 dark:bg-white">
                        <Sparkles className="h-4 w-4 text-white dark:text-gray-900" />
                      </div>
                      <div className="bg-gray-100 dark:bg-gray-800 rounded-2xl px-4 py-3">
                        <div className="flex gap-1">
                          <div className="h-2 w-2 rounded-full bg-gray-400 dark:bg-gray-500 animate-bounce" style={{ animationDelay: '0ms' }}></div>
                          <div className="h-2 w-2 rounded-full bg-gray-400 dark:bg-gray-500 animate-bounce" style={{ animationDelay: '150ms' }}></div>
                          <div className="h-2 w-2 rounded-full bg-gray-400 dark:bg-gray-500 animate-bounce" style={{ animationDelay: '300ms' }}></div>
                        </div>
                      </div>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </div>
              </div>
            </div>

            {/* Sidebar */}
            <div
              className={`fixed right-0 top-16 bottom-0 w-80 bg-gray-50 dark:bg-gray-900 border-l border-gray-200 dark:border-gray-800 transition-transform ${
                sidebarOpen ? 'translate-x-0' : 'translate-x-full'
              } hidden md:block`}
            >
              <div className="h-full flex flex-col p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Sources</h3>
                  <button
                    onClick={() => setSidebarOpen(!sidebarOpen)}
                    className="p-1 hover:bg-gray-200 dark:hover:bg-gray-800 rounded transition-colors"
                  >
                    <ChevronRight className="h-5 w-5 text-gray-600 dark:text-gray-400" />
                  </button>
                </div>
                <div className="space-y-3">
                  {sources.length > 0 ? (
                    sources.map(({ source, count }, index) => (
                      <div
                        key={index}
                        className="p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-medium text-gray-900 dark:text-white">{source}</span>
                          <span className="text-sm text-gray-500 dark:text-gray-400">{count} articles</span>
                        </div>
                      </div>
                    ))
                  ) : (
                    <p className="text-sm text-gray-500 dark:text-gray-400">No sources yet. Ask a question to see sources.</p>
                  )}
                </div>
              </div>
            </div>

            {!sidebarOpen && (
              <button
                onClick={() => setSidebarOpen(true)}
                className="fixed right-4 top-24 p-2 bg-gray-900 dark:bg-white text-white dark:text-gray-900 rounded-lg shadow-lg hover:bg-gray-800 dark:hover:bg-gray-100 transition-colors hidden md:block"
              >
                <ChevronLeft className="h-5 w-5" />
              </button>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
