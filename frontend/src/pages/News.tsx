import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Newspaper, RefreshCw, AlertCircle, ExternalLink, Filter } from 'lucide-react';
import { fetchNews } from '../api/client';

export const News: React.FC = () => {
  const [articles, setArticles] = useState<any[]>([]);
  const [sentimentFilter, setSentimentFilter] = useState<string>('all');
  const [loading, setLoading] = useState<boolean>(true);
  const [refreshing, setRefreshing] = useState<boolean>(false);
  const [disclaimer, setDisclaimer] = useState<string>('');

  const loadArticles = async (refresh: boolean = false) => {
    if (refresh) setRefreshing(true);
    else setLoading(true);
    try {
      const res = await fetchNews({
        sentiment: sentimentFilter !== 'all' ? sentimentFilter : undefined,
        refresh
      });
      setArticles(res.articles || []);
      setDisclaimer(res.disclaimer || '');
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadArticles();
  }, [sentimentFilter]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-xs transition-colors">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <Newspaper className="w-6 h-6 text-emerald-600 dark:text-emerald-400" />
              <h1 className="text-xl font-bold text-slate-900 dark:text-white tracking-tight">Market News & Sentiment Radar</h1>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              Aggregated from public RSS feeds (Mint, ET, Business Standard) with open-source linguistic NLP sentiment analysis.
            </p>
          </div>

          <button
            onClick={() => loadArticles(true)}
            disabled={refreshing}
            className="flex items-center gap-1.5 px-3.5 py-2 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white rounded-lg text-xs font-semibold shadow-xs transition-colors self-start sm:self-auto"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? 'animate-spin' : ''}`} />
            <span>{refreshing ? 'Polling RSS...' : 'Poll Live RSS'}</span>
          </button>
        </div>

        {/* Sentiment Filter Tabs */}
        <div className="flex items-center gap-2 mt-5 pt-4 border-t border-slate-100 dark:border-slate-800">
          <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 mr-2">Filter Sentiment:</span>
          {['all', 'Positive', 'Neutral', 'Negative'].map((s) => (
            <button
              key={s}
              onClick={() => setSentimentFilter(s)}
              className={`px-3 py-1 text-xs font-semibold rounded-md transition-colors ${
                sentimentFilter === s
                  ? 'bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900'
                  : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'
              }`}
            >
              {s === 'all' ? 'All Articles' : s}
            </button>
          ))}
        </div>
      </div>

      {/* Articles Feed */}
      <div className="space-y-3">
        {loading ? (
          <div className="flex items-center justify-center p-12">
            <div className="w-6 h-6 border-2 border-emerald-600 border-t-transparent rounded-full animate-spin"></div>
          </div>
        ) : articles.length === 0 ? (
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-12 text-center text-xs text-slate-500 dark:text-slate-400">
            No news articles found for this filter. Click "Poll Live RSS" to fetch latest feeds.
          </div>
        ) : (
          articles.map((item) => {
            const isPos = item.sentiment === 'Positive';
            const isNeg = item.sentiment === 'Negative';

            return (
              <div
                key={item.id}
                className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-xs hover:border-emerald-300 dark:hover:border-emerald-700 transition-colors"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="space-y-1.5 flex-1">
                    <div className="flex items-center gap-2">
                      <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">{item.source}</span>
                      <span className="text-slate-300 dark:text-slate-700">•</span>
                      <span className="text-[11px] text-slate-400">{new Date(item.published_at).toLocaleDateString()}</span>
                      {item.related_stock && (
                        <Link
                          to={`/stocks/${item.related_stock}`}
                          className="px-2 py-0.5 rounded bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 text-[10px] font-bold hover:bg-emerald-100 dark:hover:bg-emerald-900/60"
                        >
                          {item.related_stock}
                        </Link>
                      )}
                    </div>

                    <a
                      href={item.url}
                      target="_blank"
                      rel="noreferrer"
                      className="font-bold text-sm text-slate-900 dark:text-white hover:text-emerald-600 dark:hover:text-emerald-400 flex items-center gap-1.5 group"
                    >
                      <span>{item.title}</span>
                      <ExternalLink className="w-3.5 h-3.5 text-slate-400 group-hover:text-emerald-600 dark:group-hover:text-emerald-400" />
                    </a>

                    {item.summary && (
                      <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed pt-1">
                        {item.summary}
                      </p>
                    )}
                  </div>

                  {/* Sentiment Badge */}
                  <div className="text-right shrink-0">
                    <span className={`px-2.5 py-1 text-xs font-bold rounded-md block ${
                      isPos 
                        ? 'bg-emerald-100 dark:bg-emerald-950/80 text-emerald-800 dark:text-emerald-300' 
                        : (isNeg 
                          ? 'bg-rose-100 dark:bg-rose-950/80 text-rose-800 dark:text-rose-300' 
                          : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300')
                    }`}>
                      {item.sentiment}
                    </span>
                    <span className="text-[10px] text-slate-400 block mt-1">
                      Score: {item.sentiment_score > 0 ? '+' : ''}{item.sentiment_score}
                    </span>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>

      <div className="p-3 bg-slate-50 dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-lg text-xs text-slate-500 dark:text-slate-400 flex items-center gap-2">
        <AlertCircle className="w-4 h-4 text-slate-400 shrink-0" />
        <span>{disclaimer}</span>
      </div>
    </div>
  );
};
