# Open-AutoGLM 项目架构分析文档

## 目录

1. [项目概述](#项目概述)
2. [整体架构](#整体架构)
3. [模块功能详解](#模块功能详解)
4. [核心模块代码解析](#核心模块代码解析)
5. [数据流与执行流程](#数据流与执行流程)
6. [设计模式分析](#设计模式分析)
7. [扩展点与定制化](#扩展点与定制化)

---

## 项目概述

### 1.1 项目简介

**Open-AutoGLM** 是一个基于视觉语言模型（Vision-Language Model）的手机自动化智能助理框架。它通过AI理解手机屏幕内容，自动规划并执行操作流程，实现自然语言驱动的手机任务自动化。

### 1.2 核心特性

- **多平台支持**：Android (ADB)、HarmonyOS (HDC)、iOS (WebDriverAgent/XCTest)
- **视觉理解**：基于AutoGLM-Phone-9B多模态模型进行屏幕内容理解
- **自然语言交互**：用户仅需用自然语言描述需求（如"打开微信给张三发消息"）
- **智能规划**：AI自动拆解任务、规划操作步骤
- **安全机制**：敏感操作确认、人工接管（登录、验证码）
- **远程控制**：支持WiFi、TCP/IP远程调试
- **多语言支持**：中英文系统提示词和界面
- **日志记录** ⭐：
  - ✅ CLI 默认启用（main.py 运行时自动记录）
  - ✅ 双日志文件（模型响应 + 操作序列）
  - ✅ JSONL 格式，易于分析
  - ✅ 支持性能追踪（TTFT、推理时间）
  - ✅ Android、HarmonyOS、iOS 全平台支持

### 1.3 技术栈

| 技术组件 | 用途 |
|---------|------|
| Python 3.10+ | 主要开发语言 |
| OpenAI API | 模型推理接口 |
| ADB/HDC/XCTest | 设备控制工具 |
| Pillow | 图像处理 |
| vLLM/sglang | 可选的本地模型推理 |

---

## 整体架构

### 2.1 分层架构图

```
┌─────────────────────────────────────────────────────────┐
│               应用层 (Application Layer)                 │
│   - PhoneAgent (Android/HarmonyOS)                       │
│   - IOSPhoneAgent (iOS)                                  │
│   - main.py / ios.py (CLI 入口)                         │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│             业务逻辑层 (Business Logic Layer)            │
│   - ModelClient (AI推理客户端)                          │
│   - ActionHandler (操作执行器)                          │
│   - MessageBuilder (消息构建器)                         │
│   - AgentLogger (日志记录器) ⭐NEW                      │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              抽象层 (Abstraction Layer)                  │
│   - DeviceFactory (设备工厂 - 统一接口)                 │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│          平台实现层 (Platform Implementation Layer)      │
│   ┌─────────────┬─────────────┬─────────────┐          │
│   │ ADB Module  │ HDC Module  │ XCTest      │          │
│   │ (Android)   │ (HarmonyOS) │ (iOS)       │          │
│   └─────────────┴─────────────┴─────────────┘          │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│          系统交互层 (System Interaction Layer)           │
│   - Connection Management (连接管理)                     │
│   - Screenshot Capture (屏幕截图)                        │
│   - Device Control (设备控制)                            │
│   - Input Management (输入管理)                          │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│           外部依赖 (External Dependencies)               │
│   - ADB / HDC / libimobiledevice                         │
│   - OpenAI API / 本地 LLM (vLLM/sglang)                 │
│   - WebDriverAgent (iOS)                                 │
└─────────────────────────────────────────────────────────┘
```

### 2.2 目录结构

```
Open-AutoGLM/
├── phone_agent/                    # 核心包
│   ├── __init__.py                # 包导出
│   ├── agent.py                   # Android/HarmonyOS Agent
│   ├── agent_ios.py              # iOS Agent
│   ├── device_factory.py         # 设备工厂(统一接口)
│   │
│   ├── adb/                      # Android 设备控制
│   │   ├── connection.py         # ADB连接管理
│   │   ├── device.py             # 设备操作
│   │   ├── input.py              # 文本输入
│   │   └── screenshot.py         # 屏幕截图
│   │
│   ├── hdc/                      # HarmonyOS 设备控制
│   │   ├── connection.py         # HDC连接管理
│   │   ├── device.py             # 设备操作
│   │   ├── input.py              # 文本输入
│   │   └── screenshot.py         # 屏幕截图
│   │
│   ├── xctest/                   # iOS 设备控制
│   │   ├── connection.py         # WebDriverAgent连接
│   │   ├── device.py             # 设备操作
│   │   ├── input.py              # 文本输入
│   │   └── screenshot.py         # 屏幕截图
│   │
│   ├── actions/                  # 操作处理
│   │   ├── handler.py            # 通用操作处理器 (399行)
│   │   └── handler_ios.py        # iOS操作处理器 (280行)
│   │
│   ├── model/                    # AI模型客户端
│   │   └── client.py             # OpenAI兼容客户端
│   │
│   ├── logger.py                 # 日志记录模块 ⭐NEW
│   │
│   └── config/                   # 配置模块
│       ├── apps.py               # Android应用映射
│       ├── apps_harmonyos.py    # HarmonyOS应用映射
│       ├── apps_ios.py          # iOS应用映射
│       ├── prompts_zh.py         # 中文系统提示词
│       ├── prompts_en.py         # 英文系统提示词
│       ├── i18n.py               # 国际化字符串
│       └── timing.py             # 操作时序配置
│
├── logs/                         # 日志文件目录 ⭐NEW
│   ├── YYYYMMDD_HHMMSS_model.jsonl    # 模型响应日志
│   └── YYYYMMDD_HHMMSS_actions.jsonl  # 操作序列日志
│
├── main.py                       # Android/HarmonyOS CLI入口
├── ios.py                        # iOS CLI入口
├── requirements.txt              # Python依赖
└── README.md                     # 项目文档
```

---

## 模块功能详解

### 3.1 应用层 (Application Layer)

#### 3.1.1 PhoneAgent (agent.py)

**职责**：Android/HarmonyOS Agent的核心编排器

**关键类**：
- `AgentConfig`: Agent配置（最大步数、设备ID、语言、系统提示词等）
- `StepResult`: 单步执行结果
- `PhoneAgent`: 主Agent类

**核心功能**：
- `run(task)`: 执行完整任务直到完成或达到最大步数
- `step(task)`: 单步执行（用于调试）
- `reset()`: 重置Agent状态

**配置参数**：
```python
@dataclass
class AgentConfig:
    max_steps: int = 100              # 最大执行步数
    device_id: str | None = None      # 设备ID（多设备时使用）
    lang: str = "cn"                  # 语言（cn/en）
    system_prompt: str | None = None  # 自定义系统提示词
    verbose: bool = True              # 详细输出
    enable_logging: bool = False      # ⭐启用日志记录
    log_config: LogConfig | None = None  # ⭐日志配置
    session_name: str | None = None   # ⭐自定义会话名称
```

#### 3.1.2 IOSPhoneAgent (agent_ios.py)

**职责**：iOS专用Agent

**特点**：
- 使用WebDriverAgent进行设备控制
- 类似的接口设计，但针对iOS API优化
- ⭐支持完整的日志记录功能（与Android版本保持一致）

**配置参数**：
```python
@dataclass
class IOSAgentConfig:
    max_steps: int = 100                  # 最大执行步数
    wda_url: str = "http://localhost:8100"  # WebDriverAgent URL
    session_id: str | None = None         # WDA会话ID
    device_id: str | None = None          # iOS设备UDID
    lang: str = "cn"                      # 语言（cn/en）
    system_prompt: str | None = None      # 自定义系统提示词
    verbose: bool = True                  # 详细输出
    enable_logging: bool = False          # ⭐启用日志记录
    log_config: LogConfig | None = None   # ⭐日志配置
    session_name: str | None = None       # ⭐自定义会话名称
```

### 3.2 业务逻辑层 (Business Logic Layer)

#### 3.2.1 ModelClient (model/client.py)

**职责**：AI模型推理客户端

**关键类**：
- `ModelConfig`: 模型配置
- `ModelResponse`: 模型响应
- `ModelClient`: OpenAI兼容客户端
- `MessageBuilder`: 消息构建辅助类

**核心功能**：
- 流式推理（实时显示思考过程）
- 性能指标收集（TTFT、推理时间）
- 响应解析（分离思考和动作）

**模型配置**：
```python
@dataclass
class ModelConfig:
    base_url: str = "http://localhost:8000/v1"
    api_key: str = "EMPTY"
    model_name: str = "autoglm-phone-9b"
    max_tokens: int = 3000
    temperature: float = 0.0
    top_p: float = 0.85
    frequency_penalty: float = 0.2
```

#### 3.2.2 ActionHandler (actions/handler.py)

**职责**：操作执行处理器

**支持的操作类型**：

| 操作 | 说明 | 参数示例 |
|------|------|---------|
| Launch | 启动应用 | `app: "微信"` |
| Tap | 点击坐标 | `element: [500, 800]` |
| Type | 输入文本 | `text: "你好"` |
| Swipe | 滑动屏幕 | `start: [500, 800], end: [500, 200]` |
| Back | 返回上一页 | 无 |
| Home | 返回桌面 | 无 |
| Double Tap | 双击 | `element: [500, 800]` |
| Long Press | 长按 | `element: [500, 800], duration_ms: 3000` |
| Wait | 等待 | `duration: "2 seconds"` |
| Take_over | 人工接管 | `message: "请完成验证码"` |
| Note | 记录内容 | 无 |
| Call_API | 调用API | 无 |

**坐标系统**：
- 使用相对坐标系（0-1000）
- 自动转换为绝对像素坐标
- 适配不同分辨率屏幕

**示例**：
```python
# 相对坐标 [500, 500] 表示屏幕中心
# 在 1080x1920 屏幕上转换为 (540, 960)
x = int(500 / 1000 * 1080)  # 540
y = int(500 / 1000 * 1920)  # 960
```

#### 3.2.3 AgentLogger (logger.py) ⭐NEW

**职责**：日志记录与分析

**关键类**：
- `LogConfig`: 日志配置
- `AgentLogger`: 日志记录器

**核心功能**：
- **双日志文件**：每次运行创建两个独立的日志文件
  - `模型日志 (model.jsonl)`：记录完整的模型响应（思考过程 + 动作指令 + 性能指标）
  - `操作日志 (actions.jsonl)`：记录解析后的操作对象和执行结果
- **会话管理**：支持自定义会话名称，自动生成时间戳
- **JSONL格式**：每行一个JSON对象，便于流式处理和分析
- **性能追踪**：记录TTFT、思考结束时间、总推理时间等指标
- **上下文信息**：记录屏幕信息（当前应用、分辨率）

**日志配置**：
```python
@dataclass
class LogConfig:
    log_dir: str = "logs"              # 日志目录
    enable_model_log: bool = True      # 启用模型日志
    enable_action_log: bool = True     # 启用操作日志
```

**使用示例**：
```python
from phone_agent import PhoneAgent, AgentConfig
from phone_agent.logger import LogConfig

# 启用日志记录
agent_config = AgentConfig(
    enable_logging=True,
    log_config=LogConfig(log_dir="logs"),
    session_name="wechat_test"  # 可选：自定义会话名
)

agent = PhoneAgent(agent_config=agent_config)
agent.run("打开微信")

# 日志文件将生成在:
# logs/20260109_143025_wechat_test_model.jsonl
# logs/20260109_143025_wechat_test_actions.jsonl
```

**日志格式示例**：

*模型日志 (model.jsonl)*：
```json
{
  "timestamp": "2026-01-09T14:30:25.123456",
  "step": 1,
  "thinking": "当前在桌面，需要启动微信应用。我应该使用Launch操作。",
  "action": "do(action=\"Launch\", app=\"微信\")",
  "raw_content": "当前在桌面，需要启动微信应用...\ndo(action=\"Launch\", app=\"微信\")",
  "performance": {
    "time_to_first_token": 0.156,
    "time_to_thinking_end": 1.234,
    "total_time": 2.567
  }
}
```

*操作日志 (actions.jsonl)*：
```json
{
  "timestamp": "2026-01-09T14:30:27.456789",
  "step": 1,
  "action": {
    "_metadata": "do",
    "action": "Launch",
    "app": "微信"
  },
  "result": {
    "success": true,
    "message": null
  },
  "screen_info": {
    "current_app": "桌面",
    "width": 1080,
    "height": 1920
  }
}
```

### 3.3 抽象层 (Abstraction Layer)

#### 3.3.1 DeviceFactory (device_factory.py)

**职责**：设备工厂模式，提供统一的设备控制接口

**设备类型**：
```python
class DeviceType(Enum):
    ADB = "adb"      # Android设备
    HDC = "hdc"      # HarmonyOS设备
    IOS = "ios"      # iOS设备
```

**统一接口**：
- `get_screenshot()` - 获取屏幕截图
- `get_current_app()` - 获取当前应用
- `tap(x, y)` - 点击
- `swipe()` - 滑动
- `back()` / `home()` - 系统按键
- `launch_app()` - 启动应用
- `type_text()` - 输入文本
- `double_tap()` / `long_press()` - 高级触摸

**工作原理**：
```python
# 根据设备类型动态加载对应模块
if device_type == DeviceType.ADB:
    from phone_agent import adb
    module = adb
elif device_type == DeviceType.HDC:
    from phone_agent import hdc
    module = hdc
elif device_type == DeviceType.IOS:
    from phone_agent import xctest
    module = xctest
```

### 3.4 平台实现层 (Platform Implementation Layer)

#### 3.4.1 ADB模块 (phone_agent/adb/)

**connection.py - 连接管理**：
- USB连接
- WiFi连接（TCP/IP 5555端口）
- 远程连接
- 设备列表查询
- 连接状态管理

**device.py - 设备操作**：
- 触摸操作（tap, swipe, long_press）
- 系统按键（back, home, menu）
- 应用启动
- 当前应用获取

**input.py - 文本输入**：
- ADB Keyboard集成
- 多行文本支持
- 输入法自动切换

**screenshot.py - 屏幕截图**：
- 截图捕获
- 敏感页面检测（支付、银行等）
- Base64编码
- 图像优化

#### 3.4.2 HDC模块 (phone_agent/hdc/)

**结构与ADB模块类似**，针对HarmonyOS进行优化：
- 使用HDC命令替代ADB
- 支持HarmonyOS特定API
- 原生输入法支持（无需ADB Keyboard）

#### 3.4.3 XCTest模块 (phone_agent/xctest/)

**基于WebDriverAgent**：
- HTTP REST API通信
- 会话(Session)管理
- iOS特定操作支持

### 3.5 配置层 (Configuration Layer)

#### 3.5.1 应用映射 (apps.py / apps_harmonyos.py / apps_ios.py)

**Android应用映射示例**：
```python
APP_PACKAGES = {
    "微信": "com.tencent.mm",
    "支付宝": "com.eg.android.AlipayGphone",
    "淘宝": "com.taobao.taobao",
    # ... 50+应用
}
```

#### 3.5.2 系统提示词 (prompts_zh.py / prompts_en.py)

**中文提示词结构**（146行）：
- 角色定义
- 屏幕理解能力说明
- 可用操作列表及格式要求
- 输出格式规范（思考链 + 动作）
- 安全操作指引
- 示例演示

**输出格式要求**：
```
<思考过程>
do(action="操作名", 参数...)
```

或：
```
<思考过程>
finish(message="任务完成消息")
```

#### 3.5.3 时序配置 (timing.py)

**配置各操作的延迟时间**：
```python
TIMING_CONFIG = {
    "action": {
        "keyboard_switch_delay": 0.5,  # 键盘切换延迟
        "text_input_delay": 0.3,       # 文本输入延迟
        "text_clear_delay": 0.2,       # 文本清除延迟
        "keyboard_restore_delay": 0.5, # 键盘恢复延迟
    }
}
```

---

## 核心模块代码解析

### 4.1 PhoneAgent 核心执行流程

#### 4.1.1 run() 方法解析

**位置**: [agent.py:84-110](phone_agent/agent.py#L84-L110)

```python
def run(self, task: str) -> str:
    """执行完整任务"""
    # 1. 初始化上下文
    self._context = []
    self._step_count = 0

    # 2. 执行第一步（包含用户任务）
    result = self._execute_step(task, is_first=True)
    if result.finished:
        return result.message or "Task completed"

    # 3. 循环执行直到完成或达到最大步数
    while self._step_count < self.agent_config.max_steps:
        result = self._execute_step(is_first=False)
        if result.finished:
            return result.message or "Task completed"

    return "Max steps reached"
```

**执行逻辑**：
1. 清空上下文和步数计数器
2. 执行第一步，将用户任务作为初始输入
3. 循环执行后续步骤，每步基于当前屏幕状态
4. 检查任务是否完成或达到最大步数限制

#### 4.1.2 _execute_step() 方法详解

**位置**: [agent.py:136-243](phone_agent/agent.py#L136-L243)

**完整执行流程**：

```python
def _execute_step(self, user_prompt: str | None = None, is_first: bool = False) -> StepResult:
    self._step_count += 1

    # ========== 1. 屏幕状态捕获 ==========
    device_factory = get_device_factory()
    screenshot = device_factory.get_screenshot(self.agent_config.device_id)
    current_app = device_factory.get_current_app(self.agent_config.device_id)

    # ========== 2. 构建消息上下文 ==========
    if is_first:
        # 第一步：添加系统提示词和用户任务
        self._context.append(
            MessageBuilder.create_system_message(self.agent_config.system_prompt)
        )
        screen_info = MessageBuilder.build_screen_info(current_app)
        text_content = f"{user_prompt}\n\n{screen_info}"
        self._context.append(
            MessageBuilder.create_user_message(
                text=text_content,
                image_base64=screenshot.base64_data
            )
        )
    else:
        # 后续步骤：只添加屏幕信息
        screen_info = MessageBuilder.build_screen_info(current_app)
        text_content = f"** Screen Info **\n\n{screen_info}"
        self._context.append(
            MessageBuilder.create_user_message(
                text=text_content,
                image_base64=screenshot.base64_data
            )
        )

    # ========== 3. 调用AI模型 ==========
    try:
        response = self.model_client.request(self._context)
    except Exception as e:
        return StepResult(success=False, finished=True, ...)

    # ========== 4. 解析动作 ==========
    try:
        action = parse_action(response.action)
    except ValueError:
        action = finish(message=response.action)

    # ========== 5. 移除图像节省上下文 ==========
    self._context[-1] = MessageBuilder.remove_images_from_message(self._context[-1])

    # ========== 6. 执行动作 ==========
    try:
        result = self.action_handler.execute(
            action,
            screenshot.width,
            screenshot.height
        )
    except Exception as e:
        result = self.action_handler.execute(
            finish(message=str(e)),
            screenshot.width,
            screenshot.height
        )

    # ========== 7. 添加助手响应到上下文 ==========
    self._context.append(
        MessageBuilder.create_assistant_message(
            f"<think>{response.thinking}</think><answer>{response.action}</answer>"
        )
    )

    # ========== 8. 检查是否完成 ==========
    finished = action.get("_metadata") == "finish" or result.should_finish

    return StepResult(
        success=result.success,
        finished=finished,
        action=action,
        thinking=response.thinking,
        message=result.message or action.get("message")
    )
```

**关键点分析**：

1. **屏幕捕获**：每步都捕获最新屏幕状态和当前应用
2. **上下文构建**：第一步包含系统提示词和用户任务，后续步骤只包含屏幕信息
3. **图像优化**：执行后移除图像内容，避免上下文过大
4. **错误处理**：模型调用和动作执行都有异常捕获
5. **状态管理**：维护完整的对话历史（包含思考和动作）

### 4.2 ModelClient 推理流程

#### 4.2.1 流式推理实现

**位置**: [model/client.py:53-174](phone_agent/model/client.py#L53-L174)

```python
def request(self, messages: list[dict[str, Any]]) -> ModelResponse:
    # 1. 启动计时
    start_time = time.time()
    time_to_first_token = None
    time_to_thinking_end = None

    # 2. 创建流式请求
    stream = self.client.chat.completions.create(
        messages=messages,
        model=self.config.model_name,
        max_tokens=self.config.max_tokens,
        temperature=self.config.temperature,
        top_p=self.config.top_p,
        frequency_penalty=self.config.frequency_penalty,
        stream=True,  # 启用流式响应
    )

    # 3. 流式解析和实时输出
    raw_content = ""
    buffer = ""
    action_markers = ["finish(message=", "do(action="]
    in_action_phase = False
    first_token_received = False

    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            content = chunk.choices[0].delta.content
            raw_content += content

            # 记录首Token时间（TTFT指标）
            if not first_token_received:
                time_to_first_token = time.time() - start_time
                first_token_received = True

            if in_action_phase:
                # 已进入动作阶段，不再打印
                continue

            buffer += content

            # 检测动作标记（finish或do）
            for marker in action_markers:
                if marker in buffer:
                    # 打印思考部分
                    thinking_part = buffer.split(marker, 1)[0]
                    print(thinking_part, end="", flush=True)
                    print()  # 思考结束换行
                    in_action_phase = True

                    # 记录思考结束时间
                    if time_to_thinking_end is None:
                        time_to_thinking_end = time.time() - start_time
                    break

            # 智能缓冲：检查是否可能是标记前缀
            if not in_action_phase:
                is_potential_marker = False
                for marker in action_markers:
                    for i in range(1, len(marker)):
                        if buffer.endswith(marker[:i]):
                            is_potential_marker = True
                            break

                if not is_potential_marker:
                    # 安全打印缓冲内容
                    print(buffer, end="", flush=True)
                    buffer = ""

    # 4. 计算总时间
    total_time = time.time() - start_time

    # 5. 解析思考和动作
    thinking, action = self._parse_response(raw_content)

    # 6. 打印性能指标
    print(f"⏱️ 首Token时间: {time_to_first_token:.3f}s")
    print(f"⏱️ 思考结束时间: {time_to_thinking_end:.3f}s")
    print(f"⏱️ 总推理时间: {total_time:.3f}s")

    return ModelResponse(
        thinking=thinking,
        action=action,
        raw_content=raw_content,
        time_to_first_token=time_to_first_token,
        time_to_thinking_end=time_to_thinking_end,
        total_time=total_time
    )
```

**技术亮点**：

1. **流式输出**：实时显示AI思考过程，提升用户体验
2. **智能缓冲**：避免在动作标记边界截断输出
3. **性能监控**：收集TTFT、思考时间、总时间等指标
4. **分阶段处理**：区分思考阶段和动作阶段

#### 4.2.2 响应解析逻辑

**位置**: [model/client.py:176-216](phone_agent/model/client.py#L176-L216)

```python
def _parse_response(self, content: str) -> tuple[str, str]:
    """解析模型响应为思考和动作两部分"""

    # 规则1: 检测 finish(message=
    if "finish(message=" in content:
        parts = content.split("finish(message=", 1)
        thinking = parts[0].strip()
        action = "finish(message=" + parts[1]
        return thinking, action

    # 规则2: 检测 do(action=
    if "do(action=" in content:
        parts = content.split("do(action=", 1)
        thinking = parts[0].strip()
        action = "do(action=" + parts[1]
        return thinking, action

    # 规则3: 兼容旧版XML标签
    if "<answer>" in content:
        parts = content.split("<answer>", 1)
        thinking = parts[0].replace("<think>", "").replace("</think>", "").strip()
        action = parts[1].replace("</answer>", "").strip()
        return thinking, action

    # 规则4: 无标记，全部作为动作
    return "", content
```

### 4.3 ActionHandler 操作执行

#### 4.3.1 execute() 核心方法

**位置**: [actions/handler.py:45-88](phone_agent/actions/handler.py#L45-L88)

```python
def execute(self, action: dict[str, Any], screen_width: int, screen_height: int) -> ActionResult:
    """执行AI模型输出的动作"""

    # 1. 获取动作类型
    action_type = action.get("_metadata")

    # 2. 处理finish动作
    if action_type == "finish":
        return ActionResult(
            success=True,
            should_finish=True,
            message=action.get("message")
        )

    # 3. 验证动作类型
    if action_type != "do":
        return ActionResult(
            success=False,
            should_finish=True,
            message=f"Unknown action type: {action_type}"
        )

    # 4. 获取具体操作名称和处理器
    action_name = action.get("action")
    handler_method = self._get_handler(action_name)

    if handler_method is None:
        return ActionResult(
            success=False,
            should_finish=False,
            message=f"Unknown action: {action_name}"
        )

    # 5. 执行操作
    try:
        return handler_method(action, screen_width, screen_height)
    except Exception as e:
        return ActionResult(
            success=False,
            should_finish=False,
            message=f"Action failed: {e}"
        )
```

#### 4.3.2 操作处理器映射

**位置**: [actions/handler.py:90-108](phone_agent/actions/handler.py#L90-L108)

```python
def _get_handler(self, action_name: str) -> Callable | None:
    """根据操作名称获取对应的处理器方法"""
    handlers = {
        "Launch": self._handle_launch,
        "Tap": self._handle_tap,
        "Type": self._handle_type,
        "Type_Name": self._handle_type,
        "Swipe": self._handle_swipe,
        "Back": self._handle_back,
        "Home": self._handle_home,
        "Double Tap": self._handle_double_tap,
        "Long Press": self._handle_long_press,
        "Wait": self._handle_wait,
        "Take_over": self._handle_takeover,
        "Note": self._handle_note,
        "Call_API": self._handle_call_api,
        "Interact": self._handle_interact,
    }
    return handlers.get(action_name)
```

**设计模式**：策略模式（Strategy Pattern）

#### 4.3.3 关键操作处理器实现

**Tap操作处理**：
```python
def _handle_tap(self, action: dict, width: int, height: int) -> ActionResult:
    """处理点击操作"""
    element = action.get("element")
    if not element:
        return ActionResult(False, False, "No element coordinates")

    # 坐标转换（相对 -> 绝对）
    x, y = self._convert_relative_to_absolute(element, width, height)

    # 敏感操作确认
    if "message" in action:
        if not self.confirmation_callback(action["message"]):
            return ActionResult(
                success=False,
                should_finish=True,
                message="User cancelled sensitive operation"
            )

    # 执行点击
    device_factory = get_device_factory()
    device_factory.tap(x, y, self.device_id)
    return ActionResult(True, False)
```

**Type操作处理**：
```python
def _handle_type(self, action: dict, width: int, height: int) -> ActionResult:
    """处理文本输入"""
    text = action.get("text", "")
    device_factory = get_device_factory()

    # 1. 切换到ADB Keyboard
    original_ime = device_factory.detect_and_set_adb_keyboard(self.device_id)
    time.sleep(TIMING_CONFIG.action.keyboard_switch_delay)

    # 2. 清除现有文本
    device_factory.clear_text(self.device_id)
    time.sleep(TIMING_CONFIG.action.text_clear_delay)

    # 3. 输入新文本
    device_factory.type_text(text, self.device_id)
    time.sleep(TIMING_CONFIG.action.text_input_delay)

    # 4. 恢复原始输入法
    device_factory.restore_keyboard(original_ime, self.device_id)
    time.sleep(TIMING_CONFIG.action.keyboard_restore_delay)

    return ActionResult(True, False)
```

**关键点**：
- 自动切换输入法（Android）
- 时序控制（延迟等待）
- 状态恢复（恢复原输入法）

#### 4.3.4 坐标转换系统

**位置**: [actions/handler.py:110-116](phone_agent/actions/handler.py#L110-L116)

```python
def _convert_relative_to_absolute(
    self, element: list[int], screen_width: int, screen_height: int
) -> tuple[int, int]:
    """将相对坐标(0-1000)转换为绝对像素坐标"""
    x = int(element[0] / 1000 * screen_width)
    y = int(element[1] / 1000 * screen_height)
    return x, y
```

**示例**：
```
屏幕分辨率: 1080x1920
相对坐标: [500, 500] (屏幕中心)
绝对坐标: (540, 960)

相对坐标: [900, 100] (右上角)
绝对坐标: (972, 192)
```

**优势**：
- 适配不同分辨率
- 模型输出与设备无关
- 便于理解（0-1000范围）

### 4.4 DeviceFactory 工厂模式

#### 4.4.1 工厂实现

**位置**: [device_factory.py:15-140](phone_agent/device_factory.py#L15-L140)

```python
class DeviceFactory:
    def __init__(self, device_type: DeviceType = DeviceType.ADB):
        self.device_type = device_type
        self._module = None

    @property
    def module(self):
        """懒加载设备模块"""
        if self._module is None:
            if self.device_type == DeviceType.ADB:
                from phone_agent import adb
                self._module = adb
            elif self.device_type == DeviceType.HDC:
                from phone_agent import hdc
                self._module = hdc
            elif self.device_type == DeviceType.IOS:
                from phone_agent import xctest
                self._module = xctest
            else:
                raise ValueError(f"Unknown device type: {self.device_type}")
        return self._module

    def get_screenshot(self, device_id: str | None = None, timeout: int = 10):
        """统一的截图接口"""
        return self.module.get_screenshot(device_id, timeout)

    def tap(self, x: int, y: int, device_id: str | None = None, delay: float | None = None):
        """统一的点击接口"""
        return self.module.tap(x, y, device_id, delay)

    # ... 其他统一接口
```

**全局工厂实例**：
```python
# 全局单例
_device_factory: DeviceFactory | None = None

def set_device_type(device_type: DeviceType):
    """设置全局设备类型"""
    global _device_factory
    _device_factory = DeviceFactory(device_type)

def get_device_factory() -> DeviceFactory:
    """获取全局工厂实例"""
    global _device_factory
    if _device_factory is None:
        _device_factory = DeviceFactory(DeviceType.ADB)  # 默认ADB
    return _device_factory
```

**使用示例**：
```python
# 在main.py中设置设备类型
set_device_type(DeviceType.HDC)  # 切换到鸿蒙设备

# 在agent中使用统一接口
device_factory = get_device_factory()
screenshot = device_factory.get_screenshot()  # 自动调用HDC模块
```

---

## 数据流与执行流程

### 5.1 完整任务执行流程图

```
用户输入: "打开微信，给张三发送消息'今天晚上有空吗'"
                    ↓
┌────────────────────────────────────────────────────────┐
│ Step 1: 初始化                                         │
│  - 清空上下文                                           │
│  - 添加系统提示词                                       │
│  - 捕获当前屏幕（桌面）                                 │
│  - 构建消息: 用户任务 + 屏幕截图                       │
└────────────────────────────────────────────────────────┘
                    ↓
┌────────────────────────────────────────────────────────┐
│ Step 2: AI推理 (第1步)                                 │
│  - 模型接收: 系统提示词 + 任务 + 桌面截图             │
│  - 思考: "需要启动微信应用"                            │
│  - 动作: do(action="Launch", app="微信")               │
└────────────────────────────────────────────────────────┘
                    ↓
┌────────────────────────────────────────────────────────┐
│ Step 3: 执行动作                                       │
│  - ActionHandler解析动作                               │
│  - 查找微信包名: com.tencent.mm                        │
│  - 执行: adb shell am start com.tencent.mm             │
│  - 等待应用启动                                         │
└────────────────────────────────────────────────────────┘
                    ↓
┌────────────────────────────────────────────────────────┐
│ Step 4: 下一步推理 (第2步)                             │
│  - 捕获新屏幕（微信主界面）                             │
│  - 模型接收: 对话历史 + 新截图                         │
│  - 思考: "需要搜索联系人张三"                           │
│  - 动作: do(action="Tap", element=[900, 100])          │
│         (点击搜索图标)                                  │
└────────────────────────────────────────────────────────┘
                    ↓
┌────────────────────────────────────────────────────────┐
│ Step 5: 执行点击                                       │
│  - 转换坐标: [900,100] -> (972, 192)                   │
│  - 执行: adb shell input tap 972 192                   │
└────────────────────────────────────────────────────────┘
                    ↓
┌────────────────────────────────────────────────────────┐
│ Step 6: 推理 (第3步)                                   │
│  - 捕获新屏幕（搜索界面）                               │
│  - 思考: "需要输入'张三'进行搜索"                       │
│  - 动作: do(action="Type", text="张三")                │
└────────────────────────────────────────────────────────┘
                    ↓
┌────────────────────────────────────────────────────────┐
│ Step 7: 执行文本输入                                   │
│  - 切换到ADB Keyboard                                  │
│  - 清除现有文本                                         │
│  - 输入: adb shell am broadcast -a ADB_INPUT_TEXT      │
│         --es msg "张三"                                 │
│  - 恢复原输入法                                         │
└────────────────────────────────────────────────────────┘
                    ↓
┌────────────────────────────────────────────────────────┐
│ Step 8-N: 继续执行...                                  │
│  - 点击搜索结果                                         │
│  - 点击输入框                                           │
│  - 输入消息内容                                         │
│  - 点击发送按钮                                         │
└────────────────────────────────────────────────────────┘
                    ↓
┌────────────────────────────────────────────────────────┐
│ Step N: 完成                                           │
│  - 思考: "消息已发送，任务完成"                         │
│  - 动作: finish(message="已成功发送消息给张三")         │
│  - 返回结果                                             │
└────────────────────────────────────────────────────────┘
```

### 5.2 消息上下文演进

**第1步上下文**：
```json
[
  {
    "role": "system",
    "content": "你是一个手机操作助手，可以理解屏幕内容并执行操作..."
  },
  {
    "role": "user",
    "content": [
      {"type": "image_url", "image_url": "data:image/png;base64,..."},
      {"type": "text", "text": "打开微信，给张三发送消息\n\n{\"current_app\": \"桌面\"}"}
    ]
  }
]
```

**第2步上下文**（图像已移除）：
```json
[
  {"role": "system", "content": "..."},
  {"role": "user", "content": [{"type": "text", "text": "打开微信..."}]},
  {"role": "assistant", "content": "<think>需要启动微信...</think><answer>do(action=\"Launch\", app=\"微信\")</answer>"},
  {
    "role": "user",
    "content": [
      {"type": "image_url", "image_url": "data:image/png;base64,..."},
      {"type": "text", "text": "** Screen Info **\n\n{\"current_app\": \"微信\"}"}
    ]
  }
]
```

**上下文管理策略**：
1. 每步添加新的用户消息（屏幕信息）
2. 执行后立即移除图像内容
3. 保留文本内容维持对话历史
4. 避免上下文过长导致性能下降

### 5.3 性能指标流程

```
请求发送
    ↓
[开始计时] start_time = time.time()
    ↓
流式响应开始
    ↓
接收第一个Token
    ↓
[记录TTFT] time_to_first_token = time.time() - start_time
    ↓
继续接收Token并实时打印...
    ↓
检测到 "do(action=" 或 "finish(message="
    ↓
[记录思考结束] time_to_thinking_end = time.time() - start_time
    ↓
继续接收剩余Token（不再打印）
    ↓
响应完成
    ↓
[记录总时间] total_time = time.time() - start_time
    ↓
打印性能报告:
  - TTFT: 0.123s
  - 思考结束: 1.456s
  - 总时间: 2.789s
```

---

## 设计模式分析

### 6.1 工厂模式 (Factory Pattern)

**实现位置**: `DeviceFactory`

**UML类图**：
```
┌─────────────────┐
│  DeviceFactory  │
├─────────────────┤
│ - device_type   │
│ - _module       │
├─────────────────┤
│ + module()      │
│ + tap()         │
│ + swipe()       │
│ + screenshot()  │
└─────────────────┘
        △
        │ creates
        ├──────────┬──────────┬──────────┐
        ▼          ▼          ▼          ▼
    ┌─────┐    ┌─────┐    ┌────────┐
    │ adb │    │ hdc │    │ xctest │
    └─────┘    └─────┘    └────────┘
```

**优点**：
- 统一接口，隐藏平台差异
- 易于扩展新设备类型
- 解耦上层代码与具体实现

### 6.2 策略模式 (Strategy Pattern)

**实现位置**: `ActionHandler._get_handler()`

**结构**：
```
┌───────────────────┐
│  ActionHandler    │
├───────────────────┤
│ + execute()       │
│ - _get_handler()  │
└───────────────────┘
        │
        │ uses
        ▼
┌──────────────────────────────────────┐
│      Handler Method Strategies       │
├──────────────────────────────────────┤
│ - _handle_launch()                   │
│ - _handle_tap()                      │
│ - _handle_type()                     │
│ - _handle_swipe()                    │
│ - _handle_back()                     │
│ - ...                                │
└──────────────────────────────────────┘
```

**优点**：
- 易于添加新操作类型
- 每个操作独立封装
- 符合开闭原则

### 6.3 模板方法模式 (Template Method Pattern)

**实现位置**: `PhoneAgent.run()` 和 `_execute_step()`

**流程模板**：
```python
# run() 定义了任务执行的骨架
def run(self, task):
    初始化()
    第一步(task)
    while 未完成:
        下一步()
    返回结果()

# _execute_step() 定义了单步执行的骨架
def _execute_step(self, prompt, is_first):
    捕获屏幕()
    构建消息()
    调用模型()
    解析动作()
    执行动作()
    更新上下文()
    检查完成()
```

**优点**：
- 定义了稳定的执行流程
- 允许子类覆盖部分步骤
- 代码复用

### 6.4 观察者模式 (Observer Pattern)

**实现位置**: 回调函数机制

**结构**：
```
┌───────────────────┐
│  ActionHandler    │
├───────────────────┤
│ - confirmation_   │
│   callback        │
│ - takeover_       │
│   callback        │
└───────────────────┘
        │
        │ notifies
        ▼
┌──────────────────┐
│   Callbacks      │
├──────────────────┤
│ + confirm()      │
│ + takeover()     │
└──────────────────┘
```

**使用场景**：
```python
# 敏感操作确认
if "message" in action:
    if not self.confirmation_callback(action["message"]):
        return ActionResult(success=False, should_finish=True)

# 人工接管
def _handle_takeover(self, action, width, height):
    message = action.get("message", "User intervention required")
    self.takeover_callback(message)
    return ActionResult(True, False)
```

### 6.5 建造者模式 (Builder Pattern)

**实现位置**: `MessageBuilder`

**方法**：
```python
class MessageBuilder:
    @staticmethod
    def create_system_message(content: str) -> dict

    @staticmethod
    def create_user_message(text: str, image_base64: str | None) -> dict

    @staticmethod
    def create_assistant_message(content: str) -> dict

    @staticmethod
    def build_screen_info(current_app: str, **extra_info) -> str

    @staticmethod
    def remove_images_from_message(message: dict) -> dict
```

**优点**：
- 简化复杂对象构建
- 统一消息格式
- 易于维护和修改

---

## 扩展点与定制化

### 7.1 添加新设备类型

**步骤**：

1. **定义设备类型**（device_factory.py）：
```python
class DeviceType(Enum):
    ADB = "adb"
    HDC = "hdc"
    IOS = "ios"
    NEW_DEVICE = "new_device"  # 新增
```

2. **创建设备模块**（phone_agent/new_device/）：
```
phone_agent/new_device/
├── __init__.py
├── connection.py
├── device.py
├── input.py
└── screenshot.py
```

3. **实现必要接口**：
```python
# __init__.py
from .device import tap, swipe, back, home, launch_app
from .screenshot import get_screenshot
from .input import type_text, clear_text

# device.py
def tap(x, y, device_id=None, delay=None):
    # 实现点击逻辑
    pass

# ... 实现其他接口
```

4. **在工厂中注册**（device_factory.py）：
```python
@property
def module(self):
    if self._module is None:
        if self.device_type == DeviceType.ADB:
            from phone_agent import adb
            self._module = adb
        # ... 其他类型
        elif self.device_type == DeviceType.NEW_DEVICE:
            from phone_agent import new_device
            self._module = new_device
    return self._module
```

### 7.2 添加新操作类型

**步骤**：

1. **在handler中添加处理器方法**（actions/handler.py）：
```python
def _handle_custom_action(self, action: dict, width: int, height: int) -> ActionResult:
    """处理自定义操作"""
    # 实现操作逻辑
    param1 = action.get("param1")
    param2 = action.get("param2")

    # 调用设备工厂
    device_factory = get_device_factory()
    # ... 执行操作

    return ActionResult(True, False)
```

2. **在handler映射中注册**：
```python
def _get_handler(self, action_name: str) -> Callable | None:
    handlers = {
        "Launch": self._handle_launch,
        # ... 其他操作
        "Custom_Action": self._handle_custom_action,  # 新增
    }
    return handlers.get(action_name)
```

3. **更新系统提示词**（config/prompts_zh.py）：
```python
SYSTEM_PROMPT = """
...
可用操作:
1. Launch - 启动应用
...
12. Custom_Action - 自定义操作
   - 格式: do(action="Custom_Action", param1="...", param2="...")
   - 说明: 执行特定的自定义操作
...
"""
```

### 7.3 自定义系统提示词

**方法1：直接修改配置文件**

编辑 `phone_agent/config/prompts_zh.py`:
```python
SYSTEM_PROMPT = """
你是一个专业的手机操作助手...
[自定义内容]
"""
```

**方法2：运行时传入**

```python
custom_prompt = """
你是一个专注于电商操作的助手...
"""

agent_config = AgentConfig(
    system_prompt=custom_prompt,
    lang="cn"
)

agent = PhoneAgent(agent_config=agent_config)
```

### 7.4 自定义回调函数

**敏感操作确认**：
```python
def custom_confirmation(message: str) -> bool:
    """自定义确认逻辑"""
    # 例如：记录日志
    logger.info(f"Sensitive operation: {message}")

    # 例如：通过API远程确认
    response = requests.post("https://api.example.com/confirm",
                            json={"message": message})
    return response.json()["approved"]

    # 或：自动批准特定操作
    if "搜索" in message:
        return True  # 搜索操作自动批准
    return input(f"确认操作: {message}? (Y/N): ").upper() == "Y"
```

**人工接管**：
```python
def custom_takeover(message: str) -> None:
    """自定义接管逻辑"""
    # 发送通知
    send_notification(f"需要人工介入: {message}")

    # 暂停等待
    input(f"{message}\n完成后按Enter继续...")

    # 或：超时自动继续
    print(f"{message}\n等待30秒...")
    time.sleep(30)
```

**使用自定义回调**：
```python
agent = PhoneAgent(
    model_config=ModelConfig(),
    agent_config=AgentConfig(),
    confirmation_callback=custom_confirmation,
    takeover_callback=custom_takeover
)
```

### 7.5 添加新应用支持

**Android应用**（config/apps.py）：
```python
APP_PACKAGES = {
    # ... 现有应用
    "新应用名": "com.example.newapp",
    "自定义应用": "com.custom.app",
}
```

**HarmonyOS应用**（config/apps_harmonyos.py）：
```python
APP_PACKAGES = {
    # ... 现有应用
    "新鸿蒙应用": "com.example.harmonyapp",
}
```

**iOS应用**（config/apps_ios.py）：
```python
APP_PACKAGES = {
    # ... 现有应用
    "新iOS应用": "com.example.iosapp",
}
```

### 7.6 性能优化扩展点

**调整模型参数**：
```python
model_config = ModelConfig(
    base_url="http://localhost:8000/v1",
    model_name="autoglm-phone-9b",
    max_tokens=2000,        # 减少最大Token数
    temperature=0.1,        # 提高确定性
    top_p=0.9,             # 调整采样参数
    frequency_penalty=0.3,  # 减少重复
)
```

**调整时序配置**（config/timing.py）：
```python
TIMING_CONFIG = {
    "action": {
        "keyboard_switch_delay": 0.3,  # 加快键盘切换
        "text_input_delay": 0.2,       # 减少输入延迟
        "text_clear_delay": 0.1,       # 加快清除
        "keyboard_restore_delay": 0.3,
    }
}
```

**限制最大步数**：
```python
agent_config = AgentConfig(
    max_steps=50,  # 减少到50步
    verbose=False,  # 关闭详细输出
)
```

### 7.7 使用日志记录进行调试和分析 ⭐NEW

**日志记录默认启用**：

从最新版本开始，通过 `main.py` 运行 Phone Agent 时，**日志记录功能已默认启用**。每次执行任务都会自动记录到 `logs/` 目录。

**通过 CLI 使用日志**：

```bash
# 基本使用（日志自动启用）
python main.py "打开微信"

# 自定义日志目录
python main.py --log-dir my_logs "打开淘宝"

# 自定义会话名称
python main.py --session-name wechat_test "打开微信"

# 禁用日志（如果不需要）
python main.py --disable-logging "打开微信"

# iOS 设备同样支持
python main.py --device-type ios --session-name safari_test "Open Safari"
```

**新增的 CLI 参数**：

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--enable-logging` | flag | True | 启用执行日志记录 |
| `--disable-logging` | flag | False | 禁用执行日志记录 |
| `--log-dir` | string | "logs" | 日志文件目录 |
| `--session-name` | string | None | 自定义会话名称 |

**环境变量支持**：

```bash
# 通过环境变量配置默认日志目录
export PHONE_AGENT_LOG_DIR=my_logs
python main.py "打开微信"
```

---

**通过 Python API 使用日志**：

启用日志记录

日志记录功能可以帮助你：
- 调试任务执行过程
- 分析模型决策逻辑
- 追踪性能瓶颈
- 复现和排查问题
- 评估操作准确性

**基本用法**：
```python
from phone_agent import PhoneAgent, AgentConfig
from phone_agent.logger import LogConfig

# 最简单的启用方式
agent_config = AgentConfig(enable_logging=True)
agent = PhoneAgent(agent_config=agent_config)
agent.run("打开微信给张三发消息")

# 日志将自动保存在 logs/ 目录
# logs/20260109_143025_model.jsonl
# logs/20260109_143025_actions.jsonl
```

**自定义配置**：
```python
# 自定义日志配置
log_config = LogConfig(
    log_dir="experiment_logs",   # 自定义目录
    enable_model_log=True,        # 记录模型响应
    enable_action_log=True        # 记录操作序列
)

agent_config = AgentConfig(
    enable_logging=True,
    log_config=log_config,
    session_name="wechat_exp_01",  # 添加会话标识
    verbose=True
)

agent = PhoneAgent(agent_config=agent_config)
result = agent.run("测试任务")

# 获取日志信息
if agent.logger:
    summary = agent.logger.get_log_summary()
    print(f"会话ID: {summary['session_id']}")
    print(f"模型日志: {summary['model_log']}")
    print(f"操作日志: {summary['action_log']}")
    print(f"总步数: {summary.get('action_log_entries', 0) - 2}")  # 减去元数据和结束标记
```

**日志分析示例**：

1. **分析模型推理性能**：
```python
import json
from pathlib import Path

def analyze_performance(log_file):
    """分析模型性能指标"""
    ttfts = []
    thinking_times = []
    total_times = []

    with open(log_file, 'r', encoding='utf-8') as f:
        for line in f:
            entry = json.loads(line)
            if 'performance' in entry:
                perf = entry['performance']
                if perf['time_to_first_token']:
                    ttfts.append(perf['time_to_first_token'])
                if perf['time_to_thinking_end']:
                    thinking_times.append(perf['time_to_thinking_end'])
                if perf['total_time']:
                    total_times.append(perf['total_time'])

    print(f"平均TTFT: {sum(ttfts)/len(ttfts):.3f}s")
    print(f"平均思考时间: {sum(thinking_times)/len(thinking_times):.3f}s")
    print(f"平均总时间: {sum(total_times)/len(total_times):.3f}s")

analyze_performance("logs/20260109_143025_model.jsonl")
```

2. **分析操作序列**：
```python
def analyze_actions(log_file):
    """分析操作序列和成功率"""
    action_counts = {}
    success_count = 0
    total_count = 0

    with open(log_file, 'r', encoding='utf-8') as f:
        for line in f:
            entry = json.loads(line)
            if 'action' in entry and '_metadata' in entry['action']:
                action_type = entry['action'].get('action', 'unknown')
                action_counts[action_type] = action_counts.get(action_type, 0) + 1

                if entry['result']['success']:
                    success_count += 1
                total_count += 1

    print("操作统计:")
    for action, count in action_counts.items():
        print(f"  {action}: {count}次")
    print(f"\n成功率: {success_count}/{total_count} = {success_count/total_count*100:.1f}%")

analyze_actions("logs/20260109_143025_actions.jsonl")
```

3. **重放任务执行过程**：
```python
def replay_task(model_log, action_log):
    """重放任务执行过程"""
    import json

    print("=" * 60)
    print("任务重放")
    print("=" * 60)

    with open(action_log, 'r', encoding='utf-8') as f:
        for line in f:
            entry = json.loads(line)

            if entry.get('event') == 'task_start':
                print(f"\n📋 任务: {entry['task']}")
                print(f"⏰ 开始时间: {entry['timestamp']}")

            elif 'step' in entry and 'action' in entry:
                step = entry['step']
                action = entry['action']
                result = entry['result']
                screen = entry['screen_info']

                print(f"\n--- Step {step} ---")
                print(f"📱 屏幕: {screen.get('current_app', 'Unknown')}")
                print(f"🎯 操作: {action.get('action', 'Unknown')}")
                if action.get('action') == 'Launch':
                    print(f"   应用: {action.get('app')}")
                elif action.get('action') == 'Tap':
                    print(f"   坐标: {action.get('element')}")
                elif action.get('action') == 'Type':
                    print(f"   文本: {action.get('text')}")
                print(f"✅ 成功: {result['success']}")

            elif entry.get('event') == 'task_end':
                print(f"\n{'='*60}")
                print(f"🏁 任务{'成功' if entry['success'] else '失败'}: {entry.get('message', '')}")
                print(f"📊 总步数: {entry['total_steps']}")
                print(f"⏰ 结束时间: {entry['timestamp']}")
                print(f"{'='*60}")

replay_task(
    "logs/20260109_143025_model.jsonl",
    "logs/20260109_143025_actions.jsonl"
)
```

**日志用途**：
- **调试**：查看每步的思考过程和操作决策
- **性能优化**：分析TTFT和推理时间，优化模型配置
- **质量评估**：统计操作成功率，识别常见失败场景
- **任务复现**：根据日志重放任务执行过程
- **数据分析**：收集数据用于模型训练或改进提示词

---

## 附录

### A. 核心文件清单

| 文件路径 | 行数 | 功能 |
|---------|------|------|
| phone_agent/agent.py | 254 | Android/HarmonyOS Agent |
| phone_agent/agent_ios.py | ~250 | iOS Agent |
| phone_agent/device_factory.py | 168 | 设备工厂 |
| phone_agent/actions/handler.py | 400 | 操作处理器 |
| phone_agent/actions/handler_ios.py | 280 | iOS操作处理器 |
| phone_agent/model/client.py | 291 | AI模型客户端 |
| phone_agent/logger.py | ~200 | 日志记录器 ⭐NEW |
| phone_agent/config/prompts_zh.py | 146 | 中文提示词 |
| phone_agent/config/prompts_en.py | 79 | 英文提示词 |

### B. 依赖关系图

```
PhoneAgent
  ├─ depends on → ModelClient
  ├─ depends on → ActionHandler
  ├─ depends on → AgentLogger ⭐NEW
  │   └─ depends on → LogConfig
  ├─ depends on → ActionHandler
  │   └─ depends on → DeviceFactory
  │       ├─ uses → adb (动态加载)
  │       ├─ uses → hdc (动态加载)
  │       └─ uses → xctest (动态加载)
  └─ depends on → MessageBuilder

Config Layer (被所有模块使用)
  ├─ apps.py
  ├─ prompts.py
  ├─ timing.py
  └─ i18n.py
```

### C. 关键术语表

| 术语 | 解释 |
|------|------|
| ADB | Android Debug Bridge，Android设备调试工具 |
| HDC | HarmonyOS Device Connector，鸿蒙设备调试工具 |
| WebDriverAgent | iOS自动化测试框架 |
| VLM | Vision-Language Model，视觉语言模型 |
| TTFT | Time To First Token，首Token时间 |
| CoT | Chain of Thought，思维链 |
| IME | Input Method Editor，输入法 |
| Base64 | 二进制数据编码方式 |
| JSONL | JSON Lines，每行一个JSON对象的文件格式 |

### D. 常见问题

**Q: 如何切换设备类型？**
```python
from phone_agent.device_factory import set_device_type, DeviceType
set_device_type(DeviceType.HDC)  # 切换到鸿蒙
```

**Q: 如何使用远程设备？**
```python
# WiFi连接
adb connect 192.168.1.100:5555
# 然后正常使用
agent = PhoneAgent()
agent.run("打开微信")
```

**Q: 如何调试单步执行？**
```python
agent = PhoneAgent()
result = agent.step("打开微信")
print(result.thinking)
print(result.action)
# 继续下一步
result = agent.step()
```

**Q: 如何启用日志记录？** ⭐NEW

**方法1: 通过 CLI（推荐，默认启用）**
```bash
# 从最新版本开始，main.py 默认启用日志记录
python main.py "打开微信"  # 日志自动保存到 logs/ 目录

# 自定义日志配置
python main.py --log-dir my_logs --session-name test "打开微信"

# 禁用日志
python main.py --disable-logging "打开微信"

# iOS 设备
python main.py --device-type ios --session-name ios_test "Open Safari"
```

**方法2: 通过 Python API**
```python
from phone_agent import PhoneAgent, AgentConfig
from phone_agent.logger import LogConfig

# 基本用法
agent_config = AgentConfig(
    enable_logging=True,
    session_name="my_test"
)
agent = PhoneAgent(agent_config=agent_config)
agent.run("打开微信")

# 高级配置
log_config = LogConfig(
    log_dir="my_logs",       # 自定义日志目录
    enable_model_log=True,   # 启用模型日志
    enable_action_log=True   # 启用操作日志
)

agent_config = AgentConfig(
    enable_logging=True,
    log_config=log_config,
    session_name="detailed_test"
)
agent = PhoneAgent(agent_config=agent_config)

# 获取日志摘要
if agent.logger:
    summary = agent.logger.get_log_summary()
    print(f"Model log: {summary['model_log']}")
    print(f"Action log: {summary['action_log']}")
```

**iOS 设备同样支持日志记录**：
```python
from phone_agent.agent_ios import IOSPhoneAgent, IOSAgentConfig
from phone_agent.logger import LogConfig

agent_config = IOSAgentConfig(
    enable_logging=True,
    log_config=LogConfig(log_dir="ios_logs"),
    session_name="ios_test"
)
agent = IOSPhoneAgent(agent_config=agent_config)
agent.run("Open Safari")
```

**Q: 如何分析日志文件？** ⭐NEW
```python
import json

# 读取模型日志
with open("logs/20260109_143025_my_test_model.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        entry = json.loads(line)
        if "step" in entry:
            print(f"Step {entry['step']}:")
            print(f"  Thinking: {entry['thinking'][:50]}...")
            print(f"  Action: {entry['action']}")
            print(f"  TTFT: {entry['performance']['time_to_first_token']}s")

# 读取操作日志
with open("logs/20260109_143025_my_test_actions.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        entry = json.loads(line)
        if "action" in entry:
            print(f"Step {entry['step']}: {entry['action']['action']}")
            print(f"  Success: {entry['result']['success']}")
            print(f"  Screen: {entry['screen_info']['current_app']}")
```

---

**文档版本**: 1.2 ⭐重要更新
**更新内容**:
- 新增日志记录功能
- main.py 默认启用日志记录
- iOS 设备支持完整日志功能
- 新增 CLI 日志参数（--log-dir, --session-name, --disable-logging）
**生成时间**: 2026-01-10
**适用版本**: Open-AutoGLM v1.x
