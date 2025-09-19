# paper-report-mcp
> 🔍 MCP服务器，实现arxiv论文查询、下载、翻译、总结输出。

基于[arxiv-mcp-server](https://github.com/blazickjp/arxiv-mcp-server)，对核心功能进行了优化设计。



## ✨ 核心功能

- 🔎 **论文检索**: 搜索arxiv论文，搜索参数支持组合查询
- 📄 **论文获取**: 下载论文pdf原文，翻译成中文，输出markdown文件
- 📋 **论文列表**: 查看所有下载的论文列表
- 🗃️ **本地存储**: 论文pdf本地保存


## 💡 工具列表

### 1. search_papers
搜索arxiv论文，可选的搜索参数如下：

```python
result = await call_tool("search_papers", {
    "query": "transformer architecture",
    "max_results": 10,
    "date_from": "2023-01-01",
    "categories": ["cs.AI", "cs.LG"]
})
```

### 2. download_paper
根据arxiv ID下载论文pdf文件，并翻译成中文，结果输出markdown文件：

```python
result = await call_tool("download_paper", {
    "paper_id": "2401.12345"
})
```

### 3. list_papers
查看所有下载到本地的论文：

```python
result = await call_tool("list_papers", {})
```

### 4. read_paper
读取下载到本地的论文pdf和markdown文件内容：

```python
result = await call_tool("read_paper", {
    "paper_id": "2401.12345"
})
```
