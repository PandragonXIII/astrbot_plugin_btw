# astrbot_plugin_btw

一个为 AstrBot 提供 `/btw <问题>` 指令的轻量插件。  
它适合处理当前主话题之外的临时小问题，让你在不中断主线对话的情况下，快速发起一次额外的独立提问。

---
> [!WARNING]  
> 本插件由大模型主持编写，经过人工审阅。

## 功能简介

本插件提供了`/btw`指令：

- 将 `/btw` 后面的内容作为一次额外提问发送给当前模型，如：`/btw HTTP 403 是什么？`
- 不污染当前主线对话
- 用尽量轻量、可预测的方式返回结果

在不需要切换对话的情况下提供了轻量化、上下文无关的快速问答渠道。

---

## 功能特性

- 使用 AstrBot 当前会话所绑定的聊天模型
- 通过单独的 `llm_generate(...)` 调用发起一次额外提问
- 可选为回复添加 `[btw]` 前缀
- 配置简单，适合直接部署和继续扩展

---

## 快速开始

### 1. 安装插件

将插件目录放入 AstrBot 的插件目录中：

```text
AstrBot/data/plugins/astrbot_plugin_btw
```

确保目录内包含以下文件：

```text
main.py
metadata.yaml
_conf_schema.json
requirements.txt
```

然后在 AstrBot WebUI 中：

- 进入插件管理
- 找到 `astrbot_plugin_btw`
- 启用或重载插件

---

### 2. 使用方式

在聊天中发送：

```text
/btw 你的问题
```

例如：

```text
/btw What does HTTP 403 mean?
/btw 今晚吃什么
```

如果未提供问题内容：

```text
/btw
```

插件会返回用法提示。

---

### 3. 基础配置

当前版本仅提供一个轻量配置项：

#### `prefix_reply`

- 类型：`bool`
- 默认值：`true`
- 作用：是否在 `/btw` 的回复前添加 `[btw]` 前缀

示例：

- 开启后：
  ```text
  [btw] HTTP 403 表示服务器理解了请求，但拒绝授权访问。
  ```


---

## 核心逻辑

当前版本的核心逻辑非常直接：

1. 用户发送 `/btw <问题>`
2. 插件提取 `<问题>` 文本
3. 插件获取当前会话对应的聊天模型
4. 插件调用 `llm_generate(...)` 发起一次额外问题请求
5. 插件返回回答

---

## 文件结构

```text
astrbot_plugin_btw/
├── main.py
├── metadata.yaml
├── _conf_schema.json
├── README.md
├── TODO.md
├── LICENSE
└── requirements.txt
```

---

## 许可证

本项目使用 MIT License。
