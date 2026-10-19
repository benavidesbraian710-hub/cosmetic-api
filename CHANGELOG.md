# 化妆品文章智能检索系统 — 项目变更日志

> 记录项目从零到当前的每一步关键进展与变更。
> 每次改动都必须追加到此文件，格式：`## YYYY-MM-DD | 变更标题`

---

## 2026-06-17 | 产品设计方案 v1.2 定稿
- 确定检索架构：FTS5 + jieba分词关键词召回 + LLM批量精排两级架构
- 确定数据方案：每篇文章入库时调用LLM生成200-400字摘要 + 10-15个关键词存SQLite
- 数据库基线：约300篇文章

## 2026-07-18 | 数据质量治理启动
- 发现公众号数量偏差（11 vs 13），根因：搜狗来源脏数据
- 全面检查发现44篇搜狗跳转链接、45篇时效性违规、1篇空标题
- 数据治理从"数量正确"升级为"来源可信+时效合规+内容完整"

## 2026-07-20 | 数据库清洗 + v26发布
- 删除44篇搜狗来源 + 1篇6月15日前文章
- 数据库保留380篇有效文章（12个公众号）
- 发布v26（commit bae18ad）

## 2026-07-27 | 数据库扩容 — 三行业号纳入
- 新增财经早餐、亿邦动力、铱星云商三个行业公众号
- 三个新号累计补充历史文章121篇
- 数据库461→592篇（15个公众号），发布v38

## 2026-07-29 | 异构新号接入尝试（失败）
- 尝试接入WWD国际时尚特讯、化妆品财经在线、Vogue Business
- 三号全部失败（0/4篇）——文章详情页微信UI布局不同，坐标失效

## 2026-07-30 | 手动补录通道启用 + 数据库达685篇
- 手动补录9篇异构新号文章完成冷启动
- 数据库达685篇/18个公众号，发布v45

## 2026-08-04 | 数据库破787篇
- 日采21篇 + 补录14篇，数据库766→801篇（18个公众号）
- 发布v56

## 2026-08-06 | 采集方式终局切换 — RPA方案
- 公众号文章采集从peekaboo GUI坐标点击切换为RPA方案
- 新电脑RPA每日自动采集文章链接存入Excel
- 部署架构：推送GitHub触发Vercel自动部署

## 2026-08-07 | RPA新链路首次完整实战
- 两个Excel（各90条）合并去重后新增25篇、0失败
- 数据库863→888篇，commit 6b65cd9

## 2026-08-10 | 日期格式顽疾根治
- 入库脚本源头增加publish_date强制截断YYYY-MM-DD硬校验
- 修复数据库80条记录日期格式

## 2026-08-12 | 数据库破千
- 数据库达1006篇（首次破千），v67，commit 7a126e3

## 2026-08-14 | 公众号白名单硬标准确立
- 文章数据入库时wechat_name字段必须归属于18个白名单公众号之一
- 28条wechat_name归属脏数据清洗完成
- 数据库1062篇，v71

## 2026-08-17 | 项目商业化升级 — 一日闭环
- 老板凌晨战略指示 → Nick设计先行 → Phase 1前端五页面 → Phase 2后端验收
- 首页视觉定稿：红白简约品牌风（零金色 + Lucide线性图标）
- Supabase后端接入（article_reports表 + service_requests表）
- 主站v72冻结，预览站feature/new-arch分支

## 2026-08-18 | 双站数据同步 + 预览站独立
- 主站保持main分支v72冻结（旧视觉）
- 预览站cosmetic-preview独立仓库（国内免翻墙）
- 双轨数据流：主站冻视觉不冻数据、预览站冻视觉只收数据
- 数据库1111→1143篇，v73

## 2026-08-19 | 功能A「智能选文报告」上线预览仓
- 选文界面 + 右侧已选面板 + 报告要求表单
- 提交写入Supabase article_reports表
- 首页更新为三功能卡片
- service.html改为全开放式表单（删除六层结构化表单）

## 2026-08-20 | 老板演示日 + 智能找文功能立项
- 演示日开发侧缺陷清零
- Nick提出新增「智能找文」功能：自然语言混合检索推荐文章
- 后端方案当日反转：取消全文入库，改为链接+摘要+关键词+向量
- 生成《后端设计方案v2.0》

## 2026-08-21 | 智能找文前端定稿 + 数据基线更新
- 前端五项设计决策定稿（首页第5卡片/匹配理由/相关度排序/加入选文报告/一期不多轮追问）
- 数据库升级两阶段拍板：第一阶段关键词+摘要检索，第二阶段向量检索
- 存量1,230篇文章摘要/关键词批量回填启动（Mac mini后台PID 21845）
- 第九批5文件入库，数据基线更新至1,230篇/v74

## 2026-08-24 | 智能找文后端API开发完成 + 三项核心需求拍板
- FastAPI + SQLite后端API开发完成，部署Mac mini本地
- Nick拍板三项核心需求：删除重复文章/四层关键词分层/Kimi K3 LLM精排
- 数据库清理：删除28篇重复文章（1,290→1,262篇）
- API公网化：cloudflared隧道替代ngrok
- 前端样式恢复至commit 3a4405d（已确认样式不可擅动）
- 缓存规避：文件名版本号find-v2.html → find-v3.html

## 2026-08-24 | 检索架构升级 — 意图锚定检索（Intent-Anchored Search）
- **问题**：四层关键词分层平铺扩展（35个词OR召回），核心概念无特殊地位，导致美白/保湿/祝福等非相关文章被召回
- **方案**：意图锚定检索——LLM先识别查询的"锚点概念"（必须满足），再识别"修饰概念"（加分项）
- **架构变化**：
  - `llm_extract_keywords()` → `llm_parse_intent()`：输出anchor（核心概念）+ anchor_synonyms（同义词）+ modifiers（修饰词）+ exclude_if（排除主题）
  - `fts_search()` → `anchor_search()`：锚点AND召回（必须命中），修饰词加权；AND结果不足时回退到仅锚点查询
  - `llm_rerank()`：prompt动态注入anchor，LLM生成relevance分数（0-100），按分数排序；删除全部硬编码排除规则
  - `generate_match_reason()`：基于intent动态生成，不再依赖四层关键词
- **关键改进**：
  - 锚点AND召回："抗衰老成分趋势"只召回主要讨论抗衰老的文章，美白/保湿/祝福等直接不召回
  - 通用复用：同一套代码适配任意查询（美白/保湿/玻尿酸等），不需要改硬编码
  - LLM评分排序：relevance 0-100替代固定90分，排序更精确
- **实测效果**（"抗衰老成分趋势"）：返回5篇，全部主要讨论抗衰老成分，无美白/保湿/祝福等干扰文章
- **状态**：✅ 已完成并验证

## 2026-08-24 | 产品设计文档更新至v3.0
- 整合v1.2（初版设计）和v2.0（方案讨论稿），更新为反映系统实际运行状态的v3.0
- 核心内容：意图锚定检索架构、五功能卡片、双站部署、数据基线v75（1,262篇）、API设计、采集入库SOP
- 存档位置：桌面《化妆品文章智能检索系统_设计文档_v3.0.md》
- 同时创建项目变更日志CHANGELOG.md，后续每次改动追加记录

## 2026-08-24 | 时间过滤功能上线
- **问题**：搜索"近一周抗衰老"返回一周以前的文章，时间限定词未生效
- **修复**：新增`parse_time_filter()`函数，支持近一周/近两周/近一个月/近三天/近五天/近十天/近半月/今年/近期/最近等时间限定词
- **实现**：FTS5查询附加`publish_date >= date_from`条件，修饰词中自动过滤时间相关词汇
- **已知限制**：58篇新入库文章缺摘要/关键词，FTS5仅标题可匹配，召回率受限
- **状态**：✅ 已完成并推送

## 2026-10-17 13:00 LLM 精排模型切换：Kimi K3 → MiniMax M3

### 问题现象
智能找文 LLM 精排阶段（`llm_rerank()`）调用 Kimi K3，但 Kimi API 当前 403 Forbidden，导致精排全部走 fallback 兜底（直接返回 FTS5 检索结果），精排能力形同虚设。

### 根因排查
1. api.log 大量 "Kimi API 调用失败: 403 Client Error: Forbidden"
2. KIMI_API_KEY 在 Plist 显示为 `sk-kim…voOw`（72 字符 - 实际有效，但 Kimi 服务端拒了）
3. Kimi Coding Plan 端点可能已变更/欠费/账号被封

### 真正根因
Kimi Coding Plan API 当前不可用。改用 OpenClaw 已配置的 MiniMax provider（`https://api.minimaxi.com/anthropic`，anthropic-messages 协议）替代。

### 修复措施
- `main.py` 新增 `call_minimax_api()` 函数（与 call_kimi_api 同样支持 anthropic-messages 协议）
- `llm_rerank()` 改用 `call_minimax_api(prompt, model='MiniMax-M3', timeout=120)`
- `llm_parse_intent()` 保持 Kimi K3（意图解析不受影响）
- Plist (`com.cosmetic.api.plist`) 新增 `MINIMAX_API_KEY` env（待 Nick 填入完整 key）
- 双 provider 架构：Kimi 兜底意图解析，MiniMax 主战精排

### 验证结果
- [ ] 待 Nick 提供完整 MiniMax API key 后填入 Plist
- [ ] 重启 uvicorn 测试 `/api/search` 完整流程
- [ ] 验证精排结果质量（对比 Kimi 时代）


## 2026-10-19 API 智能找文全面恢复 + FTS5 重建 + LLM fallback

### 问题现象
- /api/search 全部返回 0 结果（POST 抗衰老/化妆品/美白 都 0）
- /api/stats 和 /api/health 正常 200
- API 日志显示锚点检索召回 100 篇，但 LLM 精排阶段全部失败，输出 0 篇

### 根因排查过程
- Step 1: 验证 db 状态 → cosmetic-api/cosmetic_articles.db 仍是 8-24 旧版（24MB, db-shm/wal 是 10-08），deploy 仓 db 是 10-17 当前版（35MB, 2,486 篇）
- Step 2: 软链化 cosmetic-api/cosmetic_articles.db → deploy 仓 db（数据真源统一）
- Step 3: 杀老 uvicorn PID 1921，launchd plist 自动拉起新进程（带 COSMETIC_DB_PATH 环境变量）
- Step 4: /api/stats 验证 → 2,486 articles OK；/api/health OK
- Step 5: /api/search 仍 0 → 查 API 日志发现 `MINIMAX_API_KEY 未配置`（重复 9 次）
- Step 6: 检查 plist `com.cosmetic.api.plist` → `MINIMAX_API_KEY` 值为 `"TBD_FILL_FROM_NICK"` 占位符未填
- Step 7: KIMI_API_KEY 真实有效（`sk-kim…voOw`），Kimi K3 可用
- Step 8: FTS5 验证 → articles_fts 表族存在但只 88 行，触发器 0 个（之前误建在 search-bot 目录的 Jun 18 老软链，不是 deploy db）

### 真正根因（两层叠加）
1. **FTS5 索引缺失**: deploy db 上 articles_fts 不存在或严重不完整，FTS5 MATCH 召回为 0
2. **LLM 精排失败**: plist 中 `MINIMAX_API_KEY` 是占位符，10-17 切到 MiniMax 时没填真 key
3. 两者叠加 → 任意单修都救不回 0 结果，必须双修

### 修复措施（4 步方案 B 全部完成）

**Step 1 - 软链化 + 备份**:
- 备份旧 db: `cp cosmetic_articles.db cosmetic_articles.db.bak.20261019_100530`（24MB）
- 清理旧 shm/wal: `rm -f cosmetic_articles.db-shm cosmetic_articles.db-wal`
- 软链: `ln -sf /Users/yuming.chen/.openclaw/workspace/cosmetic-deploy/cosmetic_articles.db cosmetic_articles.db`
- 验证: Python sqlite3 读软链 → 2,486 articles OK

**Step 2 - 重启 uvicorn**:
- 杀老 PID 1921（跑了 7h48m）
- launchd plist 自动拉起新进程（PID 56051 → 重启后 59550）
- launchd plist 已配 `COSMETIC_DB_PATH=/Users/yuming.chen/.openclaw/workspace/cosmetic-deploy/cosmetic_articles.db`
- Python 解释器: `/Library/Developer/CommandLineTools/.../Python -m uvicorn main:app --host 0.0.0.0 --port 8000`

**Step 3 - FTS5 重建**:
- 用绝对路径 `/Users/yuming.chen/.openclaw/workspace/cosmetic-api/cosmetic_articles.db` 打开 deploy db
- `CREATE VIRTUAL TABLE articles_fts USING fts5(title, content, content='articles', content_rowid='id')`
- `INSERT INTO articles_fts(rowid, title, content) SELECT id, COALESCE(title,''), COALESCE(content,'') FROM articles` → 2,486 行
- 加 3 个触发器保持 INSERT/DELETE/UPDATE 同步:
  - `articles_ai` AFTER INSERT → 同步到 FTS5
  - `articles_ad` AFTER DELETE → FTS5 delete 标记
  - `articles_au` AFTER UPDATE → 同步 rowid 变化

**Step 4 - LLM 精排 fallback**:
- `main.py` 的 `call_minimax_api()` 内加 fallback
- key 缺失时自动调 `call_kimi_api('kimi-k3')`
- 临时方案，Nick 填真 key 后无需改代码

### 验证结果
- /api/stats: `{"total_articles":2486,"total_sources":18,"date_range":{"start":"2026-06-15","end":"2026-10-17"}}`
- /api/health: `{"status":"ok","timestamp":"2026-10-19T10:18:20.931391"}`
- /api/search "抗衰老": 2 篇（top: "Hormesis 适度应激效应" 抗衰, score 95）
- /api/search "化妆品": 7 篇
- /api/search "美白": 1 篇
- FTS5 直接 MATCH: 化妆品 53 / 抗衰老 13 / 美白 51
- 锚点检索召回 100 → LLM 精排严格过滤到 top-N（精度优先，预期行为）

### 同步更新
- 本地 commit: "fix(rerank): MINIMAX_API_KEY 缺失时 fallback 到 Kimi K3"（1 file changed, 4 insertions, 2 deletions）
- 仓库无 remote，暂未 push
- 对应 deploy 仓 commit `a0b70fd`（export_data.py 治理）待 push

### 已知遗留
- plist `MINIMAX_API_KEY=***` 占位符（fallback 临时顶上，Nick 提供真 key 后填入 plist）
- cosmetic-api 仓库无 remote，本地 commit 无云端备份
- cosmetic-api 4 文件 modified + typechange + 10+ untracked 噪音未清理
- 10-08 那 4 个数据量异常文件没看到单独处理记录
