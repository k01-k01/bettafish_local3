# BettaFish简化版

这是一个简化版的BettaFish舆情分析系统，专为本地运行而设计。它集成了网络爬虫、本地大语言模型分析和报告生成功能，能够在没有互联网连接的情况下运行。

## 功能特点

1. **网络爬虫**: 模拟从网络上抓取与特定主题相关的内容
2. **本地LLM分析**: 使用本地部署的Qwen大语言模型进行舆情分析
3. **报告生成**: 自动生成结构化的舆情分析报告
4. **Web界面**: 提供友好的Web界面，方便用户操作
5. **历史记录**: 自动保存分析历史，支持回溯查看

## 系统要求

- Python 3.8+
- 至少8GB内存（推荐16GB）
- NVIDIA GPU（推荐，可显著提升处理速度）

## 安装步骤

1. 克隆或下载本项目到本地
2. 安装依赖包：
   ```
   pip install -r requirements.txt
   ```

3. 确保本地Qwen模型位于指定路径：`D:\project\Xianyu_AutoAgent\model\qwen\Qwen2___5-1___5B-Instruct`

## 使用方法

### 命令行模式

```bash
python app.py "分析主题"
```

### Web界面模式

```bash
python web_app.py
```

然后在浏览器中访问 http://localhost:5000

## 项目结构

```
bettafish_local3/
├── app.py              # 命令行主应用
├── web_app.py          # Web应用
├── config.py           # 配置文件
├── simple_crawler.py   # 简化版爬虫
├── local_llm.py        # 本地LLM客户端
├── analyzer.py         # 分析器
├── reporter.py         # 报告生成器
├── db.py               # 数据库模块
├── requirements.txt    # 依赖包列表
├── README.md           # 说明文档
├── templates/          # Web模板文件
│   ├── base.html       # 基础模板
│   └── index.html      # 主页模板
└── static/             # 静态资源文件
    └── style.css       # 样式文件
```

## 工作流程

1. 用户输入分析主题
2. 系统启动网络爬虫抓取相关内容
3. 使用本地Qwen大语言模型分析舆情
4. 生成结构化的分析报告
5. 展示结果并保存到本地数据库

