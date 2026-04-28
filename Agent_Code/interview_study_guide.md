# 简历面试学习指南

> 基于周子璇简历涉及的全部技术栈，按模块逐步学习，覆盖面试高频考点。
> 学习顺序：模块四(网络+OS) → 模块一(Java) → 模块五(FastAPI+设计模式) → 模块二(MySQL) → 模块六(测试) → 模块三(AI/Agent/RAG)

---

## 目录

- [模块四：计算机网络 + 操作系统](#模块四计算机网络--操作系统)
  - [4.1 TCP/UDP 协议](#41-tcpudp-协议)
  - [4.2 HTTP/HTTPS 协议](#42-httphttps-协议)
  - [4.3 进程与线程](#43-进程与线程)
  - [4.4 Git 基础](#44-git-基础)
- [模块一：Java 基础](#模块一java-基础)
- [模块五：后端开发 + 设计模式](#模块五后端开发--设计模式)
- [模块二：MySQL 数据库](#模块二mysql-数据库)
- [模块六：测试技术](#模块六测试技术)
  - [6.1 pytest 测试框架](#61-pytest-测试框架)
  - [6.2 requests 库](#62-requests-库--http-接口测试)
  - [6.3 Allure 测试报告](#63-allure-测试报告)
  - [6.4 YAML 驱动测试](#64-yaml-驱动测试数据驱动)
  - [6.5 功能测试方法](#65-功能测试方法)
  - [6.6 日志与 Jenkins CI](#66-日志与-jenkins-ci)
- [模块三：AI / Agent / RAG](#模块三ai--agent--rag)
  - [3.1 大语言模型（LLM）基础](#31-大语言模型llm基础)
  - [3.2 RAG 与 GraphRAG](#32-rag-与-graphrag)
  - [3.3 Neo4j 图数据库](#33-neo4j-图数据库)
  - [3.4 FAISS 向量检索](#34-faiss-向量检索)
  - [3.5 LangChain + LangGraph](#35-langchain--langgraph)
  - [3.6 Multi-Agent 多智能体架构](#36-multi-agent-多智能体架构)
  - [3.7 意图识别 + Map-Reduce 并行](#37-意图识别--map-reduce-并行)
  - [3.8 语义缓存 + 滑动窗口](#38-语义缓存--滑动窗口)

---

# 模块四：计算机网络 + 操作系统

## 4.1 TCP/UDP 协议

### 一、TCP 和 UDP 的本质区别

| 特性 | TCP | UDP |
|------|-----|-----|
| 连接 | 面向连接（先建立连接再传数据） | 无连接（直接发） |
| 可靠性 | 可靠传输（确认+重传） | 不可靠（发完就不管了） |
| 速度 | 较慢（有控制开销） | 快（没有额外开销） |
| 数据顺序 | 保证有序 | 不保证 |
| 数据边界 | 无边界（字节流） | 有边界（数据报） |
| 适用场景 | 网页、文件传输、邮件 | 视频直播、DNS查询、游戏 |

> **面试一句话总结：** "TCP是面向连接的可靠字节流传输协议，UDP是无连接的不可靠数据报协议。TCP保证数据有序可靠但速度较慢，UDP速度快但不保证可靠性。"

### 二、TCP 三次握手

#### 完整流程

```
客户端(Client)                          服务器(Server)
    |                                      |
    |  ① SYN=1, seq=x                     |
    |  ─────────────────────────────────>  |  (Server进入 SYN_RCVD 状态)
    |                                      |
    |  ② SYN=1, ACK=1, seq=y, ack=x+1     |
    |  <─────────────────────────────────  |
    |                                      |
    |  ③ ACK=1, seq=x+1, ack=y+1          |
    |  ─────────────────────────────────>  |  (连接建立，进入 ESTABLISHED)
    |                                      |
```

#### 关键字段解释

| 字段 | 全称 | 含义 |
|------|------|------|
| SYN | Synchronize | "我想跟你建立连接" |
| ACK | Acknowledge | "我收到了" |
| seq | sequence number | 数据包的序号 |
| ack | acknowledgement number | 期望收到的下一个序号 |

#### 三步分别做了什么

| 步骤 | 动作 | 含义 |
|------|------|------|
| 第一次 | 客户端 → 服务器：发SYN | "你好，我想连接你" |
| 第二次 | 服务器 → 客户端：回SYN+ACK | "好的，我也想连接你，并且收到了你的请求" |
| 第三次 | 客户端 → 服务器：发ACK | "好的，确认你的回复，连接建立" |

#### 为什么是三次？（面试必问）

> **核心原因：防止已失效的连接请求到达服务器，导致服务器误建连接并白白浪费资源。**

具体场景：客户端发了一个SYN请求，但在网络中滞留了很久才到达服务器。客户端以为丢了已经关闭了这个连接。但服务器收到了这个"迟到"的SYN，如果只有两次握手，服务器就直接建立连接等待数据了——但客户端根本不会发数据，服务器就傻等了。

有了第三次握手：服务器回了SYN+ACK之后，客户端发现"我没想建立连接啊"，就不会回第三个ACK，服务器也就不会建立这个无效连接。

> **面试回答模板：** "三次握手是为了确认双方的发送和接收能力都正常。第一次握手服务器确认客户端能发，第二次握手客户端确认服务器能收能发，第三次握手服务器确认客户端能收。同时防止历史重复连接的初始化，避免服务器资源浪费。"

### 三、TCP 四次挥手

#### 完整流程

```
客户端(Client)                          服务器(Server)
    |                                      |
    |  ① FIN=1, seq=u                     |
    |  ─────────────────────────────────>  |  (Server进入 CLOSE_WAIT)
    |                                      |
    |  ② ACK=1, seq=v, ack=u+1            |
    |  <─────────────────────────────────  |  (Client进入 FIN_WAIT_2)
    |                                      |
    |    ... 服务器可能还有数据要发 ...       |
    |                                      |
    |  ③ FIN=1, ACK=1, seq=w, ack=u+1     |
    |  <─────────────────────────────────  |  (Client进入 TIME_WAIT)
    |                                      |
    |  ④ ACK=1, seq=u+1, ack=w+1          |
    |  ─────────────────────────────────>  |  (Server进入 CLOSED)
    |                                      |
    |  等待 2MSL 后 → CLOSED                |
```

#### 为什么是四次而不是三次？

因为TCP是**全双工通信**（双方都能同时发数据）。当客户端说"我不想发了"（FIN），服务器说"知道了"（ACK），但**服务器可能还有数据没发完**，所以不能立刻也发FIN。等服务器数据发完了，再发自己的FIN。

简单类比：
- 客户端："我说完了" (FIN) → 服务器："好的你说了" (ACK) → 服务器继续说没说完的话... → 服务器："我也说完了" (FIN) → 客户端："好的" (ACK)

#### TIME_WAIT 状态（面试常问）

客户端发完最后一个ACK后，不是直接关闭，而是进入 **TIME_WAIT** 状态，等待 **2MSL**（Maximum Segment Lifetime，报文最大生存时间，一般2分钟）。

**为什么等待2MSL？两个原因：**

1. **确保最后一个ACK能到达服务器**：如果ACK丢了，服务器会重发FIN，客户端还能重发ACK。如果客户端直接关了，服务器就一直收不到ACK，无法正常关闭。
2. **让本连接的所有报文都在网络中消失**：防止新连接收到旧连接的延迟报文。

### 四、TCP 可靠传输的四大机制

#### 1. 滑动窗口（流量控制）

```
发送方窗口：
[已确认] [已发送未确认] [可以发送] [不能发送]
                   ←── 窗口大小 ──→
```

- 接收方通过 **Window Size** 告诉发送方"我还能接收多少数据"
- 窗口大小动态调整，接收方处理不过来就把窗口缩小（甚至为0，叫**零窗口**）
- **目的：防止发送方发太快，接收方处理不过来**

#### 2. 拥塞控制（网络层面的控制）

| 阶段 | 算法 | 说明 |
|------|------|------|
| 慢启动 | Slow Start | 初始cwnd=1，每收到一个ACK翻倍增长（指数增长） |
| 拥塞避免 | Congestion Avoidance | cwnd达到慢启动阈值后，每轮+1（线性增长） |
| 快重传 | Fast Retransmit | 收到3个重复ACK，立刻重传（不等超时） |
| 快恢复 | Fast Recovery | 快重传后，cwnd减半而不是回到1 |

简记口诀："先翻倍增长，到阈值后慢慢涨，连收3个重复ACK赶紧重传，然后减半继续"

#### 3. 超时重传

发出去的数据如果在一定时间内没收到ACK，就重新发。

#### 4. 校验和

每个TCP报文都有校验和，接收方验证数据是否损坏。

### 五、面试高频 Q&A

**Q1：TCP和UDP的区别？**

> TCP面向连接、可靠、有序、有流量控制和拥塞控制；UDP无连接、不可靠、无序、无控制。TCP适合要求可靠性的场景（HTTP/FTP），UDP适合实时性要求高的场景（视频/DNS）。

**Q2：三次握手为什么不能是两次？**

> 两次握手无法防止已失效的SYN到达服务器导致误建连接。第三次握手让服务器确认客户端确实想建立连接。

**Q3：四次挥手中TIME_WAIT是什么？为什么需要？**

> 主动关闭方在发完最后一个ACK后等待2MSL的时间。两个原因：①确保最后的ACK能到达对方（如果丢了对方会重发FIN）；②让旧连接的报文在网络中消失，避免影响新连接。

**Q4：TCP怎么保证可靠传输？**

> 四大机制：校验和（检测数据损坏）、超时重传（丢失重发）、滑动窗口（流量控制）、拥塞控制（防止网络拥塞）。

---

## 4.2 HTTP/HTTPS 协议

### 一、HTTP 是什么

HTTP（HyperText Transfer Protocol）是应用层协议，定义了**客户端和服务器之间如何交换数据**。

```
客户端(浏览器)  ——HTTP请求——>  服务器
客户端(浏览器)  <——HTTP响应——  服务器
```

本质就是：请求-响应模型，客户端主动发，服务器被动回。

### 二、HTTP 请求方法

| 方法 | 用途 | 幂等性 | 安全性 |
|------|------|--------|--------|
| GET | 获取资源 | 幂等 | 安全（不修改数据） |
| POST | 创建资源/提交数据 | 非幂等 | 不安全 |
| PUT | 全量更新资源 | 幂等 | 不安全 |
| DELETE | 删除资源 | 幂等 | 不安全 |
| PATCH | 部分更新 | 非幂等 | 不安全 |

> **幂等** = 同一个请求执行一次和执行多次，效果一样。比如GET获取用户信息，请求100次结果一样。POST下单就不行，请求100次就下100单。

### 三、GET vs POST（面试最高频）

| 区别 | GET | POST |
|------|-----|------|
| 参数位置 | URL中（?key=value） | 请求体Body中 |
| 数据长度 | URL有长度限制（浏览器约2KB） | Body无限制 |
| 安全性 | 参数暴露在URL中，不安全 | 相对安全 |
| 缓存 | 浏览器会缓存 | 不会缓存 |
| 幂等性 | 幂等 | 非幂等 |
| 本质区别 | 都是HTTP请求，TCP连接没有区别。区别在于语义约定和服务器处理方式不同 |

> **面试一句话：** "GET和POST本质都是HTTP请求，底层TCP连接没有区别。主要区别是GET参数在URL中，POST在Body中；GET幂等可缓存，POST非幂等不缓存。"

### 四、HTTP 状态码（面试必背）

#### 核心分类

| 范围 | 类别 | 含义 |
|------|------|------|
| 1xx | 信息 | 请求已接收，继续处理 |
| 2xx | 成功 | 请求已成功处理 |
| 3xx | 重定向 | 需要进一步操作 |
| 4xx | 客户端错误 | 客户端请求有问题 |
| 5xx | 服务器错误 | 服务器处理出错 |

#### 必须记住的具体状态码

| 状态码 | 含义 | 常见场景 |
|--------|------|----------|
| 200 | OK 成功 | 正常返回数据 |
| 301 | 永久重定向 | 网站换域名了 |
| 302 | 临时重定向 | 未登录跳转登录页 |
| 304 | 未修改(缓存) | 浏览器缓存还有效 |
| 400 | 请求语法错误 | 参数格式不对 |
| 401 | 未认证 | 没带Token/没登录 |
| 403 | 禁止访问 | 没权限（登录了但不够格） |
| 404 | 找不到资源 | URL写错了 |
| 500 | 服务器内部错误 | 代码抛异常了 |
| 502 | 网关错误 | Nginx连不上后端 |
| 503 | 服务不可用 | 服务器过载/维护 |

**面试重点区分 301 vs 302：**

- 301永久重定向：搜索引擎会把权重转到新地址，浏览器会缓存
- 302临时重定向：搜索引擎不会转移权重，浏览器不缓存

**面试重点区分 401 vs 403：**

- 401：你**没登录**，我不知道你是谁
- 403：你**登录了但没权限**，我知道你是谁但你不能做这个操作

### 五、HTTP 请求/响应结构

#### 请求结构

```text
POST /api/user/login HTTP/1.1          ← 请求行(方法 URL 版本)
Host: www.example.com                   ← 请求头
Content-Type: application/json
Authorization: Bearer eyJhbGci...
Cookie: session_id=abc123
                                       ← 空行分隔
{"username":"admin","password":"123"}   ← 请求体
```

#### 响应结构

```text
HTTP/1.1 200 OK                         ← 状态行(版本 状态码 原因)
Content-Type: application/json          ← 响应头
Set-Cookie: session_id=abc123
                                       ← 空行分隔
{"code":0,"message":"success","data":{}} ← 响应体
```

### 六、HTTP/1.0 → HTTP/1.1 → HTTP/2.0

| 特性 | HTTP/1.0 | HTTP/1.1 | HTTP/2.0 |
|------|----------|----------|----------|
| 连接 | 每次请求新建TCP连接 | 默认keep-alive长连接 | 多路复用 |
| 队头阻塞 | 有 | 有（TCP层面） | 解决了（HTTP层面） |
| 并发请求 | 串行 | 浏览器限制6-8个并发 | 无限制（二进制帧） |
| 头部压缩 | 无 | 无 | HPACK压缩 |
| 服务器推送 | 无 | 无 | 支持 |

#### 关键概念解释

**长连接（Keep-Alive）：** HTTP/1.0每次请求都要三次握手建立连接，用完就断。HTTP/1.1默认保持TCP连接不关，多个请求复用同一个连接。

**队头阻塞（Head-of-Line Blocking）：** HTTP/1.1中，一个TCP连接上，前面的请求没处理完，后面的就得等着。HTTP/2.0通过**二进制帧**把请求拆成小块，多个请求交替传输，互不阻塞。

**多路复用：** HTTP/2.0在同一个TCP连接上同时传输多个请求和响应，每个请求用**Stream ID**标识。

### 七、HTTPS = HTTP + TLS/SSL（面试高频）

#### HTTP为什么不安全？

HTTP是**明文传输**，数据在网络上裸奔：可以被**窃听**、**篡改**、**冒充**。

#### HTTPS加了什么？

HTTPS在HTTP和TCP之间加了一层 **TLS（Transport Layer Security）** 协议，提供三个保障：

- **加密**：数据加密传输，窃听者看不懂
- **完整性**：数据没被篡改
- **身份验证**：确认服务器是真的

#### TLS 握手流程（简化版面试回答）

```
客户端                              服务器
  |                                    |
  | ① Client Hello                     |
  |  (支持的TLS版本、加密套件列表、      |
  |   随机数random1)                    |
  | ─────────────────────────────────> |
  |                                    |
  | ② Server Hello                     |
  |  (选定TLS版本、加密套件、            |
  |   随机数random2、服务器证书)         |
  | <───────────────────────────────── |
  |                                    |
  | ③ 客户端验证证书                    |
  |  (CA机构签名验证，确认服务器身份)    |
  |                                    |
  | ④ 客户端生成预主密钥                |
  |  (random3，用服务器公钥加密发送)     |
  | ─────────────────────────────────> |
  |                                    |
  | ⑤ 双方用random1+random2+random3    |
  |    生成对称密钥(会话密钥)           |
  |                                    |
  | ⑥ 之后所有通信用对称密钥加密        |
```

> **面试回答模板：** "HTTPS在HTTP基础上加了TLS层。TLS握手时，客户端和服务器交换三个随机数，用非对称加密（RSA）安全地协商出一个对称密钥。之后的通信都用这个对称密钥加密。用非对称加密是为了安全地传递密钥，用对称加密是因为速度快。"

#### 对称加密 vs 非对称加密

|  | 对称加密 | 非对称加密 |
|--|---------|-----------|
| 原理 | 加密和解密用同一个密钥 | 公钥加密，私钥解密（反过来也行） |
| 速度 | 快 | 慢 |
| 代表 | AES | RSA |
| 用途 | 传数据（量大要快） | 传密钥（量小要安全） |

### 八、Cookie vs Session vs Token（面试必问）

|  | Cookie | Session | Token (JWT) |
|--|--------|---------|-------------|
| 存储位置 | 客户端浏览器 | 服务器端 | 客户端(localStorage) |
| 工作原理 | 服务器Set-Cookie，浏览器自动携带 | 服务器存Session，给客户端SessionID | 服务器签发Token，客户端每次请求带上 |
| 跨域 | 不支持(同源策略) | 依赖Cookie，同源限制 | 支持（无状态，放Header里） |
| 安全性 | 较低(可伪造) | 较高(数据在服务器) | 较高(签名防篡改) |
| 扩展性 | 差 | 差(分布式要共享Session) | 好(无状态，天然支持分布式) |
| 适用场景 | 简单状态保持 | 传统Web应用 | 前后端分离/API/移动端 |

#### JWT（JSON Web Token）工作流程

```
① 客户端发送 用户名+密码
② 服务器验证通过，生成JWT返回给客户端
③ 客户端把JWT存在localStorage
④ 之后每次请求在Header中带上: Authorization: Bearer <token>
⑤ 服务器验证JWT签名，解析出用户信息
```

#### JWT 结构

```text
eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhZG1pbiJ9.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
|----- Header -----|  |--- Payload ---|  |--- Signature ---|
   (算法+类型)         (用户数据)          (签名，防篡改)
```

三部分用 `.` 分隔，每部分都是 Base64 编码。**Signature** 是用 Header + Payload + 密钥 通过指定算法（如HS256）生成的，所以篡改Payload会导致签名验证失败。

### 九、面试高频 Q&A

**Q1：HTTP和HTTPS的区别？**

> HTTP明文传输端口80，HTTPS加密传输端口443。HTTPS在HTTP和TCP之间加了TLS层，通过非对称加密协商对称密钥，再用对称密钥加密数据。

**Q2：GET和POST的区别？**

> GET参数在URL中，有长度限制，幂等可缓存；POST参数在Body中，无长度限制，非幂等不缓存。底层都是TCP连接，没有本质区别。

**Q3：Cookie、Session、Token的区别？**

> Cookie存在浏览器端，Session存在服务器端（通过Cookie传SessionID），Token存在客户端（每次请求放Header里）。Token无状态支持分布式，适合前后端分离。

**Q4：HTTP/1.1和HTTP/2.0的区别？**

> HTTP/2.0支持多路复用（一个连接并发多个请求）、头部压缩（HPACK）、二进制帧传输、服务器推送，解决了HTTP/1.1的队头阻塞问题。

---

## 4.3 进程与线程

### 一、核心概念：进程、线程、协程

#### 1. 进程（Process）

**定义：** 进程是操作系统**资源分配的最小单位**，是程序的一次执行过程。

类比理解：进程就像一个**工厂**，有自己独立的厂房（内存空间）、设备（文件资源）、工人。

#### 2. 线程（Thread）

**定义：** 线程是操作系统**CPU调度的最小单位**，是进程中的一条执行流。

类比理解：线程是工厂里的**工人**，多个工人共享同一个工厂的资源，但各自干各自的活。

#### 3. 协程（Coroutine）

**定义：** 用户态的轻量级线程，由**程序自己控制切换**，不需要操作系统介入。

类比理解：协程是一个工人**自己切换任务**——先写报表写一半，去接个电话，打完电话回来继续写报表。切换由程序控制，不需要经理（操作系统）干预。

#### 三者对比（面试必背）

| 特性 | 进程 | 线程 | 协程 |
|------|------|------|------|
| 资源 | 独立内存空间 | 共享进程内存 | 共享线程内存 |
| 切换开销 | 大（需要切换内存空间） | 中（不需要切换内存空间） | 小（用户态切换） |
| 通信 | 需要IPC机制 | 直接共享内存（但要加锁） | 直接共享内存 |
| 调度者 | 操作系统 | 操作系统 | 程序自身 |
| 创建数量 | 少（开销大） | 中 | 多（几十万都行） |
| Python体现 | multiprocessing | threading | asyncio |

> **面试一句话：** "进程是资源分配的最小单位，线程是CPU调度的最小单位，协程是用户态的轻量级线程。进程间内存隔离需要IPC通信，线程间共享内存但需要同步，协程由程序控制切换开销最小。"

### 二、进程间通信（IPC）

进程内存是隔离的，A进程不能直接访问B进程的内存，所以需要IPC机制：

| 方式 | 原理 | 特点 | 类比 |
|------|------|------|------|
| 管道(Pipe) | 半双工，父子进程间传递字节流 | 单向、亲缘关系 | 一根水管，水只能往一个方向流 |
| 命名管道(FIFO) | 文件系统中的特殊文件 | 无亲缘关系也能用 | 公共水管，任何人都能接 |
| 消息队列 | 内核维护的消息链表 | 有格式、可按类型读取 | 快递柜，按编号取件 |
| 共享内存 | 多个进程映射同一块内存 | 速度最快，需要同步 | 共享白板，都能读写 |
| 信号量(Semaphore) | 计数器，控制并发访问 | 用于同步，常配合共享内存 | 停车场车位计数牌 |
| 信号(Signal) | 通知进程某个事件发生 | 只能传递信号编号 | 门铃——只知道有人按，不知道具体内容 |
| Socket | 网络通信接口 | 可跨机器通信 | 电话，远程也能交流 |

> **面试重点：共享内存** 是最快的IPC方式，因为进程直接读写内存，不需要内核空间和用户空间之间的数据拷贝。但多个进程同时写会冲突，需要配合**信号量**做同步。

### 三、死锁（Deadlock）

#### 什么是死锁

两个或多个进程/线程互相等待对方释放资源，导致大家都卡住永远无法继续。

```
线程A：拿着锁1，等锁2
线程B：拿着锁2，等锁1
→ 双方都在等对方，永远等不到 → 死锁！
```

#### 死锁的四个必要条件（面试必背）

| 条件 | 含义 | 破坏方法 |
|------|------|----------|
| 互斥 | 资源同时只能被一个线程使用 | 无法破坏（锁的本质就是互斥） |
| 持有并等待 | 持有已有资源的同时等待新资源 | 一次性申请所有资源 |
| 不可剥夺 | 已获得的资源不能被强行抢走 | 超时释放/优先级抢占 |
| 循环等待 | A等B，B等C，C等A形成环路 | 按顺序加锁 |

> **面试口诀：互持不循（互斥、持有并等待、不可剥夺、循环等待）**

#### 如何避免死锁

**实际开发中最常用的方法——固定加锁顺序：**

```python
# 错误示范：可能导致死锁
def transfer(account_from, account_to, amount):
    lock(account_from)       # 先锁转出账户
    lock(account_to)         # 再锁转入账户
    # 如果同时有反向转账，就会死锁！

# 正确做法：按固定顺序加锁（比如按账户ID排序）
def transfer(account_from, account_to, amount):
    first  = min(account_from.id, account_to.id)
    second = max(account_from.id, account_to.id)
    lock(first)              # 永远先锁ID小的
    lock(second)             # 再锁ID大的
    # 这样不管谁先调用，加锁顺序都一样，不会循环等待
```

其他避免方法：

- **设置超时**：`tryLock(timeout)`，锁等太久就放弃
- **死锁检测**：定期检查资源分配图是否有环

### 四、多线程的同步机制

多线程共享内存，同时操作同一份数据会出问题，所以需要同步：

| 机制 | 作用 | 场景 |
|------|------|------|
| synchronized (Java) / Lock (Python) | 互斥锁，同一时刻只有一个线程进入临界区 | 保护共享变量 |
| volatile (Java) | 保证变量的可见性（一个线程修改，其他线程立刻看到） | 状态标志位 |
| 信号量(Semaphore) | 控制同时访问的线程数量 | 连接池（最多5个连接） |
| 读写锁 | 读共享、写独占 | 配置信息（读多写少） |

#### 经典问题：生产者-消费者模型

```python
import threading
import queue

buffer = queue.Queue(maxsize=10)  # 缓冲区大小10

def producer():
    for i in range(100):
        buffer.put(i)        # 队列满时自动阻塞等待
        print(f"生产: {i}")

def consumer():
    while True:
        item = buffer.get()  # 队列空时自动阻塞等待
        print(f"消费: {item}")

# 生产者放数据，消费者取数据
# 队列满→生产者等待；队列空→消费者等待
```

> **面试一句话：** "生产者-消费者模式通过共享缓冲区解耦生产和消费，用锁和条件变量保证线程安全，队列满时生产者阻塞，队列空时消费者阻塞。"

### 五、Python 中的并发（async/await，主人的项目核心）

#### threading（多线程）

```python
import threading

def task(name):
    print(f"线程{name}开始")

t1 = threading.Thread(target=task, args=("A",))
t2 = threading.Thread(target=task, args=("B",))
t1.start()
t2.start()
t1.join()   # 等待t1完成
t2.join()   # 等待t2完成
```

#### asyncio（协程，主人的FastAPI项目核心）

```python
import asyncio

async def fetch_data(url):
    print(f"开始请求 {url}")
    await asyncio.sleep(1)    # 模拟IO等待，不阻塞其他协程
    print(f"完成请求 {url}")
    return f"data from {url}"

async def main():
    # 并发执行3个请求，总耗时约1秒而不是3秒
    results = await asyncio.gather(
        fetch_data("url1"),
        fetch_data("url2"),
        fetch_data("url3"),
    )

asyncio.run(main())
```

**async/await 本质：**

- `async def` 定义一个协程函数
- `await` 暂停当前协程，把CPU让给其他协程，等IO操作完成后再继续
- 遇到IO（网络请求、数据库查询、文件读写）就 `await`，CPU不干等着，去干别的活

#### 为什么FastAPI要用异步？

```text
同步模型：请求1(等数据库2s) → 请求2(等数据库2s) → 请求3(等数据库2s)
         总耗时：6秒

异步模型：请求1(等数据库，让出CPU) → 请求2(等数据库，让出CPU) → 请求3(同时等待)
         总耗时：约2秒
```

> **面试一句话：** "FastAPI基于async/await实现异步IO，在高并发场景下，一个线程就能处理大量请求。遇到IO操作时通过await挂起当前协程，CPU去处理其他请求，IO完成后再恢复执行。"

### 六、与主人项目的关联

#### 项目一（Agent智能客服）

```text
FastAPI 后端
  ├── async def chat()       ← 异步处理请求，不阻塞
  ├── async def get_db()     ← 异步数据库查询（SQLAlchemy async）
  └── SSE 流式响应            ← 异步生成器 yield 逐字返回
```

#### 项目二（智测星图）

```text
pytest 测试框架
  ├── 多线程并发执行测试用例
  └── 进程：Jenkins主进程 + 测试执行进程
```

### 七、面试高频 Q&A

**Q1：进程和线程的区别？**

> 进程是资源分配的最小单位，有独立内存空间；线程是CPU调度的最小单位，共享进程的内存。进程切换开销大，线程切换开销小。进程间通信需要IPC，线程间可以直接共享内存但需要同步。

**Q2：什么是死锁？怎么避免？**

> 死锁是多个线程互相等待对方释放资源导致永久阻塞。四个必要条件：互斥、持有并等待、不可剥夺、循环等待。实际开发中最常用的避免方法是按固定顺序加锁，打破循环等待条件。

**Q3：协程和线程的区别？**

> 线程由操作系统调度，切换需要进入内核态，开销较大；协程由程序自身调度，在用户态切换，开销极小。一个线程可以包含多个协程。Python中通过async/await实现协程，FastAPI就是基于异步协程的高性能框架。

**Q4：async/await 的原理？**

> await遇到IO操作时挂起当前协程，把控制权交给事件循环，CPU去执行其他协程。IO完成后事件循环恢复该协程继续执行。这样单线程就能处理大量并发IO请求。

---

## 4.4 Git 基础

### 一、Git 是什么

Git 是**分布式版本控制系统**，核心作用是：记录文件的每次修改历史，随时可以回退到任意版本。

```text
分布式 vs 集中式：

集中式（SVN）：所有人在同一台服务器上取代码，服务器挂了就全完
  开发者A ──→ 中心服务器 ←── 开发者B

分布式（Git）：每个人都有完整的代码仓库副本，服务器挂了本地还有
  开发者A（完整仓库） ←──→ 远程仓库 ←──→ 开发者B（完整仓库）
```

### 二、四个区域（理解Git的核心）

```text
工作区(Working Directory)    暂存区(Stage/Index)     本地仓库(Repository)     远程仓库(Remote)
  你写代码的地方                提交前的缓冲区            本地的版本历史           GitHub/GitLab
      │                          │                        │                       │
      │  git add                 │  git commit            │  git push             │
      │ ──────────────────>      │ ──────────────────>    │ ──────────────────>   │
      │                          │                        │                       │
      │  git restore             │  git reset             │  git pull             │
      │ <──────────────────      │ <──────────────────    │ <──────────────────   │
```

| 区域 | 含义 | 文件状态 |
|------|------|----------|
| 工作区 | 你实际编辑文件的地方 | Untracked / Modified |
| 暂存区 | `git add` 之后，准备提交的文件快照 | Staged |
| 本地仓库 | `git commit` 之后，保存在 `.git` 中的版本记录 | Committed |
| 远程仓库 | GitHub/GitLab 上的代码仓库 | Pushed |

### 三、常用命令速查

#### 基础操作

| 命令 | 作用 | 说明 |
|------|------|------|
| `git init` | 初始化仓库 | 在当前目录创建 `.git` 文件夹 |
| `git clone <url>` | 克隆远程仓库 | 把远程项目下载到本地 |
| `git status` | 查看状态 | 看哪些文件改了、哪些在暂存区 |
| `git add <file>` | 添加到暂存区 | `git add .` 添加所有修改 |
| `git commit -m "msg"` | 提交到本地仓库 | `-m` 后面是提交信息 |
| `git push` | 推送到远程 | 把本地提交推到 GitHub |
| `git pull` | 拉取远程更新 | = `git fetch` + `git merge` |

#### 分支操作

| 命令 | 作用 | 说明 |
|------|------|------|
| `git branch` | 查看所有分支 | `*` 标记当前分支 |
| `git branch <name>` | 创建新分支 | 基于当前分支创建 |
| `git checkout <name>` | 切换分支 | 也可以用 `git switch <name>` |
| `git checkout -b <name>` | 创建并切换 | 一步到位 |
| `git merge <name>` | 合并分支 | 把指定分支合并到当前分支 |
| `git branch -d <name>` | 删除分支 | 删除已合并的分支 |

#### 查看与回退

| 命令 | 作用 | 说明 |
|------|------|------|
| `git log` | 查看提交历史 | `--oneline` 精简显示 |
| `git diff` | 查看修改内容 | 工作区 vs 暂存区的差异 |
| `git reset --soft <commit>` | 软回退 | 回退commit，保留暂存区修改 |
| `git reset --mixed <commit>` | 混合回退（默认） | 回退commit和暂存区，保留工作区修改 |
| `git reset --hard <commit>` | 硬回退 | 全部回退，修改丢失（危险！） |
| `git revert <commit>` | 撤销某次提交 | 生成一个新的撤销commit，更安全 |

### 四、merge vs rebase（面试高频）

#### merge（合并）

```bash
# 在main分支上，把feature分支合并进来
git checkout main
git merge feature
```

```text
    A---B---C  feature
   /         \
D---E---F---G---M  main    ← M是merge commit，保留了分支历史
```

特点：保留完整的分支历史，会产生一个合并commit，历史图有分叉。

#### rebase（变基）

```bash
# 在feature分支上，把它的基点移到main最新位置
git checkout feature
git rebase main
```

```text
              A'--B'--C'  feature    ← commit被"重放"，历史是线性的
             /
D---E---F---G  main
```

特点：把分支的commit重新"接"到目标分支后面，历史是线性的一条线，更整洁。但会改写commit历史。

#### 区别总结

|  | merge | rebase |
|--|-------|--------|
| 历史 | 保留分叉，真实记录 | 线性历史，更整洁 |
| commit | 多一个merge commit | 无额外commit |
| 安全性 | 安全，不改历史 | 会改写commit hash |
| 原则 | 公共分支用merge | 个人分支用rebase |

> **面试一句话：** "公共分支（main）用merge保留完整历史，个人特性分支用rebase保持线性历史。rebase会改写commit历史，所以不要对已经push的公共分支rebase。"

### 五、冲突解决

#### 什么时候会冲突？

两个分支**修改了同一个文件的同一个位置**，Git 不知道该用哪个版本。

#### 冲突文件的样子

```text
<<<<<<< HEAD
这是当前分支的内容
=======
这是合并进来的分支的内容
>>>>>>> feature
```

#### 解决步骤

```bash
# 1. 手动编辑冲突文件，选择要保留的内容
# 删掉 <<<<<<< ======= >>>>>>> 标记，保留正确的代码

# 2. 标记为已解决
git add <冲突文件>

# 3. 完成合并
git commit -m "解决冲突：合并feature分支"
```

### 六、实际开发工作流

```bash
# 1. 从main拉最新代码
git checkout main
git pull origin main

# 2. 创建自己的功能分支
git checkout -b feature/login

# 3. 开发过程中，频繁提交
git add .
git commit -m "完成登录页面UI"

# 4. 开发完成后，推送到远程
git push origin feature/login

# 5. 在GitHub/GitLab上创建Pull Request (PR)
# 6. 代码Review通过后合并到main
```

### 七、面试高频 Q&A

**Q1：git reset 的三种模式区别？**

> - `--soft`：只回退commit，暂存区和工作区不变（撤销提交但保留修改在暂存区）
> - `--mixed`（默认）：回退commit和暂存区，工作区不变（撤销提交和add，修改还在）
> - `--hard`：全部回退，修改丢失（危险！真正删除修改）

**Q2：git reset 和 git revert 的区别？**

> reset 是回退到某个历史版本，会改写commit历史；revert 是生成一个新的commit来撤销指定commit的修改，不改写历史。公共分支应该用revert更安全。

**Q3：merge 和 rebase 的区别？**

> merge 保留完整分支历史，产生合并commit；rebase 把commit重新接到目标分支后面，历史线性整洁。公共分支用merge，个人分支用rebase。不要对已push的分支rebase。

**Q4：git pull 和 git fetch 的区别？**

> `git fetch` 只下载远程更新到本地引用，不合并，可以先查看再决定；`git pull` = `fetch` + `merge`，直接把远程更新合并到当前分支。

---

# 模块一：Java 基础

## 1.1 Java 面向对象编程（OOP）

### 一、面向对象四大特性

#### 1. 封装（Encapsulation）

**核心思想：** 隐藏内部实现细节，对外只暴露必要的接口。

```java
public class User {
    private String name;      // private 外部不能直接访问
    private int age;

    // 通过 public 方法控制访问
    public String getName() {
        return name;
    }

    public void setAge(int age) {
        if (age < 0 || age > 150) {   // 在setter里做校验
            throw new IllegalArgumentException("年龄不合法");
        }
        this.age = age;
    }
}
```

> **面试一句话：** "封装是将数据和操作数据的方法绑定在一起，通过访问修饰符控制外部访问权限，隐藏内部实现细节，提高安全性和可维护性。"

#### 2. 继承（Inheritance）

**核心思想：** 子类继承父类的属性和方法，实现代码复用。

```java
// 父类
public class Animal {
    String name;
    public void eat() {
        System.out.println(name + "在吃东西");
    }
}

// 子类继承父类
public class Dog extends Animal {
    public void bark() {
        System.out.println(name + "在叫：汪汪汪");
    }
}

// 使用
Dog dog = new Dog();
dog.name = "旺财";
dog.eat();    // 继承来的方法
dog.bark();   // 自己的方法
```

**Java 继承的规则：**

| 规则 | 说明 |
|------|------|
| 单继承 | 一个类只能继承一个父类（extends后面只能写一个） |
| 多层继承 | A→B→C，可以多层 |
| 所有类默认继承 | Java所有类默认继承 `Object` 类 |

#### 3. 多态（Polymorphism）

**核心思想：** 同一个方法调用，不同对象有不同的表现。

**三个必要条件：** 继承 + 重写 + 父类引用指向子类对象

```java
public class Animal {
    public void speak() {
        System.out.println("动物发出声音");
    }
}

public class Dog extends Animal {
    @Override
    public void speak() {
        System.out.println("汪汪汪");
    }
}

public class Cat extends Animal {
    @Override
    public void speak() {
        System.out.println("喵喵喵");
    }
}

// 多态：父类引用指向子类对象
Animal a1 = new Dog();    // 编译看左边(Animal)，运行看右边(Dog)
Animal a2 = new Cat();

a1.speak();  // 输出：汪汪汪
a2.speak();  // 输出：喵喵喵
```

> **面试一句话：** "多态是父类引用指向子类对象，调用方法时执行的是子类重写后的版本。编译时看左边的类型（父类），运行时看右边的对象（子类）。好处是提高代码扩展性，新增子类不需要修改已有代码。"

#### 4. 抽象（Abstraction）

**核心思想：** 提取事物的核心共性，忽略非必要细节。

Java 中通过**抽象类**和**接口**来实现抽象。

```java
// 抽象类：不能实例化，可以有无实现的方法
public abstract class Shape {
    abstract double area();    // 抽象方法，没有方法体

    public void printInfo() {  // 普通方法，有方法体
        System.out.println("这是一个形状，面积：" + area());
    }
}

public class Circle extends Shape {
    double radius;
    Circle(double r) { radius = r; }

    @Override
    double area() {
        return Math.PI * radius * radius;  // 子类必须实现
    }
}
```

### 二、重写（Override）vs 重载（Overload）（面试必问）

|  | 重写(Override) | 重载(Overload) |
|--|----------------|----------------|
| 发生位置 | **父子类**之间 | **同一个类**中 |
| 方法名 | 相同 | 相同 |
| 参数列表 | 相同（不能改） | **不同**（个数或类型不同） |
| 返回值 | 相同或是其子类 | 可以不同 |
| 访问修饰符 | 不能更严格（可以更宽松） | 可以不同 |
| @Override注解 | 建议加 | 不需要 |
| 本质 | 子类覆盖父类的实现 | 同名方法的不同版本 |

```java
// 重载(Overload)：同一个类，方法名相同，参数不同
public void print(int a) { }
public void print(String s) { }
public void print(int a, int b) { }

// 重写(Override)：子类覆盖父类方法
class Animal {
    public void speak() { System.out.println("动物"); }
}
class Dog extends Animal {
    @Override
    public void speak() { System.out.println("汪汪汪"); }  // 重写
}
```

> **面试一句话：** "重写是子类覆盖父类的方法，方法签名完全相同，运行时根据对象类型决定调用哪个版本（多态）。重载是同一个类中方法名相同但参数列表不同，编译时根据参数类型决定调用哪个版本。"

### 三、接口（Interface）vs 抽象类（Abstract Class）（面试高频）

|  | 接口(Interface) | 抽象类(Abstract Class) |
|--|-----------------|----------------------|
| 关键字 | `interface` / `implements` | `abstract class` / `extends` |
| 实例化 | 不能 | 不能 |
| 构造方法 | 没有 | 可以有 |
| 成员变量 | 只能是 `public static final`（常量） | 可以有普通成员变量 |
| 方法 | Java8前全是抽象方法；Java8+有default方法；Java9+有private方法 | 可以有抽象方法和普通方法 |
| 多实现/继承 | 一个类可以实现**多个**接口 | 一个类只能继承**一个**抽象类 |
| 设计理念 | "能做什么"（行为契约） | "是什么"（本质归属） |

```java
// 接口：定义行为
public interface Flyable {
    void fly();    // 抽象方法
}

public interface Swimmable {
    void swim();
}

// 一个类可以实现多个接口
public class Duck implements Flyable, Swimmable {
    @Override
    public void fly() { System.out.println("鸭子飞"); }

    @Override
    public void swim() { System.out.println("鸭子游泳"); }
}
```

> **面试一句话：** "接口定义'能做什么'，是行为契约，支持多实现，Java8后支持default方法。抽象类定义'是什么'，是本质归属，只能单继承，可以有构造方法和成员变量。当多个类有共同的本质属性时用抽象类，当需要定义共同行为能力时用接口。"

### 四、Java 访问修饰符

| 修饰符 | 同一类 | 同一包 | 子类（不同包） | 其他 |
|--------|--------|--------|----------------|------|
| `public` | Y | Y | Y | Y |
| `protected` | Y | Y | Y | N |
| `default`（不写） | Y | Y | N | N |
| `private` | Y | N | N | N |

记忆：从上到下访问范围递减：public > protected > default > private

### 五、面试高频 Q&A

**Q1：面向对象的四大特性？**

> 封装（隐藏细节，对外暴露接口）、继承（子类复用父类代码）、多态（同一方法不同实现）、抽象（提取共性忽略细节）。

**Q2：重写和重载的区别？**

> 重写是子类覆盖父类方法，方法签名相同，运行时多态；重载是同类中方法名相同参数不同，编译时多态。

**Q3：接口和抽象类的区别？**

> 接口是行为契约，支持多实现，只能有常量和抽象方法（Java8后有default）。抽象类是本质归属，只能单继承，可以有构造方法、成员变量和普通方法。

**Q4：Java为什么只支持单继承？**

> 为了避免菱形继承问题：如果A和B都有foo()方法，C同时继承A和B，调用foo()时编译器不知道用哪个。接口可以多实现是因为接口方法默认是抽象的，实现类必须自己定义，不存在歧义。

---

## 1.2 Java 集合框架

### 一、集合框架全景图

Java集合分两大体系：**Collection**（单列）和 **Map**（双列键值对）

```text
                        Iterable
                           │
                       Collection                          Map
                      ╱    │    ╲                        ╱    ╲
                  List   Set   Queue              HashMap  TreeMap
                 ╱   ╲    │                       LinkedHashMap
            ArrayList  HashSet
            LinkedList  TreeSet
            Vector
```

> **面试一句话：** "Java集合分两大体系，Collection存单列数据（List有序可重复、Set无序不重复），Map存键值对。"

### 二、List 体系（有序、可重复）

#### ArrayList vs LinkedList（面试最高频）

|  | ArrayList | LinkedList |
|--|-----------|------------|
| 底层结构 | **动态数组** `Object[]` | **双向链表** |
| 随机访问(get) | O(1) 极快（数组下标直接定位） | O(n) 慢（要从头/尾遍历） |
| 头部插入/删除 | O(n) 慢（要移动后面所有元素） | O(1) 快（改指针就行） |
| 尾部插入 | O(1) 均摊 | O(1) |
| 内存占用 | 紧凑（连续内存） | 较大（每个节点多存两个指针） |
| 适用场景 | 查询多、尾部增删多 | 频繁头部/中间增删 |

```java
// ArrayList 扩容机制（面试常问）
// 默认初始容量10，每次扩容为原来的1.5倍
ArrayList<String> list = new ArrayList<>();  // 初始容量10
// 第11个元素加入时 → 扩容到15
// 第16个元素加入时 → 扩容到22（15 * 1.5）
```

> **面试一句话：** "ArrayList底层是动态数组，随机访问O(1)快但中间插入O(n)慢，适合读多写少。LinkedList底层是双向链表，头尾操作O(1)快但随机访问O(n)慢，适合频繁增删。实际开发中95%用ArrayList。"

### 三、Map 体系（键值对）

#### HashMap 底层原理（面试重中之重）

**JDK1.8 的 HashMap = 数组 + 链表 + 红黑树**

```text
table数组
┌───┐
│ 0 │ → null
├───┤
│ 1 │ → Node(K1,V1) → Node(K2,V2) → ...   ← 链表
├───┤
│ 2 │ → null
├───┤
│ 3 │ ●  ← TreeNode(红黑树，链表长度≥8且数组≥64时树化)
├───┤      TreeNode
│...│       ╱      ╲
├───┤    TreeNode  TreeNode
│15 │
└───┘
默认初始容量16，负载因子0.75，扩容为原来的2倍
```

#### put 流程（面试必问）

```text
① 计算key的hash值：hash = (h = key.hashCode()) ^ (h >>> 16)  高16位异或低16位
② 计算数组下标：index = hash & (数组长度-1)   等价于 hash % 数组长度
③ 如果该位置为空 → 直接放入
④ 如果该位置有元素 → 发生hash冲突：
   ├── key相同(equals) → 覆盖旧值
   ├── 不同key，链表 → 尾插法追加到链表尾部
   │     └── 链表长度 ≥ 8 且数组长度 ≥ 64 → 转红黑树
   └── 不同key，红黑树 → 红黑树插入
⑤ 插入后检查容量：size > 容量×负载因子(16×0.75=12) → 扩容2倍并重新hash
```

#### 为什么用红黑树？

- 链表查找 O(n)，节点太多时很慢
- 红黑树查找 O(log n)，快得多
- **阈值8**是因为：根据泊松分布，链表长度达到8的概率极低（千万分之一），正常不会触发

#### 为什么负载因子是0.75？

- 太小（如0.5）：浪费空间，频繁扩容
- 太大（如1.0）：hash冲突多，链表长，查询慢
- **0.75是时间和空间的折中平衡点**

#### JDK1.7 vs JDK1.8 HashMap 区别（面试高频）

|  | JDK1.7 | JDK1.8 |
|--|--------|--------|
| 数据结构 | 数组 + 链表 | 数组 + 链表 + 红黑树 |
| 插入方式 | 头插法 | 尾插法 |
| hash计算 | 4次扰动 | 1次扰动（异或高16位） |
| 并发问题 | 头插法导致死循环 | 尾插法解决了死循环但仍线程不安全 |

#### ConcurrentHashMap（面试常问）

|  | HashMap | ConcurrentHashMap |
|--|---------|-------------------|
| 线程安全 | 不安全 | 安全 |
| null键/值 | 允许 | 不允许（抛NPE） |
| JDK1.7实现 | - | Segment分段锁（16段） |
| JDK1.8实现 | - | CAS + synchronized（锁单个链表头节点） |

> **面试一句话：** "ConcurrentHashMap在JDK1.8用CAS+synchronized替代了1.7的Segment分段锁，锁粒度从段级别细化到单个桶（链表头节点），并发度更高。插入时先尝试CAS，失败再用synchronized。"

### 四、Set 体系（无序、不重复）

|  | HashSet | TreeSet |
|--|---------|---------|
| 底层 | HashMap（只用了key） | 红黑树 |
| 排序 | 无序 | 自然排序或定制排序 |
| null | 允许一个null | 不允许null |
| 去重原理 | hashCode() + equals() | compareTo()返回0 |

#### HashSet 去重原理（面试常问）

```text
添加元素时：
① 计算hashCode() → 定位数组位置
② 该位置无元素 → 直接加入
③ 该位置有元素 → 调用equals()比较：
   ├── true → 重复，不加入
   └── false → 不重复，加入链表
```

> **面试一句话：** "HashSet去重先比较hashCode定位桶位置，再比较equals判断是否重复。所以重写equals必须同时重写hashCode，否则相同对象可能hash到不同位置导致去重失败。"

### 五、面试高频 Q&A

**Q1：ArrayList和LinkedList的区别？**

> ArrayList底层动态数组，随机访问O(1)快，中间插入O(n)慢；LinkedList底层双向链表，头尾操作O(1)快，随机访问O(n)慢。大多数场景用ArrayList。

**Q2：HashMap的底层原理？**

> JDK1.8的HashMap是数组+链表+红黑树。通过hash计算数组下标，冲突时形成链表，链表长度≥8且数组≥64时转红黑树。默认容量16，负载因子0.75，超出容量×0.75时扩容2倍。

**Q3：HashMap为什么线程不安全？**

> JDK1.7头插法并发扩容会导致链表成环死循环；JDK1.8改为尾插法解决了死循环，但put操作没有同步，并发put仍会数据覆盖。线程安全用ConcurrentHashMap。

**Q4：HashMap的key可以是null吗？**

> 可以，HashMap允许一个null key，放在数组第0个位置。但ConcurrentHashMap不允许null key或null value。

---

## 1.3 Java 多线程

### 一、创建线程的三种方式

| 方式 | 实现 | 优缺点 |
|------|------|--------|
| 继承Thread | `class MyThread extends Thread` 重写run() | 简单但Java单继承，不能再继承其他类 |
| 实现Runnable | `class MyTask implements Runnable` | 推荐，可以实现多个接口 |
| 实现Callable | `class MyTask implements Callable<String>` | 有返回值，能抛异常 |

```java
// 方式1：继承Thread
class MyThread extends Thread {
    public void run() {
        System.out.println("线程运行: " + Thread.currentThread().getName());
    }
}
new MyThread().start();

// 方式2：实现Runnable（推荐）
Thread t = new Thread(() -> {
    System.out.println("Runnable线程");
});
t.start();

// 方式3：实现Callable（有返回值）
FutureTask<String> task = new FutureTask<>(() -> {
    return "执行结果";
});
new Thread(task).start();
String result = task.get();  // 阻塞等待结果
```

### 二、synchronized vs Lock（面试必问）

#### synchronized（关键字，JVM层面）

```java
// 1. 同步方法（锁的是this对象）
public synchronized void method() { }

// 2. 同步代码块（锁指定对象）
synchronized (obj) {
    // 临界区
}

// 3. 静态同步方法（锁的是Class对象）
public static synchronized void method() { }
```

#### ReentrantLock（类，API层面）

```java
ReentrantLock lock = new ReentrantLock();
lock.lock();
try {
    // 临界区
} finally {
    lock.unlock();   // 必须手动释放！
}
```

#### 对比（面试必背）

|  | synchronized | ReentrantLock |
|--|-------------|---------------|
| 层面 | JVM关键字 | JDK API类 |
| 加锁/释放 | 自动 | 手动（必须在finally中unlock） |
| 可中断 | 不可 | `lockInterruptibly()` 可中断 |
| 超时获取 | 不支持 | `tryLock(timeout)` 支持 |
| 公平锁 | 只有非公平 | 可选公平/非公平（构造参数） |
| 条件变量 | 只有wait/notify | 多个Condition精准唤醒 |
| 适用场景 | 简单同步、代码块 | 复杂同步逻辑 |

> **面试一句话：** "synchronized是JVM层面的关键字，自动加锁释放，简单但不够灵活。ReentrantLock是API层面的锁，手动加锁释放，支持可中断、超时、公平锁、多条件变量，适合复杂场景。"

### 三、线程池（面试重中之重）

#### 为什么用线程池？

- 避免频繁创建销毁线程的开销
- 控制并发数量，防止资源耗尽
- 统一管理线程

#### ThreadPoolExecutor 7大核心参数（面试必背）

```java
ThreadPoolExecutor pool = new ThreadPoolExecutor(
    2,                    // ① corePoolSize：核心线程数（常驻不销毁）
    5,                    // ② maximumPoolSize：最大线程数
    60, TimeUnit.SECONDS, // ③ keepAliveTime + unit：非核心线程空闲存活时间
    new LinkedBlockingQueue<>(100),  // ④ workQueue：任务等待队列
    new ThreadFactory(),             // ⑤ threadFactory：创建线程的工厂
    new ThreadPoolExecutor.AbortPolicy()  // ⑥ handler：拒绝策略
);
```

#### 执行流程（面试必问）

```text
提交任务
  │
  ├── 核心线程数未满？ → 创建核心线程执行
  │
  ├── 核心线程满了，队列未满？ → 放入等待队列
  │
  ├── 队列也满了，未达最大线程数？ → 创建非核心线程执行
  │
  └── 最大线程数也满了？ → 执行拒绝策略
```

#### 四种拒绝策略

| 策略 | 行为 |
|------|------|
| AbortPolicy（默认） | 直接抛RejectedExecutionException异常 |
| CallerRunsPolicy | 由提交任务的线程自己执行 |
| DiscardPolicy | 默默丢弃，不通知 |
| DiscardOldestPolicy | 丢弃队列中最老的任务，重新提交当前任务 |

#### 为什么不推荐用 Executors 创建线程池？

```java
// 不推荐！
ExecutorService pool = Executors.newFixedThreadPool(10);   // 队列无界 → OOM
ExecutorService pool = Executors.newCachedThreadPool();     // 线程数无上限 → OOM

// 推荐！手动创建，参数可控
ThreadPoolExecutor pool = new ThreadPoolExecutor(
    2, 5, 60, TimeUnit.SECONDS,
    new LinkedBlockingQueue<>(100),  // 有界队列，防止OOM
    new ThreadPoolExecutor.CallerRunsPolicy()
);
```

> **面试一句话：** "不推荐Executors是因为FixedThreadPool用无界队列可能导致OOM，CachedThreadPool最大线程数是Integer.MAX_VALUE也可能OOM。应该用ThreadPoolExecutor手动创建，明确指定参数。"

### 四、volatile 关键字（面试高频）

#### 两大作用

1. **保证可见性：** 一个线程修改了volatile变量，其他线程**立刻看到**最新值
2. **禁止指令重排序：** 编译器和CPU不会把volatile变量前后的指令打乱

#### 为什么需要可见性？

```java
// 没有volatile的问题
boolean running = true;    // 线程A修改 running = false
                          // 线程B可能永远看不到修改，一直循环

volatile boolean running = true;  // 加了volatile，线程B立刻看到false
```

每个线程有自己的**工作内存（CPU缓存）**，默认不会及时同步到主内存。volatile强制每次都从主内存读取。

#### volatile 不保证原子性

```java
volatile int count = 0;
count++;   // 这不是原子操作！实际上是 读→加→写 三步
           // 多线程并发count++仍然会丢数据
// 解决：用 AtomicInteger 或 synchronized
```

### 五、CAS（Compare And Swap）（面试常问）

**无锁并发：** 不加锁也能保证线程安全的方式。

```text
CAS(V, E, N)：V=内存值，E=期望值，N=新值
① 读取内存值V
② 比较V和期望值E是否相等
   ├── 相等 → 说明没人改过，写入新值N（成功）
   └── 不相等 → 说明被别人改了，重新读取再试（自旋）
```

**CAS的问题：**

- **ABA问题：** 值从A→B→A，CAS以为没变过。解决：AtomicStampedReference（加版本号）
- **自旋开销：** 长时间CAS失败会一直循环，消耗CPU
- **只能保证一个变量的原子性**

### 六、AQS（AbstractQueuedSynchronizer）（面试进阶）

AQS是Java并发包的基石，ReentrantLock、Semaphore、CountDownLatch都基于它。

**核心思想：**

- 用一个 `volatile int state` 表示锁状态（0=空闲，≥1=被占用）
- 用一个 **CLH双向队列** 存放等待的线程
- 获取锁失败 → 包装成Node入队 → park挂起
- 释放锁 → 唤醒队列中下一个节点

> **面试一句话：** "AQS用一个volatile的state变量表示锁状态，一个CLH双向队列管理等待线程。获取锁失败时线程进入队列阻塞，释放锁时唤醒后继节点。ReentrantLock的state是重入次数，Semaphore的state是许可数。"

### 七、面试高频 Q&A

**Q1：创建线程有哪几种方式？**

> 三种：继承Thread、实现Runnable（推荐）、实现Callable（有返回值）。实际开发中都用线程池。

**Q2：synchronized和ReentrantLock的区别？**

> synchronized是JVM关键字自动释放锁，ReentrantLock是API类手动释放，支持可中断、超时、公平锁、多条件变量。

**Q3：线程池的核心参数？执行流程？**

> 7大参数：核心线程数、最大线程数、空闲存活时间、时间单位、工作队列、线程工厂、拒绝策略。任务先给核心线程→队列→非核心线程→拒绝策略。

**Q4：volatile的作用？**

> 保证可见性（修改立刻对其他线程可见）和禁止指令重排序。但不保证原子性，不能替代synchronized。

**Q5：什么是CAS？有什么问题？**

> Compare And Swap，无锁并发机制，比较当前值和期望值，相同才更新。问题有ABA问题（用版本号解决）、自旋开销、只能保证单变量原子性。

---

## 1.4 Java 反射

### 一、什么是反射

**正常使用类：** 编译时就确定了使用哪个类 → `Dog dog = new Dog();`

**反射：** 运行时动态获取类的信息（方法、字段、构造器），并动态调用。程序在运行阶段才知道操作的是什么类。

```java
// 正常方式
Dog dog = new Dog();
dog.bark();

// 反射方式
Class<?> clazz = Class.forName("com.example.Dog");  // 运行时才知道是Dog
Object obj = clazz.getDeclaredConstructor().newInstance();
Method method = clazz.getDeclaredMethod("bark");
method.invoke(obj);   // 输出：汪汪汪
```

### 二、反射的核心 API

| 类 | 作用 |
|------|------|
| `Class` | 代表一个类，反射的入口 |
| `Method` | 代表一个方法 |
| `Field` | 代表一个字段/属性 |
| `Constructor` | 代表一个构造方法 |

#### 获取 Class 对象的三种方式

```java
// 方式1：类名.class（编译时已知）
Class<Dog> clazz1 = Dog.class;

// 方式2：对象.getClass()
Dog dog = new Dog();
Class<?> clazz2 = dog.getClass();

// 方式3：Class.forName("全限定类名")（运行时动态加载）
Class<?> clazz3 = Class.forName("com.example.Dog");
```

#### 常用反射操作

```java
Class<?> clazz = Class.forName("com.example.Dog");

// 获取并调用方法
Method speakMethod = clazz.getDeclaredMethod("speak");
speakMethod.setAccessible(true);  // 突破private限制
speakMethod.invoke(obj);

// 获取并修改字段
Field nameField = clazz.getDeclaredField("name");
nameField.setAccessible(true);
nameField.set(obj, "旺财");

// 获取并调用构造方法
Constructor<?> constructor = clazz.getDeclaredConstructor(String.class);
Object dog = constructor.newInstance("旺财");
```

### 三、动态代理（面试必问）

#### 为什么需要动态代理？

**静态代理** 需要为每个类手动写代理类，接口方法一改代理类也得改。**动态代理** 在运行时自动生成代理类，不需要手动编写。

#### JDK 动态代理 vs CGLIB 动态代理

|  | JDK动态代理 | CGLIB动态代理 |
|--|------------|--------------|
| 原理 | 基于接口，生成接口的实现类 | 基于继承，生成目标类的子类 |
| 要求 | 目标类必须实现接口 | 目标类不能是final类 |
| 性能 | 生成代理快，调用略慢 | 生成代理慢，调用更快 |
| Spring默认 | 接口存在时用JDK | 无接口时用CGLIB |

```java
// JDK动态代理示例
public class ProxyFactory {
    private Object target;  // 被代理的对象

    public Object getProxyInstance() {
        return Proxy.newProxyInstance(
            target.getClass().getClassLoader(),
            target.getClass().getInterfaces(),
            (proxy, method, args) -> {
                System.out.println("前置增强：记录日志");
                Object result = method.invoke(target, args);  // 执行原方法
                System.out.println("后置增强：提交事务");
                return result;
            }
        );
    }
}

// 使用
UserService proxy = (UserService) factory.getProxyInstance();
proxy.deleteUser(1);
// 输出：
// 前置增强：记录日志
// 执行删除用户...
// 后置增强：提交事务
```

> **面试一句话：** "JDK动态代理基于接口，通过Proxy.newProxyInstance在运行时生成接口的实现类。CGLIB基于继承，通过生成目标类的子类实现代理。Spring AOP在目标类实现了接口时默认用JDK代理，否则用CGLIB。"

### 四、反射的应用场景

| 场景 | 说明 |
|------|------|
| **Spring IoC** | 通过反射创建Bean实例、注入依赖 |
| **Spring AOP** | 通过动态代理实现切面增强 |
| **注解处理** | 运行时通过反射读取注解信息 |
| **序列化框架** | Jackson/Gson通过反射获取字段进行JSON转换 |
| **JUnit** | 通过反射找到@Test标注的方法并执行 |

### 五、面试高频 Q&A

**Q1：什么是反射？**

> 反射是运行时动态获取类的信息（方法、字段、构造器）并动态调用的机制。通过Class对象获取类的结构，可以在运行时创建对象、调用方法、修改字段，甚至突破private访问限制。

**Q2：JDK动态代理和CGLIB的区别？**

> JDK动态代理基于接口，生成接口的实现类；CGLIB基于继承，生成目标类的子类。JDK要求目标类必须实现接口，CGLIB要求目标类不能是final。

**Q3：反射的应用场景？**

> Spring IoC通过反射创建Bean和注入依赖；Spring AOP通过动态代理实现切面；注解处理、JSON序列化框架（Jackson）、测试框架（JUnit）都大量使用反射。

---

## 1.5 主流框架 Spring

### 一、Spring 的两大核心

#### 1. IoC（控制反转，Inversion of Control）

**传统方式：** 对象自己创建依赖（new）

```java
class UserService {
    UserDao userDao = new UserDao();  // 自己创建，耦合度高
}
```

**IoC方式：** 对象不自己创建依赖，由Spring容器注入

```java
@Service
class UserService {
    @Autowired
    UserDao userDao;  // Spring自动注入，不需要new
}
```

|  | 传统方式 | IoC方式 |
|--|---------|---------|
| 谁创建对象 | 对象自己 new | Spring容器创建和管理 |
| 耦合度 | 高（直接依赖具体实现） | 低（依赖注入，面向接口） |
| 可测试性 | 难（依赖具体实现） | 易（可以Mock注入） |

**DI（依赖注入）是IoC的实现方式：** @Autowired、构造器注入、setter注入

#### 2. AOP（面向切面编程，Aspect-Oriented Programming）

**核心思想：** 把与业务无关的横切关注点（日志、事务、权限）从业务代码中抽离出来。

```java
// 没有 AOP：业务代码和日志混在一起
public void transfer() {
    log.info("开始转账");          // 日志
    checkPermission();             // 权限
    beginTransaction();            // 事务
    accountDao.transfer();         // 真正的业务逻辑（只有这一行是有用的）
    commitTransaction();           // 事务
    log.info("转账完成");          // 日志
}

// 有 AOP：业务代码只写业务
@Transactional    // 事务由AOP自动处理
@Log              // 日志由AOP自动处理
public void transfer() {
    accountDao.transfer();         // 只关注业务
}
```

**AOP 核心概念（面试常问）：**

| 概念 | 含义 | 类比 |
|------|------|------|
| 切面(Aspect) | 横切关注点的模块（如日志切面） | 一个功能模块 |
| 切入点(Pointcut) | 定义在哪里切入（哪些方法） | "在哪里做" |
| 通知(Advice) | 切入后做什么（前置/后置/环绕） | "做什么" |
| 织入(Weaving) | 将切面应用到目标对象的过程 | "怎么应用" |

**五种通知类型：**

| 通知 | 时机 |
|------|------|
| @Before | 方法执行前 |
| @After | 方法执行后（无论是否异常） |
| @AfterReturning | 方法正常返回后 |
| @AfterThrowing | 方法抛异常后 |
| @Around | 包裹整个方法执行（最强大） |

### 二、Spring Boot 自动配置原理（面试高频）

#### Spring Boot 的核心思想：约定大于配置

传统Spring需要大量XML配置，Spring Boot通过自动配置让你"零配置"启动。

#### 自动配置流程（面试必背）

```text
@SpringBootApplication
    │
    ├── @SpringBootConfiguration   ← 标记这是一个配置类
    ├── @ComponentScan             ← 扫描当前包及子包的组件
    └── @EnableAutoConfiguration   ← 核心！开启自动配置
            │
            ├── @Import(AutoConfigurationImportSelector.class)
            │       │
            │       └── 通过 SpringFactories 机制
            │           加载 META-INF/spring.factories 中
            │           所有 AutoConfiguration 类
            │
            └── 每个 AutoConfiguration 类上有 @Conditional 系列注解
                ├── @ConditionalOnClass      → classpath中有这个类才生效
                ├── @ConditionalOnMissingBean → 容器中没有这个Bean才创建
                └── @ConditionalOnProperty   → 配置文件中有这个属性才生效
```

> **面试一句话回答：** "Spring Boot启动时通过@EnableAutoConfiguration，利用SpringFactories机制加载所有自动配置类。每个配置类通过@ConditionalOnClass等条件注解判断是否生效，只有满足条件（如classpath中有对应依赖）的配置才会注册Bean，实现'引入依赖就自动配置'的效果。"

#### starter 机制

```xml
<!-- 引入这个依赖，就自动配置好了Redis -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-redis</artifactId>
</dependency>
```

原理：starter包含自动配置类 + @Conditional条件判断 → 有依赖就自动配好

### 三、Bean 的生命周期（面试常问）

```text
实例化(Instantiation)
    ↓
属性赋值(Populate properties) ← 依赖注入在这里完成
    ↓
BeanNameAware / BeanFactoryAware
    ↓
BeanPostProcessor.postProcessBeforeInitialization()  ← @PostConstruct
    ↓
InitializingBean.afterPropertiesSet() / init-method
    ↓
BeanPostProcessor.postProcessAfterInitialization()   ← AOP代理在这里生成
    ↓
【Bean 就绪，可以使用】
    ↓
DisposableBean.destroy() / destroy-method  ← @PreDestroy
```

> **面试一句话：** "Bean生命周期：实例化→属性注入→Aware接口回调→BeanPostProcessor前置处理→初始化→BeanPostProcessor后置处理（AOP在这里）→使用→销毁。"

### 四、Bean 的作用域

| 作用域 | 说明 |
|--------|------|
| singleton（默认） | Spring容器中只有一个实例 |
| prototype | 每次获取都创建新实例 |
| request | Web中每个HTTP请求一个实例 |
| session | Web中每个HTTP Session一个实例 |

### 五、面试高频 Q&A

**Q1：什么是IoC？**

> 控制反转，将对象的创建和依赖管理从程序代码转移到Spring容器。通过DI（依赖注入）实现，降低组件间耦合度。@Autowired是最常用的注入方式。

**Q2：什么是AOP？**

> 面向切面编程，将日志、事务、权限等横切关注点从业务代码中分离。通过动态代理（JDK或CGLIB）在方法执行前后插入增强逻辑。Spring的@Transactional就是基于AOP实现的。

**Q3：Spring Boot自动配置原理？**

> @EnableAutoConfiguration通过SpringFactories加载所有自动配置类，每个配置类用@ConditionalOnClass等条件注解判断是否生效。引入starter依赖后，classpath中存在对应类，自动配置就生效。

**Q4：Spring中Bean是线程安全的吗？**

> 默认singleton作用域下不是线程安全的，因为单例Bean被多个线程共享。有状态的Bean需要用prototype作用域或自己保证线程安全。无状态的Bean（如Service、Dao）天然线程安全。



---

# 模块五：后端开发 + 设计模式

## 5.1 FastAPI 框架

### 一、FastAPI 是什么

FastAPI 是 Python 的现代高性能 Web 框架，2018年发布，核心特点：

| 特点 | 说明 |
|------|------|
| **快** | 性能接近 Go/Node.js，基于异步ASGI |
| **简单** | 代码量少，用Python类型注解自动完成很多事 |
| **自动文档** | 自动生成交互式Swagger UI和ReDoc文档 |
| **类型安全** | Pydantic自动校验请求数据 |
| **异步原生** | 原生支持async/await |

#### FastAPI 技术栈关系

```text
你的请求 → Uvicorn(ASGI服务器) → Starlette(HTTP框架) → FastAPI(你的应用) → 响应
                                        ↕
                                   Pydantic(数据校验)
```

| 组件 | 作用 | 类比 |
|------|------|------|
| **Uvicorn** | ASGI服务器，接收HTTP请求 | 类似Java的Tomcat |
| **Starlette** | 底层HTTP/ASGI工具包 | 类似Servlet规范 |
| **Pydantic** | 数据校验和序列化 | 类似Java的Bean Validation |
| **FastAPI** | 在Starlette之上封装的框架 | 类似Spring MVC |

### 二、第一个 FastAPI 应用

```python
# main.py
from fastapi import FastAPI

# 创建应用实例
app = FastAPI(title="My API", description="API文档描述", version="1.0.0")

# 定义路由：HTTP方法 + URL路径 + 处理函数
@app.get("/")
def root():
    return {"message": "Hello World"}

# 路径参数：URL中的变量，自动类型校验
@app.get("/users/{user_id}")
def get_user(user_id: int):       # int类型注解 → 自动校验，传字符串会报错
    return {"user_id": user_id}

# 查询参数：URL中 ?key=value 的部分
@app.get("/items/")
def list_items(page: int = 1, size: int = 10):   # 有默认值的就是查询参数
    return {"page": page, "size": size}
```

```bash
# 启动服务器
uvicorn main:app --reload
# main:app = main.py文件中的app变量
# --reload = 代码修改后自动重启（开发模式）

# 访问：
# http://localhost:8000/          → {"message": "Hello World"}
# http://localhost:8000/users/123 → {"user_id": 123}
# http://localhost:8000/users/abc → 自动报错："user_id is not a valid integer"
# http://localhost:8000/items/?page=2&size=20 → {"page": 2, "size": 20}
# http://localhost:8000/docs      → 自动生成的Swagger交互式文档
```

**为什么能自动生成文档？** FastAPI读取路由定义和类型注解，自动生成OpenAPI(Swagger)规范。

### 三、Pydantic 数据校验（核心重点）

Pydantic 是 FastAPI 的数据校验引擎。核心思路：**用 Python 类型注解定义数据结构，自动校验 + 自动转换**。

```python
from pydantic import BaseModel, Field
from typing import Optional

# 定义请求体模型
class UserCreate(BaseModel):
    username: str = Field(
        ...,                          # ... 表示必填
        min_length=3,                 # 最短3个字符
        max_length=20,                # 最长20个字符
        description="用户名"
    )
    email: str = Field(
        ...,
        pattern=r"^[\w.-]+@[\w.-]+\.\w+$",   # 正则校验邮箱格式
    )
    age: int = Field(
        default=18,                   # 默认值，非必填
        ge=0,                         # greater than or equal ≥ 0
        le=150,                       # less than or equal ≤ 150
    )
    hobbies: Optional[list[str]] = None   # 可选字段

# 在路由中使用
@app.post("/users", status_code=201)
def create_user(user: UserCreate):            # 自动从Body JSON解析并校验
    return {"username": user.username, "email": user.email, "age": user.age}
```

**自动校验效果：**

```json
// 正常请求：
POST /users  {"username": "zhangsan", "email": "zs@mail.com", "age": 25}
// 响应 201：{"username": "zhangsan", "email": "zs@mail.com", "age": 25}

// 校验失败请求：
POST /users  {"username": "ab", "email": "invalid", "age": 200}
// 自动响应 422 Unprocessable Entity：
{
    "detail": [
        {"loc": ["body", "username"], "msg": "String should have at least 3 characters"},
        {"loc": ["body", "email"], "msg": "String should match pattern..."},
        {"loc": ["body", "age"], "msg": "Input should be less than or equal to 150"}
    ]
}
```

**Pydantic 常用验证器：**

| 类型 | Field约束 | 说明 |
|------|-----------|------|
| `str` | `min_length`, `max_length`, `pattern` | 字符串长度和正则 |
| `int` / `float` | `ge`(≥), `gt`(>), `le`(≤), `lt`(<) | 数值范围 |
| `list[T]` | `min_length`, `max_length` | 列表长度 |
| `Optional[T]` | `default=None` | 可选字段 |

**响应模型：** 用 `response_model=UserResponse` 控制返回字段，防止密码等敏感数据泄露。

> **面试一句话：** "Pydantic用BaseModel+类型注解自动校验请求参数，校验失败自动返回422和详细错误。还支持response_model控制响应字段，防止敏感数据泄露。"

### 四、参数获取的四种方式

```python
from fastapi import Path, Query, Header, Cookie, Depends

# 1. 路径参数：URL中的变量
@app.get("/users/{user_id}")
def get_user(user_id: int = Path(..., ge=1)):
    return {"user_id": user_id}
# 请求：GET /users/123

# 2. 查询参数：URL中 ?key=value
@app.get("/items")
def list_items(
    keyword: str = Query(default="", max_length=50),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
):
    return {"keyword": keyword, "page": page, "size": size}
# 请求：GET /items?keyword=手机&page=2&size=20

# 3. 请求体：POST/PUT的JSON数据
@app.post("/items")
def create_item(item: ItemCreate):    # BaseModel自动解析Body JSON
    return item
# 请求：POST /items  Body: {"name": "手机", "price": 2999.0}

# 4. Header / Cookie
@app.get("/profile")
def get_profile(
    authorization: str = Header(...),
    session_id: str = Cookie(default=None),
):
    return {"token": authorization, "session": session_id}
```

### 五、依赖注入（Dependency Injection）深入

FastAPI 依赖注入类似 Spring IoC，但用函数实现更轻量。

#### 基本用法：数据库连接

```python
# 定义依赖：获取数据库会话
async def get_db():
    db = AsyncSessionLocal()
    try:
        yield db           # yield = 生成器依赖，请求结束后执行finally
    finally:
        await db.close()   # 请求结束自动关闭连接

# 使用依赖
@app.get("/users")
async def list_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    return result.scalars().all()
```

#### 高级用法：认证 + 权限（嵌套依赖）

```python
from fastapi.security import HTTPBearer

security = HTTPBearer()

# 依赖1：验证Token，返回当前用户
async def get_current_user(credentials = Security(security)):
    token = credentials.credentials
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    if not payload:
        raise HTTPException(status_code=401)
    return {"user_id": payload["sub"], "role": payload["role"]}

# 依赖2：在依赖1基础上检查权限（嵌套依赖）
async def require_admin(user = Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403)
    return user

# 路由：层层依赖注入
@app.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    admin = Depends(require_admin),   # 先验证Token → 再验证权限
    db = Depends(get_db),              # 获取数据库连接
):
    await db.execute(delete(User).where(User.id == user_id))
    await db.commit()
    return {"message": "删除成功"}
```

**依赖注入执行流程：**

```text
请求到达 DELETE /users/123
  │
  ├── 1. require_admin 依赖
  │     └── get_current_user 依赖
  │           └── Security从Header提取Token
  │           └── jwt.decode验证Token → 拿到user信息
  │     └── 检查role=="admin" → 通过
  ├── 2. get_db 依赖 → 创建数据库连接
  ├── 3. 执行 delete_user 业务逻辑
  ├── 4. finally关闭数据库连接
  └── 5. 返回响应
```

> **面试一句话：** "FastAPI依赖注入通过Depends()将认证、权限、数据库等横切逻辑抽成独立函数。依赖可以嵌套（权限依赖认证），请求结束后通过yield的finally自动清理资源。类似Spring IoC但用函数实现更轻量。"

### 六、中间件（Middleware）深入

中间件在每个请求前后统一执行逻辑，类似 Spring AOP 的切面。

#### 日志中间件

```python
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    logger.info(f"{request.method} {request.url}")    # 请求前
    response = await call_next(request)                # 执行后续处理
    duration = time.time() - start_time
    logger.info(f"→ {response.status_code} ({duration:.3f}s)")  # 请求后
    response.headers["X-Process-Time"] = str(duration)
    return response
```

#### CORS 中间件（前后端分离必配）

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 允许的前端地址
    allow_credentials=True,                   # 允许携带Cookie
    allow_methods=["*"],                      # 允许的HTTP方法
    allow_headers=["*"],                      # 允许的请求头
)
```

**为什么需要CORS？** 浏览器同源策略限制了跨域请求。前端 `localhost:5173` 请求后端 `localhost:8000` 端口不同就是跨域。CORS中间件在响应头中加 `Access-Control-Allow-Origin` 告诉浏览器允许跨域。

**CORS预检请求(Preflight)：** 非简单请求（如带Authorization头）浏览器会先发OPTIONS请求询问后端是否允许跨域，CORS中间件自动处理。

### 七、异步 async/await 完整应用

```python
# 异步路由：有IO操作（数据库、HTTP请求）用async def
@app.get("/users/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()

# 同步路由：纯CPU计算用普通def，FastAPI自动放到线程池执行
@app.get("/fibonacci/{n}")
def compute_fibonacci(n: int):
    return {"result": fibonacci(n)}
```

**选择原则：** 有IO操作用 `async def`，纯CPU计算用普通 `def`。

#### SSE 流式响应（主人项目一核心功能）

```python
from fastapi.responses import StreamingResponse

@app.post("/api/chat")
async def chat(request: ChatRequest):
    async def generate():
        async for chunk in agent.stream(request.message):
            yield f"data: {json.dumps({'content': chunk})}\n\n"  # 逐token返回
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
```

**效果：** LLM生成的文字逐字返回给前端，类似ChatGPT的打字效果。

**异步为什么快：** 等IO时通过await让出CPU去处理其他请求，单线程就能处理大量并发。

```text
同步：请求1(等DB 2s) → 请求2(等DB 2s) → 请求3(等DB 2s) = 总计6s
异步：请求1(等DB) → 请求2(等DB) → 请求3(等DB) 同时等 = 总计2s
```

### 八、与主人项目的关联

```python
# 主人项目一后端实际代码结构
app = FastAPI(title="AssistGen API")
app.add_middleware(CORSMiddleware, allow_origins=["*"])

# OAuth2认证
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    if not payload: raise HTTPException(401)
    return payload

# SSE流式聊天
@app.post("/api/chat")
async def chat(request: ChatRequest, user = Depends(get_current_user)):
    async for chunk in llm_service.stream(request.message):
        yield chunk

# LangGraph Agent查询
@app.post("/api/langgraph/query")
async def langgraph_query(request: QueryRequest, user = Depends(get_current_user), db = Depends(get_db)):
    result = await agent.run(request.query)
    return result
```

### 九、面试高频 Q&A

**Q1：FastAPI的特点？为什么选它？**

> FastAPI基于Starlette+Pydantic，性能高（ASGI异步）、开发效率高（类型注解自动校验+自动生成Swagger文档）、原生支持async/await。选它是因为Python生态好、异步性能强、自动文档减少前后端沟通成本。

**Q2：FastAPI依赖注入和Spring IoC异同？**

> 相同：都是将依赖的创建管理交给框架实现解耦。不同：Spring基于类和@Autowired注解，FastAPI基于函数和Depends()更轻量。FastAPI支持嵌套依赖（权限依赖认证），yield的finally自动清理资源。

**Q3：Pydantic的作用？**

> BaseModel+类型注解自动校验参数类型、范围、格式，校验失败自动返回422。response_model控制响应字段防止敏感数据泄露。

**Q4：FastAPI怎么实现流式响应？**

> StreamingResponse + async generator实现SSE。路由用async for逐个yield LLM生成的token，前端通过ReadableStream实时接收，实现类似ChatGPT的逐字输出。

---

## 5.2 RESTful API 设计

### 一、REST 是什么

REST（Representational State Transfer）是一种 API 设计风格，三大核心原则：

1. **URL 表示资源（名词）**：描述"是什么"而非"做什么"
2. **HTTP 方法表示操作（动词）**：GET/POST/PUT/DELETE 对应增删改查
3. **无状态**：每次请求自带所有信息，服务器不保存会话

### 二、URL 设计规范

```text
正确：GET  /users          ← 名词复数 + HTTP方法当动词
错误：POST /getUsers       ← 不要把动词放在URL里！
```

| 操作 | URL | HTTP方法 | 状态码 | 说明 |
|------|-----|----------|--------|------|
| 获取列表 | `GET /users` | GET | 200 | 返回所有用户 |
| 获取单个 | `GET /users/123` | GET | 200 | 返回ID=123的用户 |
| 创建 | `POST /users` | POST | 201 Created | Body携带用户数据 |
| 全量更新 | `PUT /users/123` | PUT | 200 | 必须传完整资源 |
| 部分更新 | `PATCH /users/123` | PATCH | 200 | 只传需要修改的字段 |
| 删除 | `DELETE /users/123` | DELETE | 204 No Content | 成功无返回体 |

嵌套资源：`GET /users/123/orders` = 获取用户123的所有订单

### 三、PUT vs PATCH（面试常问）

```json
// 原始数据：{"id": 1, "name": "张三", "age": 25, "email": "zs@mail.com"}

// PUT 全量更新：必须传完整数据，没传的字段会被覆盖为null
PUT /users/1
{"name": "张三", "age": 26, "email": "zs@mail.com"}

// PATCH 部分更新：只传需要修改的字段，其他不变
PATCH /users/1
{"age": 26}
```

### 四、分页、过滤、排序

```text
分页：GET /users?page=1&size=10
过滤：GET /users?role=admin&age_gt=18
排序：GET /users?sort=created_at&order=desc
```

### 五、无状态设计（面试必问）

**有状态（Session）问题：** 服务器要存Session，重启丢失，分布式难以共享。

**无状态（Token）好处：** 服务器不存会话，天然支持分布式，重启不影响用户。

```text
POST /login → 返回JWT Token
GET /profile + Header: Authorization: Bearer <token> → 验证签名即可
```

> **面试一句话：** "RESTful要求无状态，每次请求自带Token。服务器不保存会话，天然支持水平扩展和分布式部署。"

### 六、面试高频 Q&A

**Q1：什么是RESTful？**

> URL名词+HTTP动词+无状态。GET获取、POST创建、PUT全量更新、PATCH部分更新、DELETE删除。

**Q2：PUT和PATCH的区别？**

> PUT全量更新必须传完整资源；PATCH部分更新只传修改的字段。实际开发中PATCH更常用。

**Q3：为什么无状态？**

> 无状态让每次请求独立，服务器不保存会话，便于水平扩展和分布式部署。认证用JWT Token。

---

## 5.3 设计模式（单例/工厂/观察者/策略）

### 一、设计原则速记

> **开闭原则（最重要）：** 对扩展开放，对修改关闭。加新功能不修改已有代码，通过新增类/方法扩展。

### 二、单例模式（Singleton）

**核心：** 一个类全局只有一个实例。

#### 饿汉式（线程安全，类加载时就创建）

```java
public class Singleton {
    private static final Singleton INSTANCE = new Singleton();
    private Singleton() {}
    public static Singleton getInstance() { return INSTANCE; }
}
```

缺点：不管用不用都会创建，浪费内存。

#### 懒汉式 DCL（面试必问）

```java
public class Singleton {
    private static volatile Singleton instance;
    private Singleton() {}
    public static Singleton getInstance() {
        if (instance == null) {                    // 第一次检查（避免不必要的锁）
            synchronized (Singleton.class) {
                if (instance == null) {            // 第二次检查（防止并发重复创建）
                    instance = new Singleton();
                }
            }
        }
        return instance;
    }
}
```

**为什么要两次null检查？**

```text
线程A和B同时调用getInstance()：
① 两个线程都通过第一次检查(instance == null)  ← 没锁，可以并发
② 线程A获取锁，创建实例，释放锁
③ 线程B获取锁，如果没有第二次检查 → 又创建一个实例！
④ 所以锁里面还要再检查一次
```

**为什么要volatile？**

```text
new Singleton() 分三步：①分配内存 → ②初始化对象 → ③引用赋值
JVM可能重排序为 ①→③→②，导致线程B拿到未初始化的对象
volatile禁止指令重排序，保证按顺序执行
```

> **面试一句话：** "DCL双重检查锁+volatile是最经典的单例实现。volatile禁止指令重排序，两次null检查——第一次避免不必要的锁，第二次防止并发重复创建。"

### 三、工厂模式（Factory）

**核心：** 封装对象创建，调用方不依赖具体类。

```java
interface LLMService { String chat(String message); }
class DeepSeekService implements LLMService { ... }
class OllamaService implements LLMService { ... }

class LLMFactory {
    public static LLMService create(String provider) {
        if ("deepseek".equals(provider)) return new DeepSeekService();
        if ("ollama".equals(provider)) return new OllamaService();
        throw new IllegalArgumentException("不支持: " + provider);
    }
}
// 调用方只依赖接口，不关心具体实现
LLMService service = LLMFactory.create("deepseek");
```

> **面试一句话：** "工厂模式将对象创建与使用解耦。调用方只依赖接口不依赖具体实现，新增实现时调用方代码不用改。"

### 四、观察者模式（Observer）

**核心：** 一对多依赖，状态变化时自动通知所有观察者。

```java
interface OrderEventListener { void onOrderCreated(Order order); }

class OrderService {
    private List<OrderEventListener> listeners = new ArrayList<>();
    void addListener(OrderEventListener l) { listeners.add(l); }
    void createOrder(Order order) {
        orderDao.save(order);                     // 核心业务
        for (OrderEventListener l : listeners) {  // 通知所有观察者
            l.onOrderCreated(order);
        }
    }
}

// 各自独立处理：发邮件、扣库存、加积分
orderService.addListener(new EmailNotifier());
orderService.addListener(new InventoryUpdater());
orderService.addListener(new PointsService());
```

**应用场景：** Vue响应式(数据→视图)、Spring事件机制、消息队列(发布订阅)

> **面试一句话：** "观察者模式是一对多依赖，状态变化自动通知。好处是解耦：被观察者不需要知道有哪些观察者，新增观察者不影响已有代码。"

### 五、策略模式（Strategy）

**核心：** 算法封装为独立策略类，运行时可替换。消除if-else，符合开闭原则。

```java
interface PaymentStrategy { void pay(double amount); }
class AlipayStrategy implements PaymentStrategy { public void pay(double a) { /* 支付宝具体支付逻辑 */ } }
class WechatPayStrategy implements PaymentStrategy { public void pay(double a) { /* 微信具体支付逻辑 */ } }

class PaymentContext {
    private PaymentStrategy strategy; // 当前使用的支付方式
    void setStrategy(PaymentStrategy s) { this.strategy = s; } // 可以随时切换支付方式
    void pay(double amount) { strategy.pay(amount); } // 委托给具体的支付方式去执行
}

// 运行时切换策略
ctx.setStrategy(new AlipayStrategy());  ctx.pay(100); // 输出：用支付宝支付100元
ctx.setStrategy(new WechatPayStrategy()); ctx.pay(200);  // 切换！ 输出：用微信支付200元
// 新增支付方式？只新增一个策略类，不改已有代码
```

```java
// ❌ 没有策略模式：一堆if-else
void pay(String type, double amount) {
    if ("alipay".equals(type)) { ... }
    else if ("wechat".equals(type)) { ... }
    else if ("bank".equals(type)) { ... }   // 每加一种就改这里
}

// ✅ 有策略模式：加新支付方式只新增一个策略类，符合开闭原则
```

> **面试一句话：** "策略模式将不同算法封装为独立策略类，运行时切换。消除if-else，新增策略只新增类不修改已有代码，完全符合开闭原则。"

### 六、总结

| 模式 | 核心思想 | 解决什么问题 | 项目体现 |
|------|----------|-------------|---------|
| 单例 | 全局唯一实例 | 避免重复创建浪费资源 | LLMFactory、连接池 |
| 工厂 | 封装创建逻辑 | 调用方不依赖具体类 | LLMFactory创建服务 |
| 观察者 | 一对多通知 | 解耦事件发送和接收 | Vue响应式、Spring事件 |
| 策略 | 算法可替换 | 消除if-else | LLM Provider切换 |

---

# 模块二：MySQL 数据库

## 2.1 MySQL 基本操作

### 一、CRUD 增删改查

```sql
-- 创建表
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    age INT DEFAULT 0,
    email VARCHAR(100) UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 增
INSERT INTO users (name, age, email) VALUES ('张三', 25, 'zs@mail.com');
INSERT INTO users (name, age) VALUES ('李四', 30), ('王五', 28);  -- 批量插入

-- 删
DELETE FROM users WHERE id = 1;          -- 条件删除（可回滚）
TRUNCATE TABLE users;                     -- 清空整表（更快，不可回滚，重置自增ID）

-- 改
UPDATE users SET age = 26, name = '张三丰' WHERE name = '张三';

-- 查
SELECT * FROM users;                                         -- 所有字段
SELECT name, age FROM users WHERE age > 20;                  -- 指定字段+条件
SELECT * FROM users ORDER BY age DESC LIMIT 10 OFFSET 20;    -- 排序+分页
SELECT COUNT(*), AVG(age) FROM users WHERE age > 20;         -- 聚合函数
```

### 二、DELETE vs TRUNCATE（面试常问）

|  | DELETE | TRUNCATE |
|--|-------|----------|
| 本质 | DML，逐行删除 | DDL，删除表再重建 |
| WHERE | 支持 | 不支持 |
| 速度 | 慢（逐行记录undo log） | 快（直接释放数据页） |
| 回滚 | 可以（有undo log） | 不可以 |
| 自增ID | 不重置 | 重置为1 |
| 触发器 | 触发DELETE触发器 | 不触发 |

> **面试一句话：** "DELETE是DML逐行删除可回滚，TRUNCATE是DDL重建表不可回滚但速度快。清空大表用TRUNCATE，条件删除用DELETE。"

### 三、JOIN 连接查询（面试必问）

```sql
-- 内连接(INNER JOIN)：只返回两表都有匹配的行
SELECT u.name, o.amount
FROM users u INNER JOIN orders o ON u.id = o.user_id;
-- 结果：张三-100, 张三-200, 李四-150（王五无订单被排除）

-- 左连接(LEFT JOIN)：左表全保留，右表没匹配填NULL
SELECT u.name, o.amount
FROM users u LEFT JOIN orders o ON u.id = o.user_id;
-- 结果：张三-100, 张三-200, 李四-150, 王五-NULL
```

### 四、GROUP BY + 聚合函数 + SQL执行顺序

```sql
SELECT user_id, COUNT(*) as order_count, SUM(amount) as total
FROM orders
WHERE status = 'paid'              -- WHERE：分组前过滤原始行
GROUP BY user_id
HAVING total > 100                 -- HAVING：分组后过滤结果（能用聚合函数）
ORDER BY total DESC
LIMIT 10;
```

**SQL执行顺序（面试常问）：** `FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT`

|  | WHERE | HAVING |
|--|-------|--------|
| 过滤时机 | 分组前 | 分组后 |
| 能用聚合函数 | 不能 | 能 |

### 五、子查询与 IN vs EXISTS

|  | IN | EXISTS |
|--|-----|--------|
| 子表结果小 | 优先用IN | - |
| 外表数据小 | - | 优先用EXISTS |

### 六、面试高频 Q&A

**Q1：DELETE和TRUNCATE的区别？**

> DELETE是DML逐行删除支持WHERE可回滚；TRUNCATE是DDL重建表不支持WHERE不可回滚但速度快，且重置自增ID。

**Q2：INNER JOIN和LEFT JOIN的区别？**

> INNER JOIN只返回两表匹配的行（取交集）；LEFT JOIN返回左表所有行，右表无匹配填NULL。

**Q3：WHERE和HAVING的区别？**

> WHERE在分组前过滤原始行不能用聚合函数；HAVING在分组后过滤能用聚合函数(COUNT/SUM等)。

---

## 2.2 MySQL 索引

### 一、为什么需要索引

没有索引要全表扫描，100万行比较100万次。有索引通过B+树快速定位，100万行只需约20次比较。

### 二、B+ 树结构（面试必问）

```text
                    [30 | 60]                     ← 根节点（只存key）
                  ╱          ╲
         [10|20|30]        [40|50|60]              ← 中间节点（只存key）
        ╱    |    ╲        ╱    |    ╲
     [1-10] [11-20] [21-30] [31-40] [41-50] [51-60] ← 叶子节点（key+完整数据）
        ↑      ↑      ↑      ↑      ↑      ↑
        └──────┴──────┴──────┴──────┴──────┘
              叶子节点之间用双向链表连接
```

**B+ 树的三大特点（为什么选B+树）：**

| 特点 | 说明 | 好处 |
|------|------|------|
| 非叶子节点只存key | 中间节点不存数据，能存更多key | 树更矮，磁盘IO更少（InnoDB一页16KB能存上百个key） |
| 数据全在叶子节点 | 查任何数据都要走到叶子 | 查询性能稳定（都是O(log n)） |
| 叶子节点双向链表 | 范围查询时顺着链表走 | 范围查询极快（WHERE id BETWEEN 10 AND 50） |

**为什么不用其他数据结构？**

| 数据结构 | 问题 |
|----------|------|
| 二叉搜索树 | 100万数据树高约20层，每层一次磁盘IO太慢 |
| Hash | 等值查询O(1)极快，但不支持范围查询和排序 |
| B树 | 非叶子节点也存数据，每层能存的key少，树更高 |

> **面试一句话：** "MySQL用B+树因为：非叶子只存key使树更矮减少IO，数据全在叶子使查询稳定，叶子链表使范围查询高效。不用Hash因为不支持范围查询。"

### 三、聚簇索引 vs 非聚簇索引（面试高频）

**聚簇索引（主键索引）：** 叶子节点直接存完整行数据，一张表只有一个。

**非聚簇索引（二级索引）：** 叶子节点存主键ID，需要**回表**查主键索引树拿完整数据。

```text
查找 name='张三' 的完整数据（name有二级索引）：
步骤1：在name索引树找到 name='张三' → 得到主键 id=5
步骤2：回主键索引树用 id=5 找完整行数据    ← 这就是"回表"
```

### 四、覆盖索引（面试常问）

查询的所有字段都在索引中，不需要回表。EXPLAIN的Extra显示 `Using index`。

```sql
-- 联合索引 idx_name_age (name, age)
-- ✅ 覆盖索引：只需要name和age，索引里都有，不回表
SELECT name, age FROM users WHERE name = '张三';
-- ❌ 不是覆盖索引：还需要email，索引里没有，得回表
SELECT name, age, email FROM users WHERE name = '张三';
```

> **面试一句话：** "覆盖索引是查询字段都在索引中不需要回表。EXPLAIN中Extra显示Using index。实际优化中把常用查询字段建成联合索引实现覆盖。"

### 五、最左前缀匹配（面试必问）

联合索引 `(name, age, email)` 的匹配规则：从最左列开始，不能跳过中间列，遇范围查询停止。

```sql
-- ✅ 能用索引
WHERE name = '张三'                                    -- 匹配name
WHERE name = '张三' AND age = 25                       -- 匹配name,age
WHERE name = '张三' AND age = 25 AND email = 'zs@...'  -- 匹配全部

-- ❌ 不能用（跳过了最左列name）
WHERE age = 25
WHERE email = 'zs@...'

-- ⚠️ 只能用到name（age用了范围查询，后面的email断了）
WHERE name = '张三' AND age > 20 AND email = 'zs@...'
```

### 六、索引失效场景（面试必问）

| 场景 | 示例 | 优化方法 |
|------|------|----------|
| 函数计算 | `WHERE YEAR(create_time) = 2024` | `WHERE create_time >= '2024-01-01'` |
| 隐式类型转换 | `WHERE varchar_col = 123` | 确保类型一致 `= '123'` |
| LIKE左模糊 | `WHERE name LIKE '%张'` | 用全文索引或ES |
| OR无索引列 | `WHERE name='张三' OR age=25` | 给age也加索引 |
| 不等于 | `WHERE name != '张三'` | 视情况改用IN |

### 七、面试高频 Q&A

**Q1：为什么MySQL用B+树做索引？**

> 非叶子只存key树更矮IO更少，数据全在叶子查询稳定，叶子链表支持高效范围查询。

**Q2：什么是回表？怎么避免？**

> 二级索引查到主键后要回主键索引查完整数据叫回表。用覆盖索引（查询字段都在索引中）可避免。

**Q3：什么是最左前缀原则？**

> 联合索引从最左列开始依次匹配，不能跳过，遇范围查询停止。区分度高的字段放左边。

---

## 2.3 MySQL 事务

### 一、事务是什么？

事务（Transaction）是把一组 SQL 操作打包成一个**不可分割的工作单元**，要么全部成功，要么全部回滚。

```sql
-- 典型事务：银行转账（A给B转100元）
START TRANSACTION;                          -- 开启事务
UPDATE account SET balance = balance - 100 WHERE name = 'A';  -- A扣钱
UPDATE account SET balance = balance + 100 WHERE name = 'B';  -- B加钱
COMMIT;                                     -- 提交（两步都成功才持久化）

-- 如果中间出错：
ROLLBACK;                                   -- 回滚（撤销所有未提交的修改）
```

**自动提交（autocommit）机制：**
```sql
SHOW VARIABLES LIKE 'autocommit';           -- 默认ON，每条SQL都是独立事务
SET autocommit = 0;                          -- 关闭自动提交，需手动COMMIT
```

### 二、ACID 四大特性（面试必考）

| 特性 | 含义 | 通俗理解 | InnoDB 实现方式 |
|------|------|----------|-----------------|
| **原子性(A)** | 事务中的操作要么全做，要么全不做 | 转账两步要么都成功要么都不发生 | **undo log**（回滚日志）：记录修改前的旧值，ROLLBACK时用它恢复 |
| **一致性(C)** | 事务前后数据满足完整性约束 | 转账前后总金额不变 | 由 A+I+D 三个特性共同保证，是最终目的 |
| **隔离性(I)** | 并发事务互不干扰 | A转B的同时C转D，互不影响 | **锁 + MVCC**：写操作用锁互斥，读操作用MVCC快照 |
| **持久性(D)** | 已提交的数据永久保存 | COMMIT后断电也不丢数据 | **redo log**（重做日志）：WAL机制，先写日志再写磁盘，崩溃恢复用 |

> **面试一句话：** "A靠undo log回滚，C是目标靠AID保证，I靠锁和MVCC，D靠redo log的WAL机制——其中redo log是顺序写性能高，崩溃后用它重放已提交事务。"

#### redo log 工作原理（WAL：Write-Ahead Logging）

```
客户端执行 UPDATE
       ↓
  ① 修改 Buffer Pool 中的数据页（内存）
       ↓
  ② 先写 redo log（顺序写，很快）→ 落盘
       ↓
  ③ 返回客户端"修改成功"
       ↓
  ④ 后台线程择时将脏页刷回磁盘（随机写，较慢）
```

**为什么 redo log 能保证持久性？** 即使步骤④还没完成就断电，重启时 MySQL 会读取 redo log 重放已提交的修改。

#### undo log 工作原理

```
事务执行 UPDATE users SET age=30 WHERE id=1;（原 age=25）

undo log 记录：{ id:1, age:25 }  ← 旧值

ROLLBACK → 用 undo log 把 age 恢复为 25
```

### 三、并发事务的三个问题（面试高频）

用一个银行账户表演示，初始余额 balance = 1000：

#### 1. 脏读（Dirty Read）—— 读到别人还没提交的数据

```
时间线   事务A                              事务B
  T1     BEGIN;
  T2     UPDATE account SET balance=500      BEGIN;
         WHERE id=1;  -- 改了但没提交
  T3                                         SELECT balance FROM account
                                             WHERE id=1;  → 结果：500（脏数据！）
  T4     ROLLBACK;  -- A回滚了，余额恢复1000
  T5                                         -- B拿着500去做了业务判断，全错了！
```

**本质：** B读到了A**未提交**的数据。如果A回滚，B读到的是不存在的脏数据。

#### 2. 不可重复读（Non-Repeatable Read）—— 同一事务内两次读同一行结果不同

```
时间线   事务A                              事务B
  T1     BEGIN;
  T2     SELECT balance FROM account
         WHERE id=1;  → 结果：1000
  T3                                         BEGIN;
                                             UPDATE account SET balance=800
                                             WHERE id=1;
                                             COMMIT;  -- B提交了
  T4     SELECT balance FROM account
         WHERE id=1;  → 结果：800  ← 两次读的不一样！
```

**本质：** 同一事务内，两次读取**同一行**，内容被别人的UPDATE/DELETE改了。

#### 3. 幻读（Phantom Read）—— 两次查询结果的行数不同

```
时间线   事务A                              事务B
  T1     BEGIN;
  T2     SELECT * FROM account
         WHERE age > 20;  → 结果：3行
  T3                                         BEGIN;
                                             INSERT INTO account VALUES(4,'D',25);
                                             COMMIT;
  T4     SELECT * FROM account
         WHERE age > 20;  → 结果：4行  ← 多了一行"幻影"！
```

**本质：** 同一事务内，两次读取的**行数**不同，被别人的INSERT增加了行。

| 问题 | 触发操作 | 影响 |
|------|----------|------|
| 脏读 | 读到未提交的数据 | 数据根本不存在，业务判断全部错误 |
| 不可重复读 | UPDATE/DELETE | 同一行的值变了 |
| 幻读 | INSERT | 结果集的行数变了 |

### 四、四种隔离级别（面试必背）

| 隔离级别 | 脏读 | 不可重复读 | 幻读 | 性能 | MySQL实现 |
|----------|------|-----------|------|------|-----------|
| 读未提交(Read Uncommitted) | ❌ 可能 | ❌ 可能 | ❌ 可能 | 最高 | 无特殊处理 |
| 读已提交(Read Committed, RC) | ✅ 解决 | ❌ 可能 | ❌ 可能 | 高 | 每次SELECT生成新ReadView |
| 可重复读(Repeatable Read, RR) **默认** | ✅ 解决 | ✅ 解决 | ✅ 基本解决 | 中 | 第一次SELECT生成ReadView后复用 + 间隙锁 |
| 串行化(Serializable) | ✅ 解决 | ✅ 解决 | ✅ 完全解决 | 最低 | 所有操作加共享锁，完全串行 |

**为什么 MySQL 默认用 RR？** 兼顾了安全性和性能。RR级别通过 MVCC 快照读 + 间隙锁防幻读，解决了大多数并发问题。

```sql
-- 查看当前隔离级别
SELECT @@transaction_isolation;              -- 默认：REPEATABLE-READ

-- 修改隔离级别
SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;
```

### 五、事务的传播行为（Spring中常问）

| 传播行为 | 含义 |
|----------|------|
| REQUIRED（默认） | 有事务就加入，没有就新建 |
| REQUIRES_NEW | 总是新建事务，挂起当前事务 |
| NESTED | 嵌套事务，外层回滚内层也回滚，内层回滚不影响外层 |
| SUPPORTS | 有事务就加入，没有就以非事务运行 |
| NOT_SUPPORTED | 总是以非事务运行，挂起当前事务 |

### 六、面试高频问题

**Q1：ACID分别靠什么实现？**
> A靠undo log（记录旧值用于回滚），C是最终目标靠AID共同保证，I靠锁（写互斥）+MVCC（读快照），D靠redo log（WAL机制先写日志再写磁盘）。

**Q2：脏读、不可重复读、幻读的区别？**
> 脏读是读到未提交数据（数据无效），不可重复读是同一行被UPDATE导致两次读不同，幻读是被INSERT导致两次查询行数不同。严重程度递增。

**Q3：为什么MySQL默认用RR不用RC？**
> RR在安全和性能间取得平衡。RC每次SELECT都生成新ReadView开销大且不能防不可重复读，RR复用ReadView解决了不可重复读，配合间隙锁基本解决幻读。

**Q4：redo log 和 undo log 的区别？**
> redo log 记录"做了什么修改"用于崩溃恢复（保证持久性），undo log 记录"修改前的值"用于回滚（保证原子性）。redo log 是顺序写性能高，undo log 还用于MVCC版本链。

**Q5：大事务有什么问题？怎么优化？**
> 大事务持有锁时间长→并发度低，undo log积累多→占用空间，主从延迟增大。优化：拆分长事务、避免在事务中做RPC调用、用批量操作减少事务时间。

---

## 2.4 MVCC（多版本并发控制）

### 一、MVCC 是什么？为什么需要它？

**MVCC（Multi-Version Concurrency Control）** 是一种不加锁就能实现并发读的机制——**读写互不阻塞**。

- **没有MVCC时：** 读操作要加共享锁，写操作要加排他锁，读写互相等待，并发性能差
- **有了MVCC：** 读操作通过"快照"读历史版本，不跟写操作冲突；写操作之间仍然用锁互斥

**核心思想：** 给每行数据维护多个版本，读操作根据自己的"时间点"读取对应的版本。

### 二、MVCC 的三大核心组件

#### 1. 隐藏字段（每行数据自动带的）

InnoDB 为每行数据自动添加三个隐藏字段：

| 隐藏字段 | 大小 | 含义 |
|----------|------|------|
| `DB_TRX_ID` | 6字节 | 最后修改（INSERT/UPDATE）该行的事务ID |
| `DB_ROLL_PTR` | 7字节 | 回滚指针，指向 undo log 中该行的上一个版本 |
| `DB_ROW_ID` | 6字节 | 隐藏自增ID（没有主键时自动生成，有主键则没有） |

```
  ┌─────────────────────────────────┐
  │         一行数据的实际结构        │
  ├─────────────────────────────────┤
  │ DB_TRX_ID = 103  (谁最后改了我)  │
  │ DB_ROLL_PTR = 0x7F2A (指向上一个版本) │
  │ DB_ROW_ID = 1                    │
  │ name = '张三'                    │
  │ age = 30                         │
  └─────────────────────────────────┘
```

#### 2. undo log 版本链

每次 UPDATE 操作时，旧值不会直接覆盖，而是存入 undo log，通过 ROLL_PTR 串联成一个链表：

```
当前行数据          undo log版本链
┌──────────┐
│ TRX_ID=103│
│ ROLL_PTR ─┼──→ ┌──────────┐     ┌──────────┐
│ name='张三'│    │ TRX_ID=101│     │ TRX_ID=100│
│ age=30    │    │ ROLL_PTR ─┼──→  │ ROLL_PTR ─┼──→ NULL (原始INSERT版本)
└──────────┘     │ name='张三'│     │ name='张三'│
                 │ age=28    │     │ age=25    │
                 └──────────┘     └──────────┘
                 
  最新版本(age=30)  上一版本(age=28)  最初版本(age=25)
```

**用途：** 当某个事务需要看历史版本时，就沿着 ROLL_PTR 链往前找，直到找到可见的版本。

#### 3. ReadView（读视图）

ReadView 是事务在进行**快照读（普通SELECT）**时生成的一个"快照"，记录了"当前有哪些事务正在活跃"。

| ReadView 字段 | 含义 |
|---------------|------|
| `m_ids` | 生成 ReadView 时，所有**活跃（未提交）**事务的ID列表 |
| `min_trx_id` | m_ids 中最小的事务ID |
| `max_trx_id` | 下一个将要分配的事务ID（即当前最大事务ID + 1） |
| `creator_trx_id` | 创建该 ReadView 的事务自身的ID |

### 三、可见性判断规则（面试手画流程图）

当事务执行 SELECT 时，对每行数据沿着版本链从新到旧判断：

```
                    取出当前版本的 DB_TRX_ID
                            │
              ┌─────────────┴─────────────┐
              │                           │
      DB_TRX_ID == creator_trx_id ?    不等
      (是自己改的吗？)                    │
          │ 是                    ┌──────┴──────┐
          ↓                      │              │
       ✅ 可见            DB_TRX_ID <        DB_TRX_ID >=
                          min_trx_id ?        max_trx_id ?
                          (修改时所有事务      (ReadView之后
                           都已提交？)          才开始的？)
                           │ 是       │否       │是        │否
                           ↓         │         ↓         │
                        ✅ 可见      │      ❌ 不可见    │
                                    │                    │
                              在 m_ids 中？             │
                              (修改事务还活着吗？)        │
                               │ 是       │否            │
                               ↓         ↓              │
                            ❌ 不可见  ✅ 可见           │
                                                    沿 ROLL_PTR
                                                    找上一个版本
                                                    重新判断 ──→
```

**口诀：** 自己改的可见 → 比最小的还老可见 → 比最大的还新不可见 → 在活跃列表里不可见不在就可见 → 不可见就沿链往前找。

### 四、完整实例演示

假设有事务ID为 100、101、102、103、104：

```
初始数据：id=1, name='张三', age=25, TRX_ID=100

时间线：
T1: 事务102 UPDATE age=28   → undo链: [100(age=25)]
T2: 事务102 COMMIT
T3: 事务103 UPDATE age=30   → undo链: [102(age=28)] → [100(age=25)]
T4: 事务103 未提交（活跃中）
T5: 事务101 未提交（活跃中）

此时事务104执行 SELECT：
  ReadView = { m_ids=[101,103], min_trx_id=101, max_trx_id=105, creator_trx_id=104 }
  
  检查当前行 TRX_ID=103：
    103 ≠ 104（不是自己改的）
    103 ≥ 101（不满足 < min_trx_id）
    103 < 105（不满足 ≥ max_trx_id）
    103 在 m_ids=[101,103] 中 → ❌ 不可见（事务103还没提交）
    
  沿 ROLL_PTR 找到 TRX_ID=102, age=28：
    102 ≠ 104
    102 ≥ 101（不满足 < min_trx_id）
    102 < 105
    102 不在 m_ids=[101,103] 中 → ✅ 可见！（事务102已提交）
    
  结果：事务104 读到 age=28 ✅
```

### 五、RC vs RR 区别（面试必问，核心考点）

|  | RC（读已提交） | RR（可重复读） |
|--|----------------|----------------|
| ReadView 生成时机 | **每次 SELECT** 都生成新的 | **第一次 SELECT** 生成，后续复用 |
| 效果 | 每次读都能看到最新已提交数据 | 同事务内多次读结果一致 |
| 能否防止不可重复读 | ❌ 不能 | ✅ 能 |

**为什么RC不能防止不可重复读？**

```
时间线   事务A(RC)                           事务B
  T1     SELECT ... → 生成ReadView_1
         (此时 m_ids=[B], 看到age=28)
  T2                                         UPDATE age=30; COMMIT;
  T3     SELECT ... → 生成ReadView_2 ← 新的！
         (此时 m_ids=[], TRX_ID=103不在活跃列表)
         → 读到 age=30 ← 两次读的结果不同！
```

**为什么RR能防止不可重复读？**

```
时间线   事务A(RR)                           事务B
  T1     SELECT ... → 生成ReadView_1（复用）
         (此时 m_ids=[B], 看到age=28)
  T2                                         UPDATE age=30; COMMIT;
  T3     SELECT ... → 复用ReadView_1 ← 还是同一个！
         (TRX_ID=103在旧的m_ids中 → 不可见)
         → 沿链找到 TRX_ID=102 → 不在m_ids → age=28 ← 一致！
```

> **面试一句话：** "RC每次SELECT生成新ReadView所以能看到最新提交导致不可重复读，RR复用第一次的ReadView所以同事务内读到的始终一致——这就是RR防止不可重复读的根本原因。"

### 六、快照读 vs 当前读

|  | 快照读 | 当前读 |
|--|--------|--------|
| 操作 | 普通 SELECT | SELECT ... FOR UPDATE / LOCK IN SHARE MODE / INSERT / UPDATE / DELETE |
| 读到的是 | 历史快照版本（MVCC） | 最新已提交数据（加锁） |
| 是否加锁 | 不加锁 | 加行锁/间隙锁 |

> **注意：** MVCC 只对快照读（普通SELECT）生效。UPDATE、DELETE、FOR UPDATE 等操作都是当前读，直接读最新数据并加锁。

### 七、面试高频问题

**Q1：MVCC的实现原理？**
> 三个组件：隐藏字段（TRX_ID+ROLL_PTR）记录版本信息，undo log版本链保存历史数据，ReadView判断版本可见性。SELECT时沿版本链按可见性规则找到第一个可见版本。

**Q2：RC和RR的ReadView有什么区别？**
> RC每次SELECT都创建新ReadView，能看到其他事务最新提交的数据；RR只在第一次SELECT创建ReadView并复用，保证同事务内多次读取结果一致。

**Q3：MVCC能完全解决幻读吗？**
> 快照读能通过MVCC解决，但当前读（FOR UPDATE等）需要间隙锁配合。InnoDB在RR级别默认使用临键锁（Next-Key Lock）防止幻读。

---

## 2.5 MySQL 锁

### 一、锁的分类全景

```
                        MySQL 锁的分类
                           │
          ┌────────────────┼────────────────┐
          ↓                ↓                ↓
      按粒度分          按模式分          按算法分
     ┌──────┐        ┌──────┐        ┌──────┐
     │全局锁 │        │共享锁 │        │记录锁 │
     │表级锁 │        │排他锁 │        │间隙锁 │
     │行级锁 │        │意向锁 │        │临键锁 │
     └──────┘        └──────┘        └──────┘
```

#### 1. 全局锁

```sql
FLUSH TABLES WITH READ LOCK;    -- 整个数据库只读
-- 用于：全库逻辑备份（mysqldump --single-transaction更好）
UNLOCK TABLES;
```

**缺点：** 整个库只读，业务完全阻塞。生产环境一般不用。

#### 2. 表级锁

| 锁类型 | 加锁方式 | 特点 |
|--------|----------|------|
| 表锁 | `LOCK TABLES t READ/WRITE` | 粒度大，并发低 |
| 元数据锁(MDL) | 自动加（执行SQL时） | 防止DML与DDL冲突 |
| 意向锁(IS/IX) | 自动加（InnoDB） | 快速判断表里是否有行锁 |

**意向锁的作用（面试常问）：**

```
事务A: SELECT * FROM t WHERE id=1 FOR UPDATE;  → 给id=1加行级X锁，同时给表t加意向锁IX
事务B: LOCK TABLES t WRITE;                     → 要加表级X锁

没有意向锁时：B要遍历每一行看有没有行锁 → 太慢！
有意向锁时：B只看表上有没有IX/IS锁 → 快速判断！
```

**MDL（元数据锁）的场景：**

```
事务A: BEGIN; SELECT * FROM t;  → 自动加MDL读锁（防止DDL修改表结构）
事务B: ALTER TABLE t ADD COLUMN c INT;  → 等待MDL锁释放（被A阻塞）
-- 如果A一直不提交，B就一直等，后续所有对t的查询都会被B阻塞！→ 连锁阻塞
```

#### 3. 行级锁（InnoDB独有，面试重点）

**InnoDB行锁的三种形态：**

| 锁类型 | 锁什么 | 防止什么 | 加锁条件 |
|--------|--------|----------|----------|
| 记录锁(Record Lock) | 锁住**单行**索引记录 | 防止对该行的 UPDATE/DELETE | 精确匹配唯一索引 |
| 间隙锁(Gap Lock) | 锁住两行之间的**间隙**（开区间） | 防止 INSERT（别人插不进来） | 范围查询、非唯一索引 |
| 临键锁(Next-Key Lock) **默认** | 记录锁 + 前面的间隙锁（左开右闭） | 同时防修改和防插入 → **防幻读** | InnoDB默认行锁算法 |

**图解三种行锁的关系：**

```
假设表中有 id=5, id=10, id=15 三行数据

索引排列：  (-∞, 5)  [5]  (5, 10)  [10]  (10, 15)  [15]  (15, +∞)

记录锁：          [5]       [10]         [15]          ← 只锁行本身
间隙锁：  (-∞,5)    (5,10)     (10,15)     (15,+∞)    ← 只锁间隙
临键锁：  (-∞,5]    (5,10]     (10,15]     (15,+∞]    ← 间隙 + 行（左开右闭）
```

### 二、InnoDB 加锁规则（重要！）

InnoDB 的行锁是**加在索引上的**，不是加在数据行上的：

```sql
-- 情况1：通过索引精确匹配 → 加记录锁
SELECT * FROM users WHERE id = 1 FOR UPDATE;  -- id是主键 → 只锁id=1这一行

-- 情况2：通过非唯一索引匹配 → 加临键锁
SELECT * FROM users WHERE name = '张三' FOR UPDATE;  -- name是普通索引
-- 锁住 name索引的间隙 + 行，同时锁住对应的主键索引行

-- 情况3：不走索引（全表扫描）→ 锁所有行！
SELECT * FROM users WHERE age = 25 FOR UPDATE;  -- age没有索引
-- 表中每一行都被锁住！严重影响并发
```

> **面试一句话：** "InnoDB的行锁是加在索引上的。如果没有用到索引，行锁会退化为表锁——所以一定要确保UPDATE/DELETE走了索引。"

### 三、共享锁 vs 排他锁

|  | 共享锁(S锁/读锁) | 排他锁(X锁/写锁) |
|--|-----------------|-----------------|
| 加锁SQL | `SELECT ... LOCK IN SHARE MODE` | `SELECT ... FOR UPDATE` |
| 读操作 | 允许其他事务加S锁（可并行读） | 阻塞其他S锁和X锁 |
| 写操作 | 阻塞其他事务的X锁 | 阻塞其他S锁和X锁 |
| 兼容性 | S和S兼容，S和X互斥 | X和任何锁都互斥 |

```sql
-- 共享锁示例
SELECT * FROM users WHERE id = 1 LOCK IN SHARE MODE;  -- 加S锁
-- 其他事务可以继续读（加S锁），但不能修改（被X锁阻塞）

-- 排他锁示例
SELECT * FROM users WHERE id = 1 FOR UPDATE;           -- 加X锁
-- 其他事务既不能加S锁也不能加X锁，必须等释放
```

### 四、死锁（面试高频）

#### 死锁是怎么发生的？

```
时间线   事务A                              事务B
  T1     UPDATE users SET age=30
         WHERE id=1;  → 获得id=1的X锁
  T2                                         UPDATE users SET age=28
                                             WHERE id=2;  → 获得id=2的X锁
  T3     UPDATE users SET age=28
         WHERE id=2;  → 等待B释放id=2的锁...
  T4                                         UPDATE users SET age=30
                                             WHERE id=1;  → 等待A释放id=1的锁...
                                             
  💀 A等B，B等A → 死锁！
```

#### 死锁的四个必要条件

| 条件 | 含义 | 破坏方式 |
|------|------|----------|
| 互斥 | 资源同时只能被一个事务持有 | 无法破坏（锁的本质） |
| 持有并等待 | 持有资源的同时等待其他资源 | 一次性获取所有锁 |
| 不可剥夺 | 已持有的锁不能被强制释放 | 设置锁超时（innodb_lock_wait_timeout） |
| 循环等待 | A等B，B等A | 按固定顺序加锁 |

#### InnoDB 死锁检测与处理

```sql
-- 查看锁等待超时时间（默认50秒）
SHOW VARIABLES LIKE 'innodb_lock_wait_timeout';

-- 查看死锁日志
SHOW ENGINE INNODB STATUS;
```

**InnoDB 自动死锁检测：** 当检测到死锁时，会自动回滚持有锁最少的那一个事务（代价最小的），让另一个事务继续执行。

#### 如何避免死锁？

1. **按固定顺序访问表和行**（最重要）：总是先操作id小的再操作id大的
2. **保持事务简短**：减少持锁时间
3. **合理使用索引**：避免锁升级为表锁
4. **降低隔离级别**：RC比RR锁的范围小（RC没有间隙锁）

### 五、锁和 MVCC 配合防幻读的完整机制

```
RR级别下防幻读的完整策略：

快照读（普通SELECT）：
  → MVCC 通过 ReadView 读历史快照 → 天然防幻读

当前读（FOR UPDATE / INSERT / UPDATE / DELETE）：
  → 临键锁（Next-Key Lock）锁住行+间隙
  → 别人INSERT不进来 → 防幻读
```

### 六、面试高频问题

**Q1：InnoDB有哪些行锁？**
> 三种：记录锁（锁单行）、间隙锁（锁间隙防INSERT）、临键锁（前两者之和，默认算法）。临键锁在RR级别下配合MVCC防止幻读。

**Q2：InnoDB的行锁是锁什么的？**
> 行锁是加在**索引**上的，不是加在数据行上。如果SQL没有走索引，行锁会退化为锁住所有行（效果等于表锁）。

**Q3：什么是意向锁？有什么用？**
> 意向锁是表级锁，在加行锁之前自动加。作用是让判断"表里有没有行锁"变快——不用遍历每行，只需看表上有没有意向锁。

**Q4：怎么避免死锁？**
> 1.按固定顺序操作行 2.保持事务简短 3.确保SQL走索引 4.设置合理的锁超时时间。InnoDB会自动检测死锁并回滚代价最小的事务。

**Q5：RR级别怎么防幻读的？**
> 快照读通过MVCC读历史版本防幻读，当前读通过临键锁（记录锁+间隙锁）阻止其他事务INSERT到间隙中，两种机制配合实现。

---

## 2.6 SQL 优化

### 一、慢查询分析：EXPLAIN 执行计划

EXPLAIN 是 SQL 优化的第一步——先看 MySQL 是怎么执行这条 SQL 的。

```sql
EXPLAIN SELECT * FROM users WHERE age > 20 ORDER BY name;
```

| 字段 | 含义 | 理想值 | 说明 |
|------|------|--------|------|
| **id** | 执行序号 | 从大到小执行 | 子查询会有多个id，越大越先执行 |
| **select_type** | 查询类型 | SIMPLE | SIMPLE(简单查询)、PRIMARY(主查询)、SUBQUERY(子查询) |
| **table** | 访问哪张表 | - | 显示正在访问的表名 |
| **type** | 访问类型（最重要） | ref/range | 从好到差：system > const > eq_ref > ref > range > index > **ALL** |
| **possible_keys** | 可能用到的索引 | 不为NULL | 显示有哪些候选索引 |
| **key** | 实际用了哪个索引 | 不为NULL | NULL说明没走索引！ |
| **key_len** | 索引使用的字节数 | 越短越好 | 判断复合索引用了几个字段 |
| **ref** | 索引查找的参考 | const/字段名 | 与索引比较的列或常量 |
| **rows** | 预估扫描行数 | 越少越好 | 100万行里扫100行 vs 扫100万行 |
| **Extra** | 额外信息 | Using index | 见下方详细说明 |

#### type 字段排序（从优到差）

| type | 含义 | 示例 |
|------|------|------|
| **system** | 表中只有一行 | 几乎不会遇到 |
| **const** | 通过主键/唯一索引精确匹配一行 | `WHERE id = 1` |
| **eq_ref** | JOIN时被驱动表通过主键/唯一索引匹配 | `JOIN ... ON t1.id = t2.id` |
| **ref** | 通过普通索引匹配（可能多行） | `WHERE name = '张三'`（name有索引） |
| **range** | 索引范围扫描 | `WHERE age BETWEEN 20 AND 30` |
| **index** | 全索引扫描（遍历整棵B+树） | `SELECT id FROM users`（id是主键） |
| **ALL** | **全表扫描**（最差！） | `WHERE age = 25`（age无索引） |

> **面试一句话：** "type从好到差是 system > const > eq_ref > ref > range > index > ALL。至少要达到ref级别，ALL说明没走索引必须优化。"

#### Extra 字段关键值

| Extra 值 | 含义 | 好坏 |
|----------|------|------|
| **Using index** | 覆盖索引，不需要回表 | ✅ 非常好 |
| Using where | Server层过滤（存储引擎返回多余数据） | 一般 |
| Using index condition | 索引下推（ICP），在存储引擎层过滤 | ✅ 较好 |
| **Using filesort** | 需要额外排序（没走索引排序） | ❌ 需优化 |
| **Using temporary** | 使用了临时表（GROUP BY没走索引） | ❌ 需优化 |
| Using join buffer | JOIN没有索引用了缓存 | ❌ 需优化 |

### 二、索引失效的常见场景（面试高频）

#### 1. 对索引列使用函数或运算

```sql
-- ❌ 索引失效：在索引列上使用了函数
SELECT * FROM users WHERE YEAR(created_at) = 2024;
SELECT * FROM users WHERE LEFT(name, 1) = '张';

-- ✅ 索引有效：改写为范围查询
SELECT * FROM users WHERE created_at >= '2024-01-01' AND created_at < '2025-01-01';
SELECT * FROM users WHERE name LIKE '张%';
```

#### 2. 隐式类型转换

```sql
-- 假设 phone 是 VARCHAR 类型
-- ❌ 索引失效：字符串列与数字比较，MySQL会把字符串转数字
SELECT * FROM users WHERE phone = 13800138000;

-- ✅ 索引有效：用字符串比较
SELECT * FROM users WHERE phone = '13800138000';
```

#### 3. 最左前缀原则（复合索引）

```sql
-- 假设有复合索引 idx_abc(a, b, c)

-- ✅ 走索引
WHERE a = 1;
WHERE a = 1 AND b = 2;
WHERE a = 1 AND b = 2 AND c = 3;

-- ❌ 不走索引（跳过了最左列a）
WHERE b = 2;
WHERE c = 3;
WHERE b = 2 AND c = 3;

-- ⚠️ 部分走索引（只用了a列）
WHERE a = 1 AND c = 3;  -- 只走a的索引，c无法利用索引

-- ✅ 范围查询后的列失效
WHERE a > 1 AND b = 2;  -- 只走a的索引（a是范围查询后b无法用索引）
```

> **面试一句话：** "复合索引遵循最左前缀原则，查询条件必须从索引最左列开始连续匹配。遇到范围查询（>、<、BETWEEN、LIKE）后，右边的列无法使用索引。"

#### 4. LIKE 以通配符开头

```sql
-- ❌ 索引失效：%开头无法走B+树索引
SELECT * FROM users WHERE name LIKE '%张%';
SELECT * FROM users WHERE name LIKE '%张';

-- ✅ 索引有效：前缀匹配可以用索引
SELECT * FROM users WHERE name LIKE '张%';
```

#### 5. OR 条件中有一个列没有索引

```sql
-- 假设 name 有索引，age 没有索引
-- ❌ 索引失效：OR连接时只要有一个条件没索引，整个就不走索引
SELECT * FROM users WHERE name = '张三' OR age = 25;

-- ✅ 索引有效：两个条件都有索引时OR可以走索引
-- 或者用UNION ALL拆分
SELECT * FROM users WHERE name = '张三'
UNION ALL
SELECT * FROM users WHERE age = 25;
```

#### 6. NOT IN、NOT EXISTS、!= （通常不走索引）

```sql
-- ❌ 通常不走索引
SELECT * FROM users WHERE age != 25;
SELECT * FROM users WHERE age NOT IN (20, 25, 30);

-- ✅ 改写为正向查询
SELECT * FROM users WHERE age > 25 OR age < 25;  -- 范围查询走索引
```

### 三、覆盖索引（面试必问）

**什么是覆盖索引？** 查询的所有字段都在索引中，不需要回表查主键索引。

```sql
-- 假设有复合索引 idx_name_age(name, age)

-- ✅ 覆盖索引：只需要name和age，都在索引中
SELECT name, age FROM users WHERE name = '张三';
-- Extra: Using index ← 表示覆盖索引

-- ❌ 非覆盖索引：还需要email，索引中没有，必须回表
SELECT name, age, email FROM users WHERE name = '张三';
-- Extra: NULL ← 需要回表查询
```

**图解回表 vs 覆盖索引：**

```
普通查询（需要回表）：
  二级索引树 → 找到主键ID → 回主键索引树 → 取出完整行数据
  （查了两棵树）

覆盖索引（不需要回表）：
  二级索引树 → 直接在索引中取到所有需要的字段 → 返回
  （只查了一棵树，快！）
```

> **面试一句话：** "覆盖索引是指查询的所有字段都在索引中，不需要回表。EXPLAIN中Extra显示Using index就是覆盖索引。优化时优先用覆盖索引减少IO。"

### 四、深分页优化

#### 问题：传统 LIMIT OFFSET 性能差

```sql
-- 查第100万页的数据（每页10条）
SELECT * FROM users ORDER BY id LIMIT 10 OFFSET 1000000;
-- MySQL需要扫描1000010行，然后丢弃前100万行 → 极慢！
```

#### 优化方案1：游标分页（推荐）

```sql
-- 第一页
SELECT * FROM users WHERE id > 0 ORDER BY id LIMIT 10;  -- 取到id最大值=10

-- 第二页（用上一页最后一个id）
SELECT * FROM users WHERE id > 10 ORDER BY id LIMIT 10;  -- 取到id最大值=20

-- 第三页
SELECT * FROM users WHERE id > 20 ORDER BY id LIMIT 10;
```

**原理：** 每次直接定位到起始位置，不需要跳过前面的行。适合"上一页/下一页"的场景，不支持跳页。

#### 优化方案2：子查询延迟关联

```sql
-- ❌ 原始写法：慢
SELECT * FROM users ORDER BY id LIMIT 10 OFFSET 1000000;

-- ✅ 优化写法：先用子查询在索引上定位id，再回表
SELECT * FROM users
INNER JOIN (
    SELECT id FROM users ORDER BY id LIMIT 10 OFFSET 1000000
) AS tmp ON users.id = tmp.id;
```

**原理：** 子查询只查id（走覆盖索引，不回表），快速定位10个id，再精确回表取10行数据。

#### 优化方案3：业务层优化

```sql
-- 限制最大翻页数
-- 比如只允许看前100页，超过则提示"请使用搜索缩小范围"
SELECT * FROM users ORDER BY id LIMIT 10 OFFSET 990;  -- 最多到第100页
```

### 五、其他优化策略

| 优化方向 | 做法 | 原因 |
|----------|------|------|
| 避免 SELECT * | 只查需要的字段 | 减少数据传输量，可能利用覆盖索引 |
| 小表驱动大表 | 小结果集做外表 | 减少循环次数 |
| EXISTS 替代 IN | 子查询结果集大时用EXISTS | EXISTS一旦匹配就返回，IN要全部计算 |
| 批量代替循环 | 用批量INSERT代替循环单条INSERT | 减少事务次数和网络往返 |
| 合理使用索引 | 在区分度高的列上建索引 | 性别这种只有2个值的列建索引没意义 |
| 分库分表 | 单表超500万行时考虑 | 减少单表数据量 |

```sql
-- 小表驱动大表示例
-- ❌ 大IN：先查出10万个id再去users表查
SELECT * FROM users WHERE id IN (SELECT user_id FROM orders WHERE status = 'paid');
-- orders有100万行匹配

-- ✅ EXISTS：users表小，用EXISTS让MySQL优化
SELECT * FROM users WHERE EXISTS (
    SELECT 1 FROM orders WHERE orders.user_id = users.id AND orders.status = 'paid'
);
```

### 六、索引下推（Index Condition Pushdown, ICP）

MySQL 5.6+ 的优化，在**存储引擎层**就过滤掉不满足条件的数据，减少回表次数。

```sql
-- 假设有复合索引 idx_name_age(name, age)

-- 没有ICP时：
-- 存储引擎：根据name='张'找到所有行 → 全部返回给Server层
-- Server层：再过滤age > 20
-- 回表次数：所有name LIKE '张%'的行都要回表

-- 有ICP时：
-- 存储引擎：根据name='张'找到行，同时在本层检查age > 20 → 只返回满足条件的
-- Server层：直接得到结果
-- 回表次数：只对满足age > 20的行回表 → 大幅减少！
```

> **面试一句话：** "索引下推ICP是MySQL 5.6的优化，在存储引擎层利用索引字段提前过滤，减少回表次数。EXPLAIN中Extra显示Using index condition。"

### 七、面试高频问题

**Q1：怎么分析一条慢SQL？**
> 先用EXPLAIN看执行计划：重点看type（访问类型）、key（是否走索引）、rows（扫描行数）、Extra（额外信息）。type是ALL就说明全表扫描要加索引，Extra有Using filesort/Using temporary需要优化ORDER BY和GROUP BY。

**Q2：什么情况下索引会失效？**
> 六种常见情况：①索引列用函数/运算 ②隐式类型转换 ③违反最左前缀原则 ④LIKE以%开头 ⑤OR中有无索引列 ⑥NOT IN/!=等否定条件。

**Q3：什么是覆盖索引？**
> 查询的所有字段都在索引中，不需要回表查主键索引。EXPLAIN的Extra显示Using index。覆盖索引减少了IO次数，是SQL优化的重要手段。

**Q4：深分页怎么优化？**
> 三种方案：①游标分页 WHERE id > 上次最大值 LIMIT n（推荐，但不支持跳页）②子查询延迟关联，先在索引上定位id再回表 ③业务层限制最大翻页数。

**Q5：复合索引的最左前缀原则？**
> 复合索引(a,b,c)相当于创建了a、(a,b)、(a,b,c)三个索引。查询条件必须从最左列开始连续匹配，遇到范围查询后右边的列无法使用索引。

---

# 模块六：测试技术

> 简历项目二「智测星图」涉及的核心技术栈：pytest + requests + YAML + Allure + Jenkins
> 对应项目实战：API自动化测试框架，包含单接口测试和业务场景测试

## 6.1 pytest 测试框架

### 一、pytest 是什么？

pytest 是 Python 最流行的测试框架，相比 unittest：
- 语法更简洁（不需要写类，普通函数就行）
- 自动发现测试（文件以test_开头，函数以test_开头）
- 强大的 fixture 机制（替代 setup/teardown）
- 丰富的插件生态（allure、xdist并行等）

```bash
# 安装
pip install pytest pytest-html pytest-xdist pytest-ordering pytest-rerunfailures

# 运行
pytest                          # 运行所有test_开头的文件
pytest test_login.py            # 运行指定文件
pytest -v                       # 详细输出
pytest -s                       # 显示print输出
pytest -k "login"               # 只运行名字包含login的用例
pytest -x                       # 遇到失败就停止
pytest --reruns 3               # 失败重跑3次
pytest -n 4                     # 4个进程并行执行
```

### 二、pytest 配置文件 pytest.ini

```ini
[pytest]
# 指定测试文件的命名规则
python_files = test_*.py
# 指定测试类的命名规则
python_classes = Test*
# 指定测试函数的命名规则
python_functions = test*

# 添加命令行参数（每次运行自动带上）
addopts = -v -s --alluredir=./report/temp --clean-alluredir

# 忽略警告
filterwarnings =
    ignore::DeprecationWarning
    ignore::UserWarning
```

> **面试一句话：** "pytest通过pytest.ini配置文件统一管理测试规则，python_files/classes/functions控制测试发现规则，addopts指定默认运行参数。"

### 三、fixture 机制（pytest核心，面试必问）

fixture 是 pytest 的**依赖注入**机制——在测试前准备数据、测试后清理数据。

#### 1. 基本用法

```python
import pytest

# 定义fixture
@pytest.fixture
def sample_data():
    data = {"name": "张三", "age": 25}
    yield data                    # yield之前=setup，yield之后=teardown
    print("清理数据")              # 测试完成后执行

# 使用fixture（通过函数名注入）
def test_user_info(sample_data):  # 参数名=fixture函数名
    assert sample_data["name"] == "张三"
    assert sample_data["age"] == 25
```

#### 2. fixture 的作用域（scope）

| scope | 生命周期 | 执行时机 |
|-------|----------|----------|
| `function`（默认） | 每个测试函数 | 每个测试前后各一次 |
| `class` | 每个测试类 | 类中所有测试前后各一次 |
| `module` | 每个.py文件 | 文件中所有测试前后各一次 |
| `session` | 整个测试会话 | 所有测试前后各一次 |

```python
# session级别：整个测试会话只执行一次（比如登录获取token）
@pytest.fixture(scope="session")
def login_token():
    response = requests.post("/api/login", json={"user": "admin", "pwd": "123"})
    token = response.json()["token"]
    yield token              # 所有测试共享这个token
    # teardown: 可以在这里做登出操作

# function级别：每个测试函数都执行
@pytest.fixture(scope="function")
def clean_database():
    # setup: 清空测试数据
    db.execute("DELETE FROM test_table")
    yield
    # teardown: 测试后清理
    db.execute("DELETE FROM test_table")
```

#### 3. autouse 自动使用

```python
@pytest.fixture(autouse=True)
def start_test_and_end():
    """每个测试自动执行，不需要手动传参"""
    print("=== 测试开始 ===")        # setup
    yield
    print("=== 测试结束 ===")        # teardown
```

#### 4. conftest.py —— fixture的共享文件

```
project/
├── conftest.py          ← 全局fixture（所有目录共享）
├── testcase/
│   ├── conftest.py      ← testcase目录下的fixture（该目录下共享）
│   ├── test_login.py
│   └── test_order.py
```

```python
# conftest.py（全局）
import pytest
import yaml

@pytest.fixture(scope="session", autouse=True)
def clear_extract():
    """测试会话开始时清空数据提取文件"""
    with open("extract.yaml", "w") as f:
        yaml.dump({}, f)
    yield                           # 所有测试执行
    print("所有测试完成")

@pytest.fixture(scope="session", autouse=True)
def system_login():
    """自动登录——在所有测试之前获取token"""
    # 发送登录请求
    response = requests.post("/api/login", json={...})
    token = response.json()["data"]["token"]
    # 存入extract.yaml供后续测试使用
    with open("extract.yaml", "a") as f:
        yaml.dump({"token": token}, f)
```

> **面试一句话：** "fixture是pytest的依赖注入机制，通过yield实现setup/teardown。scope控制生命周期（function/class/module/session）。conftest.py是fixture的共享文件，不需要import，pytest自动发现。"

### 四、参数化 @pytest.mark.parametrize

```python
import pytest

# 基本参数化：一组参数
@pytest.mark.parametrize("username, password, expected", [
    ("admin", "123456", "success"),
    ("admin", "wrong",  "fail"),
    ("",      "123456", "fail"),
])
def test_login(username, password, expected):
    result = login(username, password)
    assert result == expected

# 从YAML文件读取参数化数据（项目中的实际用法）
def get_testcase_yaml(filepath):
    """读取YAML测试用例文件"""
    with open(filepath, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return [(case["baseInfo"], case["testCase"]) for case in data]

@pytest.mark.parametrize("base_info, testcase", get_testcase_yaml("addUser.yaml"))
def test_add_user(base_info, testcase):
    allure.dynamic.title(testcase["case_name"])
    RequestBase().specification_yaml(base_info, testcase)
```

### 五、常用标记（mark）

```python
@pytest.mark.run(order=1)          # 指定执行顺序（需要pytest-ordering插件）
@pytest.mark.skip(reason="bug#123") # 跳过测试
@pytest.mark.xfail                  # 预期失败（失败不算异常）
@pytest.mark.parametrize(...)       # 参数化
@pytest.mark.smoke                  # 自定义标记（配合 -m 使用）

# 运行时过滤
pytest -m smoke                     # 只运行标记为smoke的测试
```

### 六、pytest 执行钩子（hooks）

```python
# conftest.py 中定义hooks

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """所有测试完成后自动调用——生成测试摘要"""
    total = terminalreporter._numcollected
    passed = len(terminalreporter.stats.get("passed", []))
    failed = len(terminalreporter.stats.get("failed", []))
    duration = round(terminalreporter.duration, 2)
    
    summary = f"""
    ======== 测试报告 ========
    总用例数：{total}
    通过：{passed}  失败：{failed}
    耗时：{duration}秒
    =========================
    """
    print(summary)
    # 可以在这里发送钉钉/企业微信通知
```

### 七、面试高频问题

**Q1：pytest和unittest的区别？**
> pytest语法更简洁（不需要继承TestCase类），fixture比setup/teardown更灵活（支持scope和依赖注入），断言直接用assert（unittest要用self.assertEqual），插件生态更丰富。unittest是Python内置的，pytest需要安装。

**Q2：fixture的scope有哪些？**
> function（默认，每个测试函数）、class（每个测试类）、module（每个.py文件）、session（整个测试会话）。scope越大生命周期越长，session适合做全局初始化如登录获取token。

**Q3：conftest.py是什么？**
> conftest.py是pytest的fixture共享文件，放在哪个目录就对哪个目录及其子目录生效。不需要import，pytest会自动发现并加载其中的fixture。

**Q4：参数化怎么做？**
> 用@pytest.mark.parametrize装饰器，第一个参数是变量名，第二个参数是参数列表。项目中从YAML读取测试数据再参数化，实现数据驱动测试。

---

## 6.2 requests 库 —— HTTP 接口测试

### 一、requests 基本用法

```python
import requests

# GET 请求
response = requests.get(
    url="http://localhost:8080/api/users",
    params={"page": 1, "size": 10},     # URL查询参数 ?page=1&size=10
    headers={"token": "abc123"}          # 请求头
)

# POST 请求（JSON格式）
response = requests.post(
    url="http://localhost:8080/api/users",
    json={"name": "张三", "age": 25},    # 自动设置 Content-Type: application/json
    headers={"token": "abc123"}
)

# POST 请求（表单格式）
response = requests.post(
    url="http://localhost:8080/api/login",
    data={"username": "admin", "password": "123456"}  # Content-Type: application/x-www-form-urlencoded
)

# PUT / DELETE
response = requests.put(url, json={...})
response = requests.delete(url)
```

### 二、Response 对象

```python
response = requests.get("http://localhost:8080/api/users/1")

response.status_code          # 200（HTTP状态码）
response.json()               # {"id": 1, "name": "张三"}（解析JSON响应体）
response.text                 # '{"id": 1, "name": "张三"}'（原始文本）
response.headers              # {'Content-Type': 'application/json', ...}
response.cookies              # 响应中的Cookie
response.elapsed.total_seconds()  # 响应耗时（秒）
response.encoding             # 响应编码
```

### 三、项目中封装的 SendRequest 类

```python
import requests
import allure
import json

class SendRequest:
    """统一请求封装——项目中所有HTTP请求都通过这个类"""
    
    def __init__(self):
        self.session = requests.Session()  # Session对象自动管理Cookie
    
    def run_main(self, method, url, data=None, headers=None, **kwargs):
        """
        统一请求入口
        根据method自动选择GET/POST/PUT/DELETE
        """
        method = method.upper()
        
        # 记录请求信息到Allure报告
        allure.attach(f"URL: {url}", "请求地址", allure.attachment_type.TEXT)
        allure.attach(json.dumps(data, ensure_ascii=False), "请求参数", allure.attachment_type.TEXT)
        
        try:
            if method == "GET":
                response = self.session.get(url, params=data, headers=headers, 
                                           timeout=60, verify=False)
            elif method == "POST":
                response = self.session.post(url, json=data, headers=headers,
                                            timeout=60, verify=False)
            elif method == "PUT":
                response = self.session.put(url, json=data, headers=headers,
                                           timeout=60, verify=False)
            elif method == "DELETE":
                response = self.session.delete(url, headers=headers,
                                              timeout=60, verify=False)
            
            # 记录响应到Allure
            allure.attach(response.text, "响应结果", allure.attachment_type.TEXT)
            
            # 统一返回格式
            result = {
                "status_code": response.status_code,
                "body": response.json(),
                "text": response.text,
                "cookies": dict(response.cookies),
                "elapsed": response.elapsed.total_seconds()
            }
            return result
            
        except requests.exceptions.ConnectionError:
            raise Exception("连接失败，请检查服务是否启动")
        except requests.exceptions.Timeout:
            raise Exception("请求超时")
        except requests.exceptions.RequestException as e:
            raise Exception(f"请求异常：{e}")
```

> **面试一句话：** "用requests.Session()管理会话，自动维护Cookie。封装统一请求入口根据method分发，统一异常处理和日志记录。verify=False跳过SSL验证，timeout=60防止请求卡死。"

### 四、Session 会话管理

```python
# ❌ 不用Session：每次请求都带Cookie，手动管理
response1 = requests.post("/api/login", json={...})
token = response1.json()["token"]
response2 = requests.get("/api/users", headers={"token": token})  # 手动带token

# ✅ 用Session：自动管理Cookie和连接池
session = requests.Session()
response1 = session.post("/api/login", json={...})  # 登录后Cookie自动保存
response2 = session.get("/api/users")                 # 后续请求自动带上Cookie
```

|  | 不用 Session | 用 Session |
|--|-------------|------------|
| Cookie管理 | 手动从response取，手动放到request | 自动维护 |
| 连接复用 | 每次新建TCP连接 | 连接池复用（性能更好） |
| 适用场景 | 单次请求 | 需要登录态的接口测试 |

### 五、接口关联（上一个接口的响应作为下一个接口的参数）

```python
import jsonpath
import yaml

# ===== 方案1：直接变量传递 =====
def test_login_and_query():
    # 第一步：登录
    login_resp = requests.post("/api/login", json={"user": "admin", "pwd": "123"})
    token = login_resp.json()["data"]["token"]    # 提取token
    
    # 第二步：用token查询用户信息
    user_resp = requests.get("/api/users/1", headers={"token": token})
    assert user_resp.json()["code"] == 200

# ===== 方案2：YAML提取（项目中的做法）=====
# extract.yaml 存储：{token: "abc123", user_id: 1001}

def extract_data(response, extract_dict):
    """从响应中提取数据，写入extract.yaml供后续使用"""
    if not extract_dict:
        return
    extract_data = {}
    for key, json_path in extract_dict.items():
        # jsonpath提取：$.data.token
        value = jsonpath.jsonpath(response, json_path)
        extract_data[key] = value[0]
    
    # 写入extract.yaml
    with open("extract.yaml", "a") as f:
        yaml.dump(extract_data, f)

# YAML中引用提取的数据
# token: ${get_extract_data(token)}
```

### 六、面试高频问题

**Q1：requests中json和data参数的区别？**
> json参数会自动序列化为JSON并设置Content-Type为application/json；data参数发送表单数据，Content-Type为application/x-www-form-urlencoded。接口测试主要用json参数。

**Q2：为什么要用Session？**
> Session自动管理Cookie（登录后的sessionId自动在后续请求中携带），而且底层使用连接池复用TCP连接，性能比每次新建连接好。

**Q3：接口自动化中怎么做数据关联？**
> 第一步：从上一个接口的响应中提取关键数据（token、id等），用jsonpath提取后存到YAML文件或全局变量；第二步：在后续接口的请求参数中通过${get_extract_data(key)}引用这些数据。

---

## 6.3 Allure 测试报告

### 一、Allure 是什么？

Allure 是一个**灵活的、美观的**测试报告框架，可以生成HTML格式的测试报告，展示测试步骤、附件、分类等信息。

```bash
# 安装
pip install allure-pytest

# 1. 运行测试并生成原始数据
pytest --alluredir=./report/temp --clean-alluredir

# 2. 生成并打开HTML报告
allure serve ./report/temp

# 或者生成静态报告
allure generate ./report/temp -o ./report/html --clean
allure open ./report/html
```

### 二、项目中的 run.py 执行入口

```python
import pytest
import shutil
import os

if __name__ == '__main__':
    # 1. 运行pytest，生成Allure原始数据
    pytest.main([
        '-s', '-v',
        '--alluredir=./report/temp',       # Allure原始数据目录
        '--clean-alluredir',                # 每次运行前清空
        './testcase',                       # 指定测试目录
        '--junitxml=./report/results.xml',  # 同时生成JUnit XML（给Jenkins用）
        '-p', 'no:warnings',
    ])
    
    # 2. 复制环境信息到报告目录
    shutil.copy('./environment.xml', './report/temp')
    
    # 3. 自动打开Allure报告
    os.system('allure serve ./report/temp')
```

### 三、Allure 装饰器（在测试代码中使用）

```python
import allure

# 1. @allure.feature —— 测试模块（大分类）
@allure.feature("用户管理模块")
class TestUserManage:

    # 2. @allure.story —— 测试场景（小分类）
    @allure.story("添加用户")
    @pytest.mark.parametrize("base_info, testcase", get_testcase_yaml("addUser.yaml"))
    def test_add_user(self, base_info, testcase):
        # 3. 动态设置测试用例标题
        allure.dynamic.title(testcase["case_name"])
        
        # 4. 添加描述信息
        allure.description("测试添加用户接口的各种场景")
        
        # 5. 添加附件（请求/响应数据）
        allure.attach(
            json.dumps(testcase["data"], ensure_ascii=False),
            name="请求参数",
            attachment_type=allure.attachment_type.JSON
        )
        
        # 执行测试
        result = RequestBase().specification_yaml(base_info, testcase)
        
        # 6. 添加步骤
        with allure.step("发送请求并验证响应"):
            assert result is not None
        
        with allure.step("验证数据库"):
            db_result = db.query("SELECT * FROM users WHERE name='test'")
            assert len(db_result) > 0
```

### 四、Allure 报告展示层级

```
Allure 报告结构：
├── Feature（模块）        ← @allure.feature("用户管理")
│   ├── Story（场景）      ← @allure.story("添加用户")
│   │   ├── 用例1          ← allure.dynamic.title("正常添加")
│   │   │   ├── Step 1     ← with allure.step("发送请求")
│   │   │   ├── Step 2     ← with allure.step("验证响应")
│   │   │   └── 附件       ← allure.attach(...)
│   │   ├── 用例2
│   │   └── 用例3
│   └── Story（另一个场景）
└── Feature（另一个模块）
```

### 五、environment.xml —— 报告环境信息

```xml
<environment>
    <parameter>
        <key>Browser</key>
        <value>Chrome</value>
    </parameter>
    <parameter>
        <key>Python</key>
        <value>3.10</value>
    </parameter>
    <parameter>
        <key>BaseUrl</key>
        <value>http://127.0.0.1:8787</value>
    </parameter>
    <parameter>
        <key>Environment</key>
        <value>测试环境</value>
    </parameter>
</environment>
```

### 六、Allure 报告中的关键信息

| 报告区域 | 展示内容 | 用到的装饰器 |
|----------|----------|-------------|
| 概览 | 通过/失败/跳过/总数、耗时图表 | 自动统计 |
| Suites | 按模块和场景分层的用例列表 | @feature + @story |
| 用例详情 | 请求参数、响应结果、断言结果 | @attach + @step |
| 环境 | 测试环境配置信息 | environment.xml |
| 趋势图 | 历次运行的通过率趋势 | 自动生成（需保留历史数据） |

### 七、面试高频问题

**Q1：Allure报告怎么生成的？**
> 两步走：pytest运行时用--alluredir生成JSON格式的原始数据，然后用allure serve或allure generate命令将原始数据渲染成HTML报告。报告中展示测试步骤、附件、通过率等。

**Q2：Allure的装饰器怎么用？**
> @allure.feature标记测试模块，@allure.story标记测试场景，allure.dynamic.title动态设置用例名，allure.attach添加请求/响应附件，with allure.step添加测试步骤。层次是feature > story > 用例 > step。

**Q3：如何在Jenkins中集成Allure？**
> 安装Jenkins的Allure插件，Pipeline中用allure includeProperties: false, jdk: '', results: [[path: 'report/temp']]生成报告。Jenkins每次构建后会自动在构建页面展示Allure报告链接。

---

## 6.4 YAML 驱动测试（数据驱动）

### 一、为什么用 YAML 驱动测试？

传统方式把测试数据写在Python代码里，改一个参数就要改代码。YAML驱动把**测试数据从代码中分离出来**：

|  | 传统方式 | YAML驱动 |
|--|---------|----------|
| 数据位置 | 写死在Python代码里 | 独立的.yaml文件 |
| 修改方式 | 改代码→重新部署 | 改YAML→直接运行 |
| 维护成本 | 高（需要懂代码） | 低（非技术人员也能维护） |
| 可读性 | 一般 | 高（结构清晰） |

### 二、YAML 基本语法

```yaml
# YAML 语法要点

# 1. 键值对
name: 张三
age: 25

# 2. 列表（用 - 开头）
fruits:
  - apple
  - banana
  - orange

# 3. 嵌套对象
user:
  name: 张三
  address:
    city: 武汉
    street: 珞狮路

# 4. 引用变量 & 锚点
default_config: &default
  timeout: 30
  retry: 3

api_config:
  <<: *default          # 引用default的值
  host: localhost
```

```python
# Python 操作 YAML
import yaml

# 读取
with open("test.yaml", "r", encoding="utf-8") as f:
    data = yaml.safe_load(f)    # safe_load安全加载，防止代码注入

# 写入
with open("output.yaml", "w") as f:
    yaml.dump(data, f, allow_unicode=True)
```

### 三、项目中 YAML 测试用例的完整结构

```yaml
# addUser.yaml —— 添加用户接口的测试用例

- baseInfo:                             # 接口基本信息（所有testCase共享）
    api_name: 添加用户
    url: /api/user/add                  # 接口路径（host在config.ini中配置）
    method: post                        # 请求方法
    header:                             # 请求头
      Content-Type: application/json;charset=UTF-8
      token: ${get_extract_data(token)} # 动态引用：从extract.yaml取token
      
  testCase:                             # 测试场景列表（可以有多个）
    - case_name: 正常添加用户            # 场景1：正常场景
      json:                             # 请求参数（JSON格式）
        login_name: test_${timestamp()} # 动态生成用户名（时间戳）
        password: ${md5_encryption(123456)}  # MD5加密密码
        email: test@example.com
      validation:                       # 断言规则
        - contains: {'msg': '操作成功'}
        - eq: {'status_code': 200}
      extract:                          # 提取数据
        user_id: $.data.id              # JSONPath提取新用户ID
        
    - case_name: 重复用户名添加          # 场景2：异常场景
      json:
        login_name: admin               # 已存在的用户名
        password: 123456
        email: admin@example.com
      validation:
        - contains: {'msg': '用户名已存在'}
```

### 四、YAML 中的动态参数替换

```python
import re
import yaml

def replace_load(data):
    """替换YAML中的 ${function()} 动态参数"""
    if isinstance(data, dict):
        for key, value in data.items():
            data[key] = replace_load(value)         # 递归处理字典
    elif isinstance(data, list):
        for i, item in enumerate(data):
            data[i] = replace_load(item)             # 递归处理列表
    elif isinstance(data, str):
        # 匹配 ${function(args)} 模式
        pattern = r'\$\{(.*?)\((.*?)\)\}'
        matches = re.findall(pattern, data)
        for func_name, args in matches:
            # 动态调用debugtalk.py中的函数
            func = getattr(debugtalk, func_name)
            result = func(args) if args else func()
            data = data.replace(f'${{{func_name}({args})}}', str(result))
    return data
```

**debugtalk.py 中定义的动态函数：**

```python
# common/debugtalk.py —— YAML可调用的工具函数

import time
import hashlib

def timestamp():
    """10位时间戳"""
    return str(int(time.time()))

def timestamp_thirteen():
    """13位时间戳（毫秒）"""
    return str(int(time.time() * 1000))

def md5_encryption(text):
    """MD5加密"""
    return hashlib.md5(text.encode()).hexdigest()

def get_extract_data(key, index=0):
    """从extract.yaml中获取数据"""
    with open("extract.yaml", "r") as f:
        data = yaml.safe_load(f)
    if index == 0:
        return data.get(key)            # 返回单个值
    elif index == -1:
        return str(data.get(key))       # 转字符串
    elif index == -2:
        return data.get(key)            # 返回列表
```

### 五、断言框架（Assertions）

```python
# common/assertions.py —— 5种断言类型

class Assertions:
    
    def assert_result(self, response_data, validation_list):
        """统一断言入口"""
        for validation in validation_list:
            if "contains" in validation:
                # 1. 包含断言：响应文本包含指定字符串
                expected = validation["contains"]
                for key, value in expected.items():
                    assert str(value) in str(response_data), \
                        f"断言失败：响应中不包含 {value}"
            
            elif "eq" in validation:
                # 2. 相等断言：JSON中某个字段等于期望值
                expected = validation["eq"]
                for key, value in expected.items():
                    actual = jsonpath.jsonpath(response_data, f"$.{key}")[0]
                    assert actual == value, \
                        f"断言失败：{key} 期望{value}，实际{actual}"
            
            elif "ne" in validation:
                # 3. 不等断言
                expected = validation["ne"]
                for key, value in expected.items():
                    actual = jsonpath.jsonpath(response_data, f"$.{key}")[0]
                    assert actual != value
            
            elif "rv" in validation:
                # 4. 响应值断言（任意层级字段）
                expected = validation["rv"]
                for key, value in expected.items():
                    actual = jsonpath.jsonpath(response_data, f"$.{key}")[0]
                    assert actual == value
            
            elif "db" in validation:
                # 5. 数据库断言：执行SQL并验证
                sql = validation["db"]
                db_result = ConnectMysql().query_all(sql)
                assert len(db_result) > 0, f"数据库查询无结果：{sql}"
```

**YAML中的断言写法：**

```yaml
validation:
  - contains: {'msg': '操作成功'}        # 响应包含"操作成功"
  - eq: {'error_code': '0000'}          # error_code等于0000
  - ne: {'status': 'deleted'}           # status不等于deleted
  - rv: {'data.name': '张三'}            # data.name等于张三
  - db: SELECT * FROM users WHERE name='张三'  # 数据库能查到记录
```

### 六、完整执行流程

```
run.py 启动
    │
    ↓
pytest 发现 test_*.py 文件
    │
    ↓
conftest.py 执行 session 级 fixture
    ├── 清空 extract.yaml
    └── 自动登录（获取token存入extract.yaml）
    │
    ↓
读取 YAML 测试用例文件
    ├── 解析 baseInfo（接口信息）
    └── 解析 testCase（测试场景）
    │
    ↓
替换动态参数 ${function()}
    ├── ${get_extract_data(token)} → 从extract.yaml取值
    ├── ${timestamp()} → 当前时间戳
    └── ${md5_encryption(123456)} → 加密后的密码
    │
    ↓
发送 HTTP 请求（SendRequest）
    │
    ↓
提取响应数据（extract）
    └── 存入 extract.yaml 供后续用例使用
    │
    ↓
执行断言（Assertions）
    ├── contains / eq / ne / rv / db
    │
    ↓
记录 Allure 报告
    ├── @feature / @story / @step
    └── allure.attach（请求参数 + 响应结果）
    │
    ↓
生成 Allure HTML 报告 + 发送通知
```

### 七、面试高频问题

**Q1：什么是数据驱动测试？**
> 测试数据和测试逻辑分离。测试数据存放在YAML/CSV/Excel中，测试代码读取数据后执行，添加新的测试场景只需要添加一条数据，不需要改代码。好处是维护成本低、非技术人员也能维护用例。

**Q2：YAML测试用例的结构是怎样的？**
> 分为baseInfo（接口基本信息：URL、method、header）和testCase（测试场景列表，包含case_name、请求参数、validation断言、extract提取）。baseInfo所有场景共享，每个testCase是一个独立的测试场景。

**Q3：YAML中的动态参数怎么实现？**
> 用 ${function()} 语法，在读取YAML后通过正则匹配提取函数名和参数，动态调用debugtalk.py中的函数获取实际值（时间戳、加密结果、提取的数据等），替换后再发送请求。

---

## 6.5 功能测试方法

### 一、黑盒测试概述

**黑盒测试：** 不关注代码内部实现，只关注输入和输出——从用户角度验证功能是否正确。

| 方法 | 关注点 | 适用场景 |
|------|--------|----------|
| 等价类划分 | 将输入分为有效/无效等价类 | 表单输入、参数验证 |
| 边界值分析 | 测试边界上的值 | 数值范围、字符串长度 |
| 判定表/因果图 | 多条件组合 | 逻辑复杂的业务 |
| 错误推测 | 凭经验猜测容易出错的地方 | 补充测试 |
| 正交实验 | 减少多因素组合数 | 配置项多的情况 |

### 二、等价类划分（面试必考）

**核心思想：** 把所有可能的输入划分成若干"等价类"，每个类中选一个代表值测试——如果这个值对了，整个类都认为是对的。

#### 例：用户注册页面——用户名输入框

| 规则 | 有效等价类 | 无效等价类 |
|------|-----------|-----------|
| 长度 | 6~20个字符 | <6个字符；>20个字符 |
| 字符类型 | 字母+数字 | 特殊字符(@#$)；纯空格；中文 |
| 首字符 | 字母开头 | 数字开头；特殊字符开头 |
| 唯一性 | 不存在的用户名 | 已存在的用户名 |
| 空值 | 非空 | 空（不输入） |

```
有效测试用例：zhangsan123（6-20位字母数字，字母开头）→ 应该注册成功
无效测试用例：
  - abc（少于6位）→ 应提示"用户名至少6位"
  - abcdefghijklmnopqrst12345（超过20位）→ 应提示"用户名最多20位"
  - 123abc（数字开头）→ 应提示"用户名必须字母开头"
  - abc@123（含特殊字符）→ 应提示"用户名只能包含字母和数字"
  - admin（已存在）→ 应提示"用户名已存在"
  - （空）→ 应提示"请输入用户名"
```

> **面试一句话：** "等价类划分是把输入分为有效等价类和无效等价类，每类选一个代表值测试。有效等价类验证正常流程，无效等价类验证异常处理。"

### 三、边界值分析（面试必考）

**核心思想：** 大量bug出现在边界上，所以要重点测试边界值。

#### 规则：找边界 → 测试边界及两侧

| 边界 | 低于边界 | 边界值 | 高于边界 |
|------|---------|--------|---------|
| 长度6~20 | 5（不通过） | 6（通过） | 7（通过） |
| | 19（通过） | 20（通过） | 21（不通过） |
| 年龄18~65 | 17（不通过） | 18（通过） | 19（通过） |
| | 64（通过） | 65（通过） | 66（不通过） |

#### 例：订单金额 1~99999 元

```
边界值测试用例：
  - 0.99元  → 无效（低于最小值）
  - 1元     → 有效（最小边界）
  - 1.01元  → 有效
  - 99998元 → 有效
  - 99999元 → 有效（最大边界）
  - 100000元 → 无效（超过最大值）
```

> **面试一句话：** "边界值分析是测试边界及两侧的值。规则是：如果范围是[a,b]，就测试a-1、a、a+1、b-1、b、b+1。因为大部分bug出现在边界上。"

### 四、等价类 + 边界值 结合使用（面试常考综合题）

#### 例：密码输入框（8~16位，必须包含字母和数字）

```
等价类划分：
  有效：8~16位，含字母和数字     → "abc12345"
  无效：少于8位                  → "ab12"
  无效：多于16位                 → "abcdefghijklmnopq1234567890"
  无效：只有字母没有数字          → "abcdefgh"
  无效：只有数字没有字母          → "12345678"
  无效：含特殊字符               → "abc@1234"
  无效：空                       → ""

边界值（在有效等价类的基础上）：
  长度=7   → 无效（abc1234）
  长度=8   → 有效（abc12345）
  长度=9   → 有效（abc123456）
  长度=15  → 有效（abcdefghijklmn1）
  长度=16  → 有效（abcdefghijklmno1）
  长度=17  → 无效（abcdefghijklmnopq1）
```

### 五、判定表（多条件组合）

当多个条件互相影响时，用判定表穷举所有组合。

#### 例：电商优惠券使用条件

| 条件 | 规则1 | 规则2 | 规则3 | 规则4 | 规则5 |
|------|-------|-------|-------|-------|-------|
| 订单金额 ≥ 100 | Y | Y | Y | N | N |
| 会员等级 ≥ 金牌 | Y | Y | N | Y | N |
| 优惠券未过期 | Y | N | Y | Y | N |
| **能否使用** | ✅ | ❌ | ❌ | ❌ | ❌ |

### 六、测试用例的完整写法

```yaml
# 一个完整测试用例的要素
test_case:
  id: TC_USER_001
  title: 正常添加用户
  priority: P1                    # 优先级
  precondition: 已登录管理员账号    # 前置条件
  steps:                          # 测试步骤
    - step: 进入用户管理页面
    - step: 点击"添加用户"按钮
    - step: 输入用户名test001，密码123456，邮箱test@mail.com
    - step: 点击"提交"按钮
  expected:                       # 预期结果
    - 页面提示"添加成功"
    - 用户列表中出现test001
    - 数据库中新增一条用户记录
```

### 七、面试高频问题

**Q1：等价类划分和边界值分析的区别？**
> 等价类划分是从大量数据中选出代表性数据（每类选一个），减少测试数量；边界值分析是专门测试边界上的值（a-1、a、a+1），因为边界最容易出错。实际中两者结合使用。

**Q2：给你一个登录页面，怎么设计测试用例？**
> 先用等价类划分（用户名/密码各分有效和无效等价类），再用边界值分析（用户名长度边界），然后考虑异常场景（空值、SQL注入、XSS）、安全场景（暴力破解、session过期）、兼容性（不同浏览器）。

**Q3：什么是P0/P1/P2优先级？**
> P0：冒烟测试级别的核心功能（比如登录、下单）；P1：主要功能路径；P2：次要功能和异常场景；P3：边界和极端场景。优先级越高越早测试。

---

## 6.6 日志与 Jenkins CI

### 一、日志记录（logging）

#### 1. 为什么需要日志？

- 测试失败时，日志是**定位问题的第一手证据**
- 记录请求参数、响应结果、断言结果
- 自动化测试无人值守运行，日志是唯一的排查手段

#### 2. Python logging 模块

```python
import logging
from logging.handlers import RotatingFileHandler

def setup_logger():
    """配置日志"""
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # 格式：时间 - 级别 - 文件:行号 - [模块:函数] - 消息
    fmt = logging.Formatter(
        '%(levelname)s - %(asctime)s - %(filename)s:%(lineno)d - '
        '[%(module)s:%(funcName)s] - %(message)s'
    )
    
    # 文件输出（自动轮转：每个文件5MB，保留7个备份，保留30天）
    file_handler = RotatingFileHandler(
        "logs/test.log",
        maxBytes=5*1024*1024,    # 5MB
        backupCount=7,
        encoding="utf-8"
    )
    file_handler.setFormatter(fmt)
    
    # 控制台输出
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(fmt)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger
```

#### 3. 日志级别

| 级别 | 数值 | 使用场景 |
|------|------|----------|
| DEBUG | 10 | 调试信息（请求参数、响应体） |
| INFO | 20 | 正常流程信息（测试开始/结束） |
| WARNING | 30 | 警告（接口响应慢、数据异常） |
| ERROR | 40 | 错误（断言失败、请求异常） |
| CRITICAL | 50 | 严重错误（服务不可用） |

#### 4. 项目中的日志使用

```python
# common/recordlog.py
logger = setup_logger()

# 在请求封装中使用
class SendRequest:
    def run_main(self, method, url, data, **kwargs):
        logger.info(f"发送请求：{method} {url}")
        logger.debug(f"请求参数：{json.dumps(data, ensure_ascii=False)}")
        
        try:
            response = self.session.request(method, url, json=data, **kwargs)
            logger.info(f"响应状态码：{response.status_code}")
            logger.debug(f"响应内容：{response.text}")
            return response
        except Exception as e:
            logger.error(f"请求异常：{e}")
            raise
```

### 二、Jenkins CI 持续集成

#### 1. 为什么需要 Jenkins？

| 没有Jenkins | 有Jenkins |
|------------|-----------|
| 手动运行测试脚本 | 定时/触发自动运行 |
| 本地跑，结果只有自己看 | 服务器跑，团队都能看报告 |
| 没有历史趋势 | 历次构建结果对比 |
| 失败了没人知道 | 失败自动发通知（钉钉/邮件） |

#### 2. Jenkins Pipeline 配置

```groovy
// Jenkinsfile
pipeline {
    agent any
    
    tools {
        python 'Python3.10'
    }
    
    triggers {
        cron('0 2 * * *')          // 每天凌晨2点自动运行
        // pollSCM('H/5 * * * *')  // 或者：代码提交后自动运行
    }
    
    stages {
        stage('拉取代码') {
            steps {
                git branch: 'main', url: 'https://github.com/xxx/api-test.git'
            }
        }
        
        stage('安装依赖') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }
        
        stage('执行测试') {
            steps {
                sh 'python run.py'
            }
        }
        
        stage('生成Allure报告') {
            steps {
                allure includeProperties: false,
                       jdk: '',
                       results: [[path: 'report/temp']]
            }
        }
    }
    
    post {
        always {
            // 不管成功失败都发钉钉通知
            dingtalk(
                robot: '测试机器人',
                type: 'TEXT',
                text: ["测试完成：${currentBuild.result}，详情：${env.BUILD_URL}"]
            )
        }
        failure {
            mail to: 'team@example.com',
                 subject: "测试失败：${env.JOB_NAME} #${env.BUILD_NUMBER}",
                 body: "测试失败了，请查看：${env.BUILD_URL}allure"
        }
    }
}
```

#### 3. Jenkins + Allure + 钉钉 完整流程

```
代码提交到Git
    │
    ↓
Jenkins 自动触发构建（或定时触发）
    │
    ↓
┌─────────────────────────┐
│ Stage 1: 拉取最新代码     │
│ Stage 2: 安装依赖         │
│ Stage 3: 执行pytest测试   │
│   ├── 生成 Allure 数据    │
│   └── 生成 JUnit XML      │
│ Stage 4: 生成 Allure 报告  │
└─────────────────────────┘
    │
    ↓
post 阶段：发送通知
    ├── 钉钉机器人：发送测试摘要
    └── 邮件：失败时发送告警
    │
    ↓
团队成员查看 Allure 报告
    ├── 通过率、失败用例
    ├── 请求参数、响应结果
    └── 历史趋势对比
```

#### 4. 钉钉通知集成

```python
# common/dingRobot.py
import requests
import time

def send_dd_msg(summary):
    """发送钉钉机器人通知"""
    webhook = "https://oapi.dingtalk.com/robot/send?access_token=xxx"
    
    data = {
        "msgtype": "text",
        "text": {
            "content": f"""
【自动化测试报告】
项目：智测星图
时间：{time.strftime('%Y-%m-%d %H:%M:%S')}
{summary}
详情请查看Jenkins: http://jenkins.example.com/job/api-test/
"""
        }
    }
    requests.post(webhook, json=data)
```

### 三、面试高频问题

**Q1：自动化测试中的日志怎么设计？**
> 使用Python的logging模块，配置RotatingFileHandler实现日志轮转（防止单个文件过大）。双输出：文件+控制台。在请求发送前后记录URL、参数、响应、耗时。日志级别：DEBUG记录详细信息，INFO记录流程，ERROR记录异常。

**Q2：Jenkins在自动化测试中的作用？**
> 实现持续集成：定时或代码提交触发自动运行测试，生成Allure报告，失败时自动发钉钉/邮件通知。这样测试不需要人工干预，团队随时查看最新测试结果和历史趋势。

**Q3：pytest怎么生成JUnit XML？**
> pytest运行时加--junitxml=./report/results.xml参数，生成JUnit格式的XML报告。Jenkins可以直接解析这个文件展示测试结果，和Allure报告互补。

---

# 模块三：AI / Agent / RAG

> 简历项目一「Agent智能客服」涉及的全部技术栈
> 核心架构：LangGraph多智能体 + GraphRAG知识检索 + Neo4j图数据库 + FAISS语义缓存

## 3.1 大语言模型（LLM）基础

### 一、什么是大语言模型？

大语言模型（Large Language Model, LLM）是基于Transformer架构的深度学习模型，通过海量文本数据训练，能够理解和生成自然语言。

```
训练数据（互联网文本、书籍、代码等）
        ↓
  Transformer 架构（自注意力机制）
        ↓
  学会"预测下一个token"的能力
        ↓
  能对话、写代码、回答问题、推理
```

### 二、常见LLM对比

| 模型 | 厂商 | 特点 | 项目中使用方式 |
|------|------|------|---------------|
| DeepSeek-V3 | 深度求索 | 性价比高，中文能力强 | 主要对话模型（deepseek-chat） |
| DeepSeek-R1 | 深度求索 | 推理能力强（CoT链式思考） | 深度推理（deepseek-r1:32b） |
| Qwen2.5 | 阿里 | 开源可本地部署 | 本地Ollama运行（qwen2.5:32b） |
| GPT-4o | OpenAI | 多模态（文本+图像） | 图像理解（vision模型） |
| BGE-M3 | BAAI | 文本向量化模型 | Embedding语义向量 |

### 三、LLM 的两种使用模式

#### 1. API调用（云端模型）

```python
from openai import AsyncOpenAI

# DeepSeek API
client = AsyncOpenAI(
    api_key="sk-xxx",
    base_url="https://api.deepseek.com"
)

# 同步调用
response = await client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "你是一个客服助手"},
        {"role": "user", "content": "iPhone 15多少钱？"}
    ],
    stream=False  # 一次性返回完整响应
)

# 流式调用（SSE，逐字输出）
stream = await client.chat.completions.create(
    model="deepseek-chat",
    messages=[...],
    stream=True  # 逐token返回
)

async for chunk in stream:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="")  # 实时输出
```

#### 2. 本地部署（Ollama）

```bash
# 安装Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 拉取模型
ollama pull qwen2.5:32b
ollama pull deepseek-r1:32b
ollama pull bge-m3

# 运行
ollama run qwen2.5:32b
```

```python
# Python调用Ollama
import aiohttp, json

async def call_ollama(messages, model="qwen2.5:32b"):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:11434/api/chat",
            json={"model": model, "messages": messages, "stream": True}
        ) as resp:
            async for line in resp.content:
                chunk = json.loads(line)
                if "message" in chunk:
                    yield chunk["message"]["content"]
```

|  | API调用 | 本地部署(Ollama) |
|--|---------|-----------------|
| 成本 | 按token收费 | 免费（需GPU硬件） |
| 数据安全 | 数据发到云端 | 数据不出本地 |
| 延迟 | 网络延迟 | 本地推理延迟 |
| 模型大小 | 不限 | 受限于显存 |

### 四、项目中的LLM工厂模式

```python
# llm_factory.py —— 工厂模式切换LLM

class LLMFactory:
    @staticmethod
    def create_chat_service():
        if settings.CHAT_SERVICE == "deepseek":
            return DeepseekService()       # 调用DeepSeek API
        else:
            return OllamaService()         # 调用本地Ollama

    @staticmethod
    def create_embedding_service():
        return EmbeddingService()           # BGE-M3 向量化

# 使用
chat_service = LLMFactory.create_chat_service()
async for chunk in chat_service.generate_stream(messages):
    yield chunk
```

> **面试一句话：** "项目通过工厂模式实现LLM的灵活切换。DeepSeek用于主对话和Agent推理，Ollama用于本地推理和向量化，GPT-4o用于图像理解。.env配置文件控制使用哪个服务。"

### 五、Structured Output（结构化输出）

让LLM返回**指定格式**的数据（而非自由文本），是意图识别的关键技术：

```python
from langchain_deepseek import ChatDeepSeek
from typing import Literal, TypedDict

class Router(TypedDict):
    """意图分类结果——强制LLM返回这个结构"""
    logic: str                    # 分类的推理过程
    type: Literal[                # 只能返回这5种之一
        "general-query",          # 闲聊
        "additional-query",       # 需要追问
        "graphrag-query",         # 知识库查询
        "image-query",            # 图片处理
        "file-query"              # 文件处理
    ]

# 使用
model = ChatDeepSeek(model="deepseek-chat")
structured_model = model.with_structured_output(Router)

result = await structured_model.ainvoke([
    {"role": "system", "content": "你是客服，分类用户问题"},
    {"role": "user", "content": "iPhone 15 Pro多少钱？"}
])
# result = {"logic": "用户询问产品价格，需要查知识库", "type": "graphrag-query"}
```

### 六、面试高频问题

**Q1：什么是LLM？**
> 大语言模型是基于Transformer架构的AI模型，通过海量文本训练学会"预测下一个token"。它能理解自然语言并生成回复，广泛应用于对话、代码生成、推理等场景。

**Q2：为什么要用Structured Output？**
> LLM默认返回自由文本，不利于程序处理。Structured Output通过约束解码或JSON Schema，强制LLM返回预定义的数据结构（如Router的type字段），让程序能根据分类结果做路由决策。

**Q3：流式输出(SSE)是什么？为什么用？**
> Server-Sent Events，服务端逐token推送响应给前端。LLM生成速度慢，如果等全部生成完再返回，用户要等很久。流式输出让用户逐字看到回复，体验更好。

---

## 3.2 RAG 与 GraphRAG

### 一、为什么需要 RAG？

LLM 有两个致命问题：
1. **知识截止：** 训练数据有时效性（不知道最新的产品价格）
2. **幻觉：** 会编造不存在的答案

**RAG（Retrieval Augmented Generation，检索增强生成）** 的思路：先从知识库检索相关信息，再把检索结果作为上下文喂给LLM，让LLM基于真实数据回答。

```
传统LLM：
  用户问题 → LLM → 回答（可能是编的）

RAG：
  用户问题 → 检索知识库 → 找到相关文档 → [问题+文档]一起给LLM → 回答（有据可依）
```

### 二、传统 RAG 流程

```
┌─────────────── 离线阶段（建索引）──────────────────┐
│                                                    │
│  文档 ─→ 分块(Chunking) ─→ Embedding向量化         │
│                                  ↓                 │
│                         存入向量数据库(FAISS)       │
└────────────────────────────────────────────────────┘

┌─────────────── 在线阶段（查询）────────────────────┐
│                                                    │
│  用户问题                                          │
│      ↓                                             │
│  问题 Embedding（和文档用同一个向量模型）            │
│      ↓                                             │
│  向量相似度检索（FAISS Top-K）                      │
│      ↓                                             │
│  取出最相关的K个文档块                              │
│      ↓                                             │
│  构建 Prompt：[问题 + 检索到的文档]                  │
│      ↓                                             │
│  LLM 基于文档生成回答                               │
└────────────────────────────────────────────────────┘
```

```python
# 传统RAG的简单实现
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS

# 1. 文档分块
from langchain.text_splitter import RecursiveCharacterTextSplitter
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(documents)

# 2. 向量化并建索引
embeddings = OllamaEmbeddings(model="bge-m3")
vectorstore = FAISS.from_documents(chunks, embeddings)

# 3. 检索 + 生成
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
relevant_docs = retriever.invoke("iPhone 15多少钱？")

# 4. 构建prompt给LLM
prompt = f"""基于以下文档回答问题：
{relevant_docs}

问题：iPhone 15多少钱？
"""
response = llm.invoke(prompt)
```

### 三、传统 RAG 的局限

| 问题 | 说明 |
|------|------|
| **碎片化** | 文档切块后丢失了全局信息，无法回答跨文档的汇总问题 |
| **无关联** | 不知道实体之间的关系（如"某个供应商的所有产品"） |
| **全局查询差** | "总结所有用户评价的趋势"这类问题需要看所有数据，Top-K不够 |

### 四、GraphRAG（图检索增强生成）

**GraphRAG** 是微软提出的方案——先从文档中**抽取知识图谱**（实体+关系），再利用图谱的结构化信息进行检索。

#### GraphRAG 的两阶段流程

```
┌─────────────── 索引阶段 ──────────────────────┐
│                                                │
│  原始文档                                      │
│      ↓                                         │
│  LLM 抽取实体和关系                             │
│      ↓                                         │
│  构建知识图谱（实体为节点，关系为边）             │
│      ↓                                         │
│  社区检测（Louvain算法，把图分成社区）           │
│      ↓                                         │
│  LLM 生成社区摘要（每个社区的总结）              │
│      ↓                                         │
│  存储：图数据 + 社区报告 + 实体/关系表           │
└────────────────────────────────────────────────┘

┌─────────────── 查询阶段 ──────────────────────┐
│                                                │
│  两种查询模式：                                 │
│                                                │
│  【Local Search（局部搜索）】                    │
│  问题 → 提取关键词 → 匹配相关实体               │
│      → 获取实体的邻居子图 + 相关文本块           │
│      → LLM 基于子图信息生成回答                  │
│  适合：具体问题（"iPhone 15的价格？"）           │
│                                                │
│  【Global Search（全局搜索）】                   │
│  问题 → 遍历所有社区摘要                        │
│      → Map-Reduce：并行总结每个社区               │
│      → 汇总所有社区回答生成最终答案               │
│  适合：总结性问题（"所有产品的用户评价趋势？"）   │
└────────────────────────────────────────────────┘
```

#### 项目中 GraphRAG 的实现

```python
# graphrag_query.py —— GraphRAG查询接口

from graphrag.api import local_search, global_search

class GraphRAGAPI:
    def __init__(self):
        self.project_dir = settings.GRAPHRAG_PROJECT_DIR
        self.query_type = settings.GRAPHRAG_QUERY_TYPE  # local/global
    
    async def initialize(self):
        """加载GraphRAG索引数据"""
        # 加载配置
        self.config = load_config(Path(self.project_dir))
        
        # 加载各类数据表
        self.entities = await load_table("entities")         # 实体表
        self.communities = await load_table("communities")   # 社区表
        self.community_reports = await load_table("community_reports")  # 社区报告
        self.relationships = await load_table("relationships")  # 关系表
        self.text_units = await load_table("text_units")     # 文本块表
    
    async def query(self, question: str) -> str:
        """执行GraphRAG查询"""
        if self.query_type == "local":
            # 局部搜索：找相关实体的子图
            response, context = await local_search(
                config=self.config,
                entities=self.entities,
                communities=self.communities,
                community_reports=self.community_reports,
                text_units=self.text_units,
                relationships=self.relationships,
                community_level=3,              # 社区层级（越高越概括）
                response_type="text",
                query=question
            )
        elif self.query_type == "global":
            # 全局搜索：Map-Reduce社区摘要
            response, context = await global_search(
                config=self.config,
                communities=self.communities,
                community_reports=self.community_reports,
                community_level=3,
                query=question
            )
        
        return response
```

### 五、RAG vs GraphRAG 对比（面试重点）

|  | 传统 RAG | GraphRAG |
|--|---------|----------|
| 数据结构 | 文本块(Chunk) | 知识图谱(实体+关系+社区) |
| 索引方式 | 向量索引(FAISS) | 图索引 + 向量索引 |
| 检索方式 | 语义相似度Top-K | 实体匹配 + 子图遍历 |
| 擅长 | 具体事实查询 | 关系推理 + 全局总结 |
| 成本 | 低（只需向量化） | 高（需LLM抽取实体关系） |
| 全局理解 | 差（只能看Top-K） | 好（社区摘要覆盖全图） |

> **面试一句话：** "传统RAG通过向量相似度检索文本块，适合具体问题；GraphRAG先构建知识图谱再检索，通过社区摘要实现全局理解，适合关系推理和总结性问题。项目中两者结合使用。"

### 六、面试高频问题

**Q1：什么是RAG？**
> 检索增强生成。先从知识库检索相关文档，再把文档和问题一起喂给LLM生成回答。解决了LLM的知识截止和幻觉问题。

**Q2：GraphRAG和传统RAG的区别？**
> 传统RAG用向量检索文本块，只能回答局部问题。GraphRAG先从文档抽取知识图谱（实体+关系），再做社区检测和摘要。查询时可以遍历图谱做关系推理，也可以Map-Reduce社区摘要做全局总结。

**Q3：GraphRAG的Local Search和Global Search的区别？**
> Local Search提取问题中的实体，在图谱中找到相关子图和文本块，适合具体问题。Global Search遍历所有社区摘要做Map-Reduce汇总，适合全局总结类问题。

---

## 3.3 Neo4j 图数据库

### 一、什么是图数据库？

传统关系型数据库（MySQL）用**表格**存储数据，图数据库用**节点(Node)和关系(Relationship)**存储数据。

```
关系型数据库（MySQL）：
┌──────────┐     ┌──────────┐     ┌──────────┐
│ Product  │     │ Category │     │ Supplier │
├──────────┤     ├──────────┤     ├──────────┤
│ id=1     │     │ id=1     │     │ id=1     │
│ name=iPhone│   │ name=手机│     │ name=苹果 │
│ cate_id=1 │     └──────────┘     └──────────┘
│ supp_id=1 │          ↑                ↑
└──────────┘     外键关联            外键关联
                 需要JOIN查询        需要JOIN查询

图数据库（Neo4j）：
(Product: iPhone) ──BELONGS_TO──→ (Category: 手机)
(Product: iPhone) ──SUPPLIED_BY──→ (Supplier: 苹果)
(Customer: 张三) ──PLACED──→ (Order: #001) ──CONTAINS──→ (Product: iPhone)
```

> **面试一句话：** "图数据库用节点和关系直接存储实体间的连接，查询关系型数据不需要JOIN，直接沿边遍历，对多跳查询性能远超关系型数据库。"

### 二、Cypher 查询语言

Neo4j 使用 Cypher 查询语言，语法直观像画图：

```cypher
// 1. 创建节点
CREATE (p:Product {name: 'iPhone 15', price: 7999})
CREATE (c:Category {name: '手机'})

// 2. 创建关系
MATCH (p:Product {name: 'iPhone 15'}), (c:Category {name: '手机'})
CREATE (p)-[:BELONGS_TO]->(c)

// 3. 简单查询：iPhone 15属于哪个分类？
MATCH (p:Product {name: 'iPhone 15'})-[:BELONGS_TO]->(c:Category)
RETURN c.name
// 结果：手机

// 4. 多跳查询：张三买了哪些供应商的产品？
MATCH (cu:Customer {name: '张三'})-[:PLACED]->(o:Order)-[:CONTAINS]->(p:Product)-[:SUPPLIED_BY]->(s:Supplier)
RETURN DISTINCT s.name
// 结果：苹果, 三星

// 5. 聚合查询：每个分类有多少产品？
MATCH (p:Product)-[:BELONGS_TO]->(c:Category)
RETURN c.name, COUNT(p) as product_count
ORDER BY product_count DESC

// 6. 条件查询：价格大于5000的手机
MATCH (p:Product)-[:BELONGS_TO]->(c:Category {name: '手机'})
WHERE p.price > 5000
RETURN p.name, p.price
```

### 三、项目中 Neo4j 的数据模型

```
节点类型：
  (Product)      → ProductID, ProductName, UnitPrice, UnitsInStock, QuantityPerUnit
  (Category)     → CategoryID, CategoryName, Description
  (Supplier)     → SupplierID, CompanyName, ContactName, Phone
  (Customer)     → CustomerID, CompanyName, ContactName
  (Order)        → OrderID, OrderDate
  (Review)       → ReviewID, ReviewText, Rating, ReviewDate

关系类型：
  (Product)──BELONGS_TO──→(Category)        产品属于某分类
  (Product)──SUPPLIED_BY──→(Supplier)       产品由某供应商提供
  (Order)──CONTAINS──→(Product)             订单包含某产品
  (Customer)──PLACED──→(Order)              客户下了某订单
  (Customer)──WROTE──→(Review)              客户写了某评价
  (Review)──ABOUT──→(Product)               评价关于某产品
```

### 四、项目中的连接和使用

```python
# kg_neo4j_conn.py
from langchain_neo4j import Neo4jGraph

def get_neo4j_graph():
    """创建Neo4j图连接"""
    graph = Neo4jGraph(
        url="bolt://localhost:7687",      # Neo4j bolt协议
        username="neo4j",
        password="password",
        database="neo4j"
    )
    return graph

# 使用：执行Cypher查询
graph = get_neo4j_graph()
result = graph.query("MATCH (p:Product) WHERE p.UnitPrice > 5000 RETURN p")
```

### 五、Text2Cypher（自然语言转Cypher）

项目中让LLM把用户问题转成Cypher查询：

```
用户问题：iPhone 15 Pro多少钱？
     ↓ LLM转换
生成Cypher：MATCH (p:Product {ProductName: 'iPhone 15 Pro'}) RETURN p.UnitPrice
     ↓ 执行
查询结果：{UnitPrice: 8999}
     ↓ LLM生成回答
最终回答：iPhone 15 Pro的价格是8999元。
```

### 六、Neo4j vs MySQL（面试常考）

|  | MySQL | Neo4j |
|--|-------|-------|
| 数据模型 | 表格（行+列） | 图（节点+边） |
| 关系查询 | JOIN（多表关联） | 直接遍历边 |
| 多跳查询 | 性能差（N个JOIN） | 性能好（沿边遍历） |
| 适合场景 | 结构化数据、事务处理 | 关系密集型数据、推荐系统 |
| 查询语言 | SQL | Cypher |
| ACID | 支持 | 支持 |

### 七、面试高频问题

**Q1：为什么用Neo4j而不用MySQL存商品关系？**
> 商品、分类、供应商、订单之间是多对多的复杂关系。MySQL查多跳关系需要多次JOIN，性能随跳数指数下降。Neo4j直接沿边遍历，多跳查询性能稳定。比如"张三买了哪些供应商的产品"，Neo4j一次遍历搞定。

**Q2：Cypher的基本语法？**
> MATCH匹配模式，WHERE过滤条件，RETURN返回结果，CREATE创建节点/关系。模式用()表示节点、-[]->表示关系。例如`MATCH (p:Product)-[:BELONGS_TO]->(c:Category) RETURN p, c`。

**Q3：什么是Text2Cypher？**
> 让LLM把自然语言转成Cypher查询。先给LLM展示图数据库的Schema（节点和关系的结构），再让LLM根据用户问题生成对应的Cypher语句，执行后把结果返回给用户。

---

## 3.4 FAISS 向量检索

### 一、什么是向量检索？

**核心思想：** 把文本变成**向量（一串数字）**，语义相近的文本在向量空间中距离也近。

```
文本 → Embedding模型 → 向量（如768维浮点数）
                          ↓
                    向量空间中的点

"iPhone 15多少钱" → [0.12, -0.34, 0.56, ...]
"苹果手机价格"     → [0.11, -0.33, 0.55, ...]  ← 相似度高（语义接近）
"今天天气很好"     → [0.87, 0.21, -0.45, ...]  ← 相似度低（语义无关）
```

**为什么需要向量检索？** 关键词搜索只能匹配字面相同的内容，向量检索能匹配**语义相似**的内容。

### 二、Embedding（文本向量化）

```python
# 使用Ollama的BGE-M3模型进行文本向量化
import aiohttp, json

async def get_embedding(text: str, model="bge-m3"):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:11434/api/embed",
            json={"model": model, "input": text}
        ) as resp:
            result = await resp.json()
            return result["embeddings"][0]  # 返回1024维向量

# 示例
vec = await get_embedding("iPhone 15多少钱")
# vec = [0.023, -0.147, 0.891, ..., -0.034]  # 1024个浮点数
```

### 三、FAISS（Facebook AI Similarity Search）

FAISS 是 Meta 开源的高效向量相似度搜索库，专门用于**从海量向量中快速找到最相似的Top-K个**。

```python
import faiss
import numpy as np

# 1. 创建索引
dimension = 1024  # 向量维度（BGE-M3输出1024维）
index = faiss.IndexFlatIP(dimension)  # 内积索引（等价于余弦相似度，需先归一化）

# 2. 添加向量
vectors = np.random.random((10000, dimension)).astype('float32')
faiss.normalize_L2(vectors)  # L2归一化（让内积=余弦相似度）
index.add(vectors)

# 3. 搜索
query = np.random.random((1, dimension)).astype('float32')
faiss.normalize_L2(query)
scores, indices = index.search(query, k=5)  # 找最相似的5个

print(f"相似度分数: {scores}")     # [[0.98, 0.95, 0.91, 0.88, 0.85]]
print(f"对应索引: {indices}")      # [[234, 1567, 89, 4523, 789]]
```

### 四、项目中 FAISS 的两种用途

#### 用途1：RAG 文档检索

```python
# 传统RAG中的FAISS使用
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings

embeddings = OllamaEmbeddings(model="bge-m3")

# 建索引
vectorstore = FAISS.from_documents(documents, embeddings)

# 检索
results = vectorstore.similarity_search("iPhone 15价格", k=3)
# 返回最相关的3个文档块
```

#### 用途2：语义缓存（Semantic Cache）——项目核心创新

```python
# redis_semantic_cache.py —— FAISS加速的语义缓存

class RedisSemanticCache:
    """
    核心思路：用户问过的问题，相似问题直接返回缓存答案
    
    架构：
    - FAISS：内存中快速向量检索（毫秒级）
    - Redis：持久化存储向量+响应（重启不丢数据）
    """
    
    def __init__(self):
        self.redis = redis.from_url("redis://localhost:6379")
        self.faiss_index = None          # FAISS索引（内存）
        self.id_to_hash = []             # FAISS索引ID → Redis Hash映射
        self.score_threshold = 0.90      # 相似度阈值
        self._rebuild_index()            # 启动时从Redis重建FAISS索引
    
    def _rebuild_index(self):
        """启动时从Redis加载所有向量，重建FAISS索引"""
        all_keys = self.redis.keys("cache:vec:*")
        vectors, hash_ids = [], []
        
        for vec_key in all_keys:
            raw = self.redis.get(vec_key)
            vec = np.array(json.loads(raw), dtype=np.float32)
            vec = self._normalize(vec)     # L2归一化
            vectors.append(vec)
            hash_ids.append(vec_key.split(":")[-1])
        
        if vectors:
            dim = len(vectors[0])
            self.faiss_index = faiss.IndexFlatIP(dim)
            self.faiss_index.add(np.stack(vectors).astype(np.float32))
            self.id_to_hash = hash_ids
    
    async def lookup(self, messages):
        """查询缓存：用FAISS找最相似的问题"""
        user_msg = self._get_last_user_message(messages)
        
        # 1. 向量化用户问题
        query_vec = await self._get_embedding(user_msg)
        query_vec = self._normalize(np.array(query_vec, dtype=np.float32)).reshape(1, -1)
        
        # 2. FAISS搜索Top-1
        scores, indices = self.faiss_index.search(query_vec, 1)
        best_score = float(scores[0][0])
        
        # 3. 相似度 >= 阈值 → 命中缓存
        if best_score >= self.score_threshold:
            hash_id = self.id_to_hash[indices[0][0]]
            cached = self.redis.get(f"cache:resp:{hash_id}")
            return cached.decode("utf-8")  # 直接返回缓存的回答
        
        return None  # 未命中，需要调LLM
    
    async def update(self, messages, response, expire=3600):
        """更新缓存：新问答对存入Redis+FAISS"""
        user_msg = self._get_last_user_message(messages)
        vector = await self._get_embedding(user_msg)
        
        hash_id = hashlib.md5(user_msg.encode()).hexdigest()
        
        # 存入Redis（向量+响应，设过期时间）
        self.redis.set(f"cache:vec:{hash_id}", json.dumps(vector), ex=expire)
        self.redis.set(f"cache:resp:{hash_id}", response.encode("utf-8"), ex=expire)
        
        # 同步更新FAISS索引
        self._add_to_index(np.array(vector, dtype=np.float32), hash_id)
```

**语义缓存流程图：**

```
用户问题："iPhone 15 Pro多少钱？"
        ↓
  Embedding向量化
        ↓
  FAISS检索（毫秒级）
        ↓
  找到最相似的问题："苹果15Pro价格多少"（相似度0.95）
        ↓
  0.95 >= 0.90（阈值）→ 命中缓存！
        ↓
  从Redis取出缓存的回答 → 直接返回（跳过LLM调用）
  
  另一种情况：
  用户问题："推荐一款适合学生的手机"
        ↓
  FAISS检索最高相似度 = 0.65 < 0.90 → 未命中
        ↓
  正常调LLM → 保存问答对到缓存
```

### 五、为什么用 FAISS + Redis 混合架构？

|  | 纯Redis | 纯FAISS | FAISS+Redis |
|--|---------|---------|-------------|
| 检索速度 | 慢（线性扫描） | 快（索引搜索） | 快 |
| 持久化 | 支持 | 不支持（内存） | 支持 |
| 重启恢复 | 天然支持 | 丢失 | 从Redis重建 |
| 容量 | 受限于内存 | 受限于内存 | Redis可持久化到磁盘 |

### 六、L2归一化的作用

```python
def _normalize(self, vector):
    """L2归一化：让向量长度变为1"""
    norm = np.linalg.norm(vector)  # 计算L2范数（向量长度）
    if norm == 0:
        return vector
    return vector / norm

# 归一化前：vec = [3, 4]          范数 = 5
# 归一化后：vec = [0.6, 0.8]      范数 = 1

# 为什么归一化？
# FAISS的IndexFlatIP计算的是内积(Inner Product)
# 归一化后：内积 = 余弦相似度
# cos(a, b) = (a·b) / (|a| × |b|)  →  |a|=|b|=1时 → cos(a,b) = a·b
```

### 七、面试高频问题

**Q1：什么是FAISS？**
> FAISS是Meta开源的向量相似度搜索库。把文本通过Embedding模型转成向量，FAISS能从百万级向量中毫秒级找到最相似的Top-K。项目里用FAISS做RAG文档检索和语义缓存。

**Q2：语义缓存是什么？怎么实现的？**
> 语义缓存是根据问题语义（而非关键词）做缓存匹配。实现：用户问题Embedding后用FAISS检索历史问题，如果相似度超过阈值（0.90），直接返回缓存的回答。存储用Redis持久化，检索用FAISS加速。

**Q3：为什么需要L2归一化？**
> FAISS的IndexFlatIP计算内积，L2归一化让向量长度为1，此时内积等于余弦相似度，值域在[-1,1]，便于用固定阈值（如0.90）判断相似度。

---

## 3.5 LangChain + LangGraph

### 一、LangChain 是什么？

LangChain 是一个**LLM应用开发框架**，提供了模块化的组件来构建LLM应用：

```
LangChain 核心组件：
┌──────────────────────────────────────────────┐
│                                              │
│  Model I/O        → 统一调用各LLM的接口       │
│  Retrieval        → 文档加载、切分、检索       │
│  Chains           → 串联多个步骤的管道         │
│  Agents           → 让LLM自主决策调用工具      │
│  Memory           → 管理对话历史               │
│  Callbacks        → 日志、流式输出等回调       │
│                                              │
└──────────────────────────────────────────────┘
```

```python
# LangChain 基本用法
from langchain_deepseek import ChatDeepSeek
from langchain_core.prompts import ChatPromptTemplate

# 1. 创建LLM实例
llm = ChatDeepSeek(
    api_key="sk-xxx",
    base_url="https://api.deepseek.com",
    model="deepseek-chat"
)

# 2. 创建Prompt模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个电商客服"),
    ("human", "{question}")
])

# 3. 链式调用（LCEL语法）
chain = prompt | llm

# 4. 执行
response = await chain.ainvoke({"question": "iPhone 15多少钱？"})
print(response.content)
```

### 二、LangGraph 是什么？为什么要用？

LangChain 的 Chain 是**线性执行**的（A→B→C），但实际业务需要**条件分支、循环、状态管理**：

|  | LangChain Chain | LangGraph |
|--|----------------|-----------|
| 执行方式 | 线性A→B→C | 图（有向图，支持分支和循环） |
| 条件路由 | 不支持 | 支持（conditional_edges） |
| 状态管理 | 需要手动管理 | 内置State管理 |
| 循环 | 不支持 | 支持（Agent循环） |
| 并行 | 不支持 | 支持（Map-Reduce） |
| 人机交互 | 不支持 | 支持（interrupt+resume） |

**LangGraph = LangChain + 状态图**，用于构建复杂的Agent工作流。

### 三、LangGraph 核心概念

#### 1. State（状态）

```python
from dataclasses import dataclass, field
from typing import Annotated
from langgraph.graph.message import add_messages

@dataclass
class InputState:
    """输入状态——用户的输入消息"""
    messages: Annotated[list, add_messages]   # add_messages：新消息追加而非覆盖

@dataclass
class AgentState(InputState):
    """完整状态——Agent处理过程中的所有数据"""
    router: dict = field(default_factory=dict)   # 意图分类结果
    steps: list = field(default_factory=list)     # 执行步骤记录
    question: str = ""                             # 提取的问题
    answer: str = ""                               # 最终回答
```

> **add_messages 的作用：** 当新消息到来时，自动追加到messages列表（而不是替换）。这保证了对话历史的完整性。

#### 2. Node（节点）—— 处理函数

```python
async def analyze_and_route_query(state: AgentState, *, config) -> dict:
    """节点：意图分类"""
    model = ChatDeepSeek(model="deepseek-chat")
    
    # 用Structured Output让LLM返回分类结果
    router = await model.with_structured_output(Router).ainvoke(state.messages)
    
    # 返回要更新的状态字段（部分更新，不影响其他字段）
    return {"router": router}

async def respond_to_general_query(state: AgentState, *, config) -> dict:
    """节点：处理闲聊"""
    response = await llm.ainvoke(state.messages)
    return {"answer": response.content, "messages": [response]}

async def create_research_plan(state: AgentState, *, config) -> dict:
    """节点：调用知识图谱子图"""
    kg_graph = build_kg_subgraph()
    result = await kg_graph.ainvoke({"question": state.router["question"]})
    return {"answer": result["answer"], "messages": [AIMessage(content=result["answer"])]}
```

#### 3. Edge（边）—— 节点间的连接

```python
from langgraph.graph import StateGraph, START, END

builder = StateGraph(AgentState, input=InputState)

# 添加节点
builder.add_node(analyze_and_route_query)
builder.add_node(respond_to_general_query)
builder.add_node(get_additional_info)
builder.add_node("create_research_plan", create_research_plan)

# 固定边：START → 第一个节点
builder.add_edge(START, "analyze_and_route_query")

# 条件边：根据意图分类结果路由到不同节点
builder.add_conditional_edges(
    "analyze_and_route_query",       # 源节点
    route_query,                     # 路由函数（返回目标节点名）
    {
        "respond_to_general_query": "respond_to_general_query",
        "get_additional_info": "get_additional_info",
        "create_research_plan": "create_research_plan",
    }
)

# 固定边：各节点 → END
builder.add_edge("respond_to_general_query", END)
builder.add_edge("get_additional_info", END)
builder.add_edge("create_research_plan", END)
```

#### 4. 条件路由函数

```python
def route_query(state: AgentState) -> str:
    """根据router.type决定下一步走哪个节点"""
    query_type = state.router["type"]
    
    if query_type == "general-query":
        return "respond_to_general_query"
    elif query_type == "additional-query":
        return "get_additional_info"
    elif query_type == "graphrag-query":
        return "create_research_plan"
    elif query_type == "image-query":
        return "create_image_query"
    elif query_type == "file-query":
        return "create_file_query"
```

#### 5. Compile & Run

```python
from langgraph.checkpoint.memory import MemorySaver

# 编译图（checkpointer实现会话持久化）
graph = builder.compile(checkpointer=MemorySaver())

# 运行
config = {"configurable": {"thread_id": "conversation_123"}}
result = await graph.ainvoke(
    {"messages": [HumanMessage(content="iPhone 15多少钱？")]},
    config=config
)

# 流式输出
async for chunk, metadata in graph.astream(
    {"messages": [HumanMessage(content="iPhone 15多少钱？")]},
    config=config,
    stream_mode="messages"
):
    if chunk.content:
        print(chunk.content, end="")
```

### 四、完整的主图结构

```
                    START
                      │
                      ↓
          ┌─── analyze_and_route_query ───┐
          │       （意图分类节点）           │
          └──────────┬────────────────────┘
                     │
        ┌────────────┼────────────────────────┐
        ↓            ↓            ↓            ↓
  general-query  graphrag-query  image-query  additional-query
        │            │            │            │
        ↓            ↓            ↓            ↓
  respond_to_    create_      create_      get_additional
  general_query  research_    image_query  _info
                plan(KG子图)
        │            │            │            │
        ↓            ↓            ↓            ↓
       END          END          END          END
```

### 五、Checkpointer（状态持久化）

```python
# MemorySaver：内存存储（重启丢失）
from langgraph.checkpoint.memory import MemorySaver
checkpointer = MemorySaver()

# SQLite：持久化到文件
from langgraph.checkpoint.sqlite import SqliteSaver
checkpointer = SqliteSaver.from_conn_string("checkpoints.db")

# 编译时传入
graph = builder.compile(checkpointer=checkpointer)

# 通过thread_id区分不同会话
config = {"configurable": {"thread_id": "user_123_conv_456"}}

# 同一会话的多次调用共享状态
result1 = await graph.ainvoke({"messages": ["你好"]}, config=config)
result2 = await graph.ainvoke({"messages": ["iPhone多少钱"]}, config=config)
# 第二次调用时，state中保留了第一次的对话历史
```

### 六、面试高频问题

**Q1：LangChain和LangGraph的区别？**
> LangChain是LLM应用框架，提供模型调用、检索、Chain等组件。LangGraph是基于LangChain的状态图框架，支持条件分支、循环、并行执行，适合构建复杂的Agent工作流。简单链用LangChain，复杂Agent用LangGraph。

**Q2：LangGraph的State、Node、Edge分别是什么？**
> State是贯穿整个工作流的数据结构，Node是处理函数（接收State返回状态更新），Edge定义节点间的连接（固定边或条件边）。流程是START→Node→...→END。

**Q3：LangGraph怎么做会话持久化？**
> 用Checkpointer。编译图时传入checkpointer（MemorySaver内存存储或SqliteSaver持久化），运行时通过configurable.thread_id区分不同会话，同一thread_id的多次调用共享状态历史。

---

## 3.6 Multi-Agent 多智能体架构

### 一、什么是 Multi-Agent？

把一个复杂的AI任务**拆分给多个专职Agent**，每个Agent只负责自己擅长的部分，通过协作完成整体任务。

```
单Agent：
  用户问题 → 一个大Agent包揽一切（容易出错、效率低）

Multi-Agent：
  用户问题 → 路由Agent（分类）
               → 闲聊Agent（处理闲聊）
               → 知识库Agent（查询知识）
                    → 规划Agent（拆分子任务）
                    → 工具选择Agent（选合适工具）
                         → Cypher Agent（查Neo4j）
                         → GraphRAG Agent（查文档）
                    → 总结Agent（汇总结果）
                    → 回答Agent（生成最终答案）
```

### 二、项目中 Multi-Agent 的层级设计

```
第一层：主Agent（lg_builder.py）
├── 意图路由：classify user query
│
├── 闲聊Agent：respond_to_general_query
│   └── 直接用LLM回答
│
├── 追问Agent：get_additional_info
│   └── 提示用户补充信息
│
├── 图片Agent：create_image_query
│   └── 调用GPT-4o分析图片
│
└── 知识图谱子图（kg_sub_graph/）  ← 第二层：子Agent系统
    │
    ├── 护栏Agent（Guardrails）
    │   └── 判断问题是否在业务范围内
    │
    ├── 规划Agent（Planner）
    │   └── 把复杂问题拆成子任务
    │
    ├── 工具选择Agent（Tool Selection）× N（并行）
    │   ├── Cypher查询Agent → Neo4j
    │   ├── 预定义查询Agent → 预写好的Cypher
    │   └── GraphRAG Agent → 微软GraphRAG
    │
    ├── 总结Agent（Summarize）
    │   └── 汇总多个工具的结果
    │
    └── 最终回答Agent（Final Answer）
        └── 生成用户友好的回答
```

### 三、子图（Sub-Graph）实现

知识图谱子图本身也是一个完整的 StateGraph，嵌套在主图内部：

```python
# kg_builder.py —— 知识图谱子图构建

def build_kg_subgraph():
    """构建知识图谱子图"""
    builder = StateGraph(OverallState, input=InputState, output=OutputState)
    
    # 添加所有子Agent节点
    builder.add_node("guardrails", create_guardrails_node(llm, graph))
    builder.add_node("planner", create_planner_node(llm))
    builder.add_node("cypher_query", create_cypher_query_node())
    builder.add_node("predefined_cypher", create_predefined_cypher_node(graph))
    builder.add_node("customer_tools", create_graphrag_query_node())
    builder.add_node("tool_selection", create_tool_selection_node(llm))
    builder.add_node("summarize", create_summarization_node(llm))
    builder.add_node("final_answer", create_final_answer_node())
    
    # 边
    builder.add_edge(START, "guardrails")
    builder.add_conditional_edges("guardrails", guardrails_conditional_edge)
    builder.add_conditional_edges("planner", map_reduce_planner_to_tool_selection)
    builder.add_edge("cypher_query", "summarize")
    builder.add_edge("predefined_cypher", "summarize")
    builder.add_edge("customer_tools", "summarize")
    builder.add_edge("summarize", "final_answer")
    builder.add_edge("final_answer", END)
    
    return builder.compile()
```

**子图内部流程：**

```
START → Guardrails（业务范围检查）
           │
     ┌─────┴─────┐
     ↓           ↓
  超出范围    在范围内
     │           │
     ↓           ↓
  Final      Planner（任务拆分）
  Answer         │
                 ↓
          Map-Reduce并行 ← 关键！
          ┌──────┼──────┐
          ↓      ↓      ↓
      tool_   tool_   tool_
      select  select  select
       │      │       │
       ↓      ↓       ↓
    Cypher  Predef  GraphRAG
       │      │       │
       └──────┼───────┘
              ↓
         Summarize（汇总）
              ↓
        Final Answer → END
```

### 四、各子Agent的职责

#### 1. 护栏Agent（Guardrails）—— 安全校验

```python
async def guardrails(state):
    """检查用户问题是否在业务范围内"""
    # 用LLM判断
    prompt = f"""判断以下问题是否与电商业务相关：
    问题：{state["question"]}
    只能回答：continue（继续）或 end（结束）"""
    
    result = await llm.with_structured_output(GuardrailsOutput).ainvoke(prompt)
    
    if result.decision == "continue":
        return {"next_action": "planner"}     # 进入规划
    else:
        return {"next_action": "final_answer"}  # 直接回答"无法处理"
```

#### 2. 规划Agent（Planner）—— 任务拆分

```python
async def planner(state):
    """把复杂问题拆成多个子任务"""
    prompt = f"""把用户问题拆分成可以并行查询的子任务。
    例如："iPhone 15和Samsung S24哪个好" 可以拆成：
    - 查询iPhone 15的信息
    - 查询Samsung S24的信息"""
    
    result = await llm.with_structured_output(PlannerOutput).ainvoke({
        "question": state["question"]
    })
    
    return {"tasks": result.tasks}
    # tasks = [
    #   Task(question="iPhone 15的价格、配置、评价", parent_task="compare"),
    #   Task(question="Samsung S24的价格、配置、评价", parent_task="compare")
    # ]
```

#### 3. 工具选择Agent（Tool Selection）—— 为每个子任务选工具

```python
async def tool_selection(state):
    """为每个子任务选择最合适的查询工具"""
    question = state["question"]
    
    # LLM决定用哪个工具
    result = await tool_chain.ainvoke({"question": question})
    
    # 根据选择的工具路由到对应节点
    if result.tool == "text2cypher":
        return Command(goto="cypher_query")        # 动态生成Cypher
    elif result.tool == "predefined_cypher":
        return Command(goto="predefined_cypher")    # 用预定义查询
    elif result.tool == "graphrag":
        return Command(goto="customer_tools")       # 用GraphRAG查文档
```

#### 4. 总结Agent（Summarize）—— 汇总多工具结果

```python
async def summarize(state):
    """汇总所有工具的查询结果"""
    results = [c.get("records") for c in state.get("cyphers", []) if c.get("records")]
    
    if results:
        summary = await llm.ainvoke(
            f"基于以下查询结果，简洁回答用户问题：\n"
            f"问题：{state['question']}\n"
            f"查询结果：{results}"
        )
        return {"summary": summary.content}
    return {"summary": "未找到相关数据。"}
```

### 五、面试高频问题

**Q1：为什么要用Multi-Agent而不是一个大Agent？**
> 1. 职责分离：每个Agent只做一件事，Prompt更精准，准确率更高 2. 并行执行：多个子任务可以并行处理，效率更高 3. 可维护性：单个Agent出问题只影响局部 4. 可扩展性：新增功能只需添加新Agent。

**Q2：子图（Sub-Graph）是什么？**
> 子图是嵌套在主图内部的完整StateGraph。主图负责意图路由，子图（如知识图谱子图）内部有自己独立的节点、边和状态管理。子图对主图来说是黑盒——主图只需调用它获取结果。

**Q3：护栏Agent（Guardrails）的作用？**
> 在正式处理前做安全检查，判断用户问题是否在业务范围内。超出范围的问题直接返回拒绝回答，避免触发不必要的LLM调用和知识库查询，节省成本的同时防止越界。

---

## 3.7 意图识别 + Map-Reduce 并行

### 一、意图识别（Intent Recognition）

意图识别是主Agent的第一步——**判断用户想干什么**，然后路由到对应的处理节点。

#### 项目中的意图分类

```python
class Router(TypedDict):
    """LLM返回的意图分类结果"""
    logic: str    # LLM的推理过程（为什么这样分类）
    type: Literal[
        "general-query",    # 闲聊："你好"、"讲个笑话"
        "additional-query", # 需要追问："我想买手机"（买哪个？预算？）
        "graphrag-query",   # 知识库查询："iPhone 15多少钱"
        "image-query",      # 图片处理：用户上传了图片
        "file-query"        # 文件处理：用户上传了文件
    ]
```

#### 意图识别的Prompt设计

```python
ROUTER_SYSTEM_PROMPT = """你是电商智能客服，请将用户问题分类：

## general-query
与电商业务无关的闲聊、日常对话

## additional-query
用户想咨询但缺少关键信息（没说具体型号、没给订单号、问题描述不清）

## graphrag-query
可以通过查询知识库回答的问题：
- 产品价格、库存、规格参数
- 订单状态、物流查询
- 会员积分、促销活动
- 退换货政策
- 产品使用指南

## image-query
用户上传了图片需要分析

## file-query
用户上传了文件需要处理
"""
```

#### 实际分类示例

| 用户输入 | 分类 | 原因 |
|----------|------|------|
| "你好" | general-query | 闲聊 |
| "iPhone 15 Pro Max 256G多少钱" | graphrag-query | 查产品价格 |
| "我的订单到哪了" | additional-query | 缺少订单号 |
| "订单号12345到哪了" | graphrag-query | 查物流 |
| "这两种手机哪个好" | additional-query | 没说哪两种 |
| "iPhone和Samsung哪个拍照好" | graphrag-query | 可查知识库对比 |

> **面试一句话：** "意图识别用LLM的Structured Output能力，通过Router TypedDict约束LLM返回预定义的5种意图类型。系统Prompt定义每种意图的特征和判断标准，确保分类准确。"

### 二、Map-Reduce 并行工具调用

#### 什么是 Map-Reduce？

```
Map阶段：把一个复杂任务拆成多个独立子任务，并行处理
Reduce阶段：汇总所有子任务的结果

用户："对比iPhone 15和Samsung S24的配置和价格"
           ↓
    Planner拆分任务：
    ├── Task1: "查询iPhone 15的配置和价格"
    ├── Task2: "查询Samsung S24的配置和价格"
    └── Task3: "查询两款手机的用户评价"
           ↓
    Map阶段（并行执行）：
    ┌── Task1 → Tool Select → Cypher Agent → 结果1 ─┐
    ├── Task2 → Tool Select → Cypher Agent → 结果2 ─┤
    └── Task3 → Tool Select → GraphRAG Agent → 结果3─┤
                                                      ↓
    Reduce阶段（汇总）：
    Summarize Agent 把结果1+2+3 综合生成对比报告
```

#### LangGraph 中的 Map-Reduce 实现

```python
from langgraph.types import Send

def map_reduce_planner_to_tool_selection(state: OverallState) -> list[Send]:
    """
    Map阶段的关键函数：
    Planner产出了多个Task，每个Task发送一个tool_selection实例
    
    Send的作用：创建节点的多个并行实例
    - 同一个"tool_selection"节点，每个Task一个实例
    - LangGraph自动并行执行所有实例
    """
    return [
        Send(
            "tool_selection",    # 目标节点名
            {                    # 传给该实例的输入状态
                "question": task.question,
                "parent_task": task.parent_task,
            }
        )
        for task in state.get("tasks", [])
    ]

# 在图中使用
builder.add_conditional_edges(
    "planner",                            # 源节点
    map_reduce_planner_to_tool_selection, # Map函数
    ["tool_selection"]                    # 目标节点（可以并行多个实例）
)
```

#### 完整流程图解

```
用户："iPhone 15和Samsung S24的价格和评价"
    ↓
Guardrails → 在范围内 ✓
    ↓
Planner → 拆成3个Task：
    Task1: "iPhone 15价格"
    Task2: "Samsung S24价格"  
    Task3: "两款手机评价"
    ↓
Map阶段（Send并行分发）：
    ┌─ Send("tool_selection", {question: "iPhone 15价格"}) ──→ Cypher查询
    ├─ Send("tool_selection", {question: "Samsung S24价格"}) ─→ Cypher查询
    └─ Send("tool_selection", {question: "两款手机评价"}) ──→ GraphRAG查询
    ↓ （三个工具并行执行）
    ↓
Reduce阶段（Summarize）：
    汇总三条结果：
    - iPhone 15 Pro: ¥8999
    - Samsung S24: ¥6999
    - 评价：iPhone拍照更自然，Samsung夜景更强
    ↓
Final Answer → "iPhone 15 Pro售价8999元，Samsung S24售价6999元..."
```

### 三、Send 的本质（面试可能深问）

```python
# Send 是 LangGraph 的特殊对象，实现并行
from langgraph.types import Send

# 普通边：一个节点只能有一个输出
builder.add_edge("A", "B")  # A完成后去B（只有一个）

# 条件边：一个节点输出到多个目标之一
builder.add_conditional_edges("A", route_func, {"B": "B", "C": "C"})
# A完成后去B或C（只能选一个）

# Send：一个节点输出到同一目标的多个实例
def map_func(state):
    return [Send("B", {"task": t}) for t in state.tasks]
# A完成后，创建N个B的实例，并行执行
```

### 四、面试高频问题

**Q1：意图识别怎么实现的？**
> 用LLM的Structured Output功能。定义Router TypedDict（包含logic和type字段），系统Prompt描述每种意图的特征。LLM分析用户问题后返回结构化的分类结果，程序根据type字段路由到对应处理节点。

**Q2：Map-Reduce在Agent中怎么用的？**
> Planner Agent把复杂问题拆成多个子任务，每个子任务通过Send对象分发到tool_selection节点的独立实例，LangGraph自动并行执行。所有工具完成后，Summarize Agent汇总结果生成最终回答。

**Q3：Send和普通边有什么区别？**
> 普通边是一个节点执行完跳到下一个节点（一对一）。Send可以创建同一节点的多个实例并行执行（一对多），每个实例有独立的输入状态。这是LangGraph实现Map-Reduce的关键机制。

---

## 3.8 语义缓存 + 滑动窗口

### 一、语义缓存（Semantic Cache）

#### 为什么需要缓存？

```
没有缓存：
  用户A问"iPhone 15多少钱" → LLM处理（耗时2秒，花费￥0.01）
  用户B问"苹果15什么价格" → LLM处理（耗时2秒，花费￥0.01）
  用户C问"iPhone 15 Pro售价多少" → LLM处理（耗时2秒，花费￥0.01）
  → 三个问题语义相同，但每次都调LLM，浪费钱和时间

有缓存：
  用户A问"iPhone 15多少钱" → LLM处理 → 缓存
  用户B问"苹果15什么价格" → FAISS检索 → 相似度0.96 → 命中缓存！瞬间返回
  用户C问"iPhone 15 Pro售价多少" → FAISS检索 → 相似度0.92 → 命中缓存！瞬间返回
```

#### 缓存命中判断标准

```python
# 核心参数
SCORE_THRESHOLD = 0.90   # 相似度阈值（0-1）

# 判断逻辑
if similarity_score >= 0.90:
    return cached_response    # 命中：直接返回缓存
else:
    call_llm_and_cache()      # 未命中：调LLM并存入缓存
```

**为什么不用精确匹配？** 因为同一意图的表达方式千变万化："iPhone 15多少钱"、"苹果15什么价格"、"15pro售价"都是问价格，关键词匹配搞不定，必须用语义相似度。

#### 缓存存储结构

```
Redis 中的数据：

Key: cache:vec:{md5(原始问题)}     Value: [0.023, -0.147, ...]  # 向量（JSON）
Key: cache:resp:{md5(原始问题)}    Value: "iPhone 15售价7999元"  # 缓存回答
Key: cache:meta:{md5(原始问题)}    Value: {                      # 元数据
    "created_at": 1719000000,
    "last_access": 1719003600,
    "access_count": 5
}

FAISS 索引（内存）：
  IndexFlatIP(1024维)  # 内积索引
  包含所有向量 → 快速检索
```

#### 自动清理机制

```python
async def _auto_cleanup(self):
    """后台任务：缓存超过最大数量时自动清理"""
    while True:
        all_keys = self.redis.keys("cache:meta:*")
        
        if len(all_keys) > self.max_cache_size:
            # 按最后访问时间排序
            items = [(k, json.loads(self.redis.get(k))["last_access"]) for k in all_keys]
            items.sort(key=lambda x: x[1])  # 最旧的排前面
            
            # 删除最旧的条目
            for key, _ in items[:len(all_keys) - self.max_cache_size]:
                hash_id = key.split(":")[-1]
                self.redis.delete(f"cache:vec:{hash_id}")
                self.redis.delete(f"cache:resp:{hash_id}")
                self.redis.delete(f"cache:meta:{hash_id}")
            
            # 重建FAISS索引
            self._rebuild_index()
        
        await asyncio.sleep(self.cleanup_interval)
```

### 二、滑动窗口（Sliding Window）

#### 为什么需要滑动窗口？

LLM的输入有**token长度限制**，而且按token收费。对话越长，发送的历史消息越多：

```
第1轮对话：1条历史 → 发送1条
第10轮对话：10条历史 → 发送10条
第50轮对话：50条历史 → 发送50条 ← Token爆炸！又贵又慢！
```

**滑动窗口：** 只保留**最近N轮**对话历史，丢弃更早的消息。

#### 项目中的实现

```python
# message_utils.py

def sliding_window_messages(
    messages: list[dict],
    max_rounds: int = 10,           # 保留最近10轮
    max_chars_per_msg: int = 2000,  # 每条消息最多2000字符
) -> list[dict]:
    """对对话历史应用滑动窗口"""
    
    if not messages:
        return messages
    
    # 1. 分离系统消息和对话消息
    system_msgs = [m for m in messages if m["role"] == "system"]
    dialog_msgs = [m for m in messages if m["role"] != "system"]
    
    # 2. 统计当前对话轮数（一个"用户消息+AI回复"=一轮）
    dialog_rounds = sum(1 for m in dialog_msgs if m["role"] == "user")
    
    # 3. 如果没超过窗口大小，只截断过长的消息
    if dialog_rounds <= max_rounds:
        return system_msgs + [_truncate(m, max_chars_per_msg) for m in dialog_msgs]
    
    # 4. 超过了：只保留最近max_rounds轮
    kept = _keep_last_rounds(dialog_msgs, max_rounds)
    
    return system_msgs + [_truncate(m, max_chars_per_msg) for m in kept]


def _keep_last_rounds(dialog_msgs: list[dict], max_rounds: int) -> list[dict]:
    """保留最后N轮对话"""
    user_count = 0
    cut_idx = 0
    
    # 从后往前数，找到第max_rounds轮的起始位置
    for i in range(len(dialog_msgs) - 1, -1, -1):
        if dialog_msgs[i]["role"] == "user":
            user_count += 1
            if user_count == max_rounds:
                cut_idx = i
                break
    
    return dialog_msgs[cut_idx:]  # 返回最后N轮


def _truncate(msg: dict, max_chars: int) -> dict:
    """截断过长的单条消息"""
    if len(msg.get("content", "")) > max_chars:
        return {**msg, "content": msg["content"][:max_chars] + "...[已截断]"}
    return msg
```

#### 滑动窗口效果

```
原始对话（50轮，约30000 tokens）：
┌──────────────────────────────────────────────────┐
│ Round 1-40: 早期对话（已经不相关了）               │  ← 丢弃
├──────────────────────────────────────────────────┤
│ Round 41-50: 最近10轮对话                         │  ← 保留
└──────────────────────────────────────────────────┘

应用滑动窗口后（10轮，约6000 tokens）：
┌──────────────────────────────────────────────────┐
│ [System Prompt]                                   │ ← 始终保留
│ Round 41: ...                                     │
│ Round 42: ...                                     │
│ ...                                               │
│ Round 50: ...                                     │ ← 最近10轮
└──────────────────────────────────────────────────┘

Token减少：30000 → 6000（减少80%）
费用减少：$0.0084 → $0.00084（减少90%）
```

### 三、完整请求处理流程（结合缓存+窗口）

```
用户发送消息
    │
    ↓
① 滑动窗口裁剪对话历史（保留最近10轮）
    │
    ↓
② 语义缓存查询（FAISS检索相似问题）
    │
    ├── 命中（相似度 ≥ 0.90）→ 直接返回缓存回答（跳过LLM）
    │
    └── 未命中
         │
         ↓
    ③ LangGraph Agent处理
         ├── 意图识别
         ├── 路由到对应Agent
         ├── 知识库查询（Neo4j/GraphRAG）
         └── 生成回答
         │
         ↓
    ④ 更新语义缓存（存入Redis+FAISS）
         │
         ↓
    ⑤ 返回回答给用户（SSE流式输出）
```

### 四、性能优化效果

| 优化手段 | 效果 | 适用场景 |
|----------|------|----------|
| 语义缓存 | 相似问题秒回，LLM调用减少90% | 重复/相似问题（客服场景极常见） |
| 滑动窗口 | Token减少80-90%，费用降低90% | 长对话场景 |
| Map-Reduce并行 | 多子任务并行，响应时间减少50%+ | 复杂对比/汇总查询 |
| 流式输出 | 首字响应时间<1秒 | 所有场景 |

### 五、面试高频问题

**Q1：语义缓存和普通缓存有什么区别？**
> 普通缓存用key精确匹配（"iPhone 15多少钱"只匹配这个字符串）。语义缓存用向量相似度匹配，"苹果15什么价格"和"iPhone 15多少钱"语义相同，相似度0.96，也能命中缓存。实现方式是FAISS向量检索+Redis持久化。

**Q2：滑动窗口为什么能节省Token？**
> LLM每次调用都要发送完整的对话历史，对话越长token越多。滑动窗口只保留最近N轮（项目默认10轮），丢弃更早的历史。系统Prompt始终保留。实测50轮对话可减少80% token。

**Q3：相似度阈值（0.90）怎么定的？**
> 经验值。太低（如0.70）会导致语义不同的问题也命中缓存（误答），太高（如0.98）会导致几乎无法命中（缓存利用率低）。0.90在客服场景下是精度和命中率的平衡点，可以通过A/B测试调整。

**Q4：整个系统的请求处理流程是什么？**
> 用户消息 → 滑动窗口裁剪历史 → 语义缓存查找（命中则直接返回）→ LangGraph Agent（意图识别→路由→知识库查询→生成回答）→ 更新缓存 → SSE流式返回。关键优化点：缓存避免重复LLM调用，窗口控制Token消耗，Map-Reduce并行加速复杂查询。
