import React from 'react';
import { Newspaper } from 'lucide-react';

const News = ({ articles }) => {
    if (!articles || articles.length === 0) {
        return (
            <div className="bg-gray-800 rounded-xl shadow-lg p-6">
                <h2 className="text-2xl font-semibold mb-6 text-blue-400 flex items-center">
                    <Newspaper className="w-6 h-6 mr-2" />
                    Market News
                </h2>
                <p className="text-gray-400">No news available yet</p>
            </div>
        );
    }

    const recentArticles = articles.slice(0, 5);

    return (
        <div className="bg-gray-800 rounded-xl shadow-lg p-6">
            <h2 className="text-2xl font-semibold mb-6 text-blue-400 flex items-center">
                <Newspaper className="w-6 h-6 mr-2" />
                Market News
            </h2>
            <div className="space-y-4">
                {recentArticles.map((article, index) => {
                    const releaseTime = article.publish_at
                        ? new Date(article.publish_at * 1000).toLocaleString()
                        : new Date(article.datetime).toLocaleString();

                    return (
                        <div
                            key={index}
                            className="bg-gray-700 rounded-lg p-4 border-l-4 border-blue-500 hover:bg-gray-600 transition-all duration-200 hover:translate-x-1"
                        >
                            <h3 className="font-bold text-lg text-white mb-2">{article.headline}</h3>
                            <p className="text-gray-300 text-sm leading-relaxed mb-3">{article.article}</p>
                            <div className="flex justify-between text-xs text-gray-400">
                                <span className="font-semibold text-blue-400">{article.symbol}</span>
                                <span>Released: {releaseTime}</span>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default News;
