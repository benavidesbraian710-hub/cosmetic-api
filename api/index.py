from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import jieba
import re
from datetime import datetime
import os

app = FastAPI(title="化妆品文章智能检索API", version="1.0.0")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库路径（Vercel环境）
DB_PATH = os.path.join(os.path.dirname(__file__), "cosmetic_articles.db")

# 数据模型
class Article(BaseModel):
    id: int
    title: str
    url: str
    wechat_name: str
    publish_date: str
    summary: Optional[str] = None
    keywords: Optional[str] = None
    match_reason: Optional[str] = None
    score: Optional[float] = None

class SearchRequest(BaseModel):
    query: str
    limit: int = 50
    offset: int = 0

class SearchResponse(BaseModel):
    total: int
    articles: List[Article]
    query: str
    took_ms: int

# 数据库连接
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# 关键词提取
def extract_keywords(query: str) -> List[str]:
    words = jieba.lcut(query)
    stopwords = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'}
    keywords = [w for w in words if len(w) > 1 and w not in stopwords]
    return keywords

# 生成匹配理由
def generate_match_reason(article: dict, query_keywords: List[str]) -> str:
    matched = []
    text = f"{article['title']} {article['summary'] or ''} {article['keywords'] or ''}".lower()
    
    for kw in query_keywords:
        if kw.lower() in text:
            matched.append(kw)
    
    if matched:
        unique_matched = list(dict.fromkeys(matched))[:3]
        return f"本文涉及「{'」「'.join(unique_matched)}」相关内容，与您的搜索意图高度相关。"
    return "本文内容与您的搜索查询相关。"

# 智能搜索接口
@app.post("/api/search", response_model=SearchResponse)
async def search_articles(request: SearchRequest):
    start_time = datetime.now()
    
    query_keywords = extract_keywords(request.query)
    
    if not query_keywords:
        raise HTTPException(status_code=400, detail="查询关键词为空")
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 构建FTS5查询
        fts_query = ' OR '.join(f'"{kw}"' for kw in query_keywords)
        
        # FTS5全文检索
        cursor.execute('''
            SELECT a.id, a.title, a.url, a.wechat_name, a.publish_date, a.summary, a.keywords,
                   bm25(articles_fts) as fts_score
            FROM articles a
            JOIN articles_fts ON a.id = articles_fts.rowid
            WHERE articles_fts MATCH ?
            ORDER BY fts_score
            LIMIT ? OFFSET ?
        ''', (fts_query, request.limit, request.offset))
        
        results = cursor.fetchall()
        
        # 获取总数
        cursor.execute('''
            SELECT COUNT(*) FROM articles a
            JOIN articles_fts ON a.id = articles_fts.rowid
            WHERE articles_fts MATCH ?
        ''', (fts_query,))
        total = cursor.fetchone()[0]
        
        # 转换为Article对象
        articles = []
        for row in results:
            article_dict = dict(row)
            match_reason = generate_match_reason(article_dict, query_keywords)
            articles.append(Article(
                id=article_dict['id'],
                title=article_dict['title'],
                url=article_dict['url'],
                wechat_name=article_dict['wechat_name'],
                publish_date=article_dict['publish_date'],
                summary=article_dict['summary'],
                keywords=article_dict['keywords'],
                match_reason=match_reason,
                score=article_dict['fts_score']
            ))
        
        took_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return SearchResponse(
            total=total,
            articles=articles,
            query=request.query,
            took_ms=took_ms
        )
        
    except sqlite3.OperationalError as e:
        if "no such table" in str(e):
            return await fallback_search(request, query_keywords, start_time)
        raise HTTPException(status_code=500, detail=f"数据库错误: {str(e)}")
    finally:
        conn.close()

# 回退搜索
async def fallback_search(request: SearchRequest, query_keywords: List[str], start_time: datetime):
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        like_conditions = []
        params = []
        for kw in query_keywords:
            like_conditions.append("(title LIKE ? OR summary LIKE ? OR keywords LIKE ?)")
            params.extend([f'%{kw}%', f'%{kw}%', f'%{kw}%'])
        
        where_clause = ' OR '.join(like_conditions)
        
        cursor.execute(f'''
            SELECT id, title, url, wechat_name, publish_date, summary, keywords
            FROM articles
            WHERE {where_clause}
            ORDER BY publish_date DESC
            LIMIT ? OFFSET ?
        ''', params + [request.limit, request.offset])
        
        results = cursor.fetchall()
        
        cursor.execute(f'''
            SELECT COUNT(*) FROM articles WHERE {where_clause}
        ''', params)
        total = cursor.fetchone()[0]
        
        articles = []
        for row in results:
            article_dict = dict(row)
            match_reason = generate_match_reason(article_dict, query_keywords)
            articles.append(Article(
                id=article_dict['id'],
                title=article_dict['title'],
                url=article_dict['url'],
                wechat_name=article_dict['wechat_name'],
                publish_date=article_dict['publish_date'],
                summary=article_dict['summary'],
                keywords=article_dict['keywords'],
                match_reason=match_reason,
                score=1.0
            ))
        
        took_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return SearchResponse(
            total=total,
            articles=articles,
            query=request.query,
            took_ms=took_ms
        )
        
    finally:
        conn.close()

# 获取文章详情
@app.get("/api/articles/{article_id}", response_model=Article)
async def get_article(article_id: int):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, title, url, wechat_name, publish_date, summary, keywords
        FROM articles WHERE id = ?
    ''', (article_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    article_dict = dict(row)
    return Article(**article_dict)

# 获取统计信息
@app.get("/api/stats")
async def get_stats():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM articles')
    total = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(DISTINCT wechat_name) FROM articles')
    sources = cursor.fetchone()[0]
    
    cursor.execute('SELECT MIN(publish_date), MAX(publish_date) FROM articles')
    date_range = cursor.fetchone()
    
    conn.close()
    
    return {
        "total_articles": total,
        "total_sources": sources,
        "date_range": {
            "start": date_range[0],
            "end": date_range[1]
        }
    }

# 健康检查
@app.get("/api/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

# Vercel Serverless入口
def handler(request):
    return app(request)
