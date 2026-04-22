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
- [模块三：AI / Agent / RAG](#模块三ai--agent--rag)

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

FastAPI 是 Python 的现代 Web 框架，核心特点：**快**（性能接近Go/Node.js）、**简单**（代码少）、**自动文档**（自带Swagger UI）。

```text
FastAPI 的核心依赖：
├── Starlette    ← 底层HTTP框架（处理请求响应）
├── Pydantic     ← 数据校验（校验请求参数）
└── Uvicorn      ← ASGI服务器（运行FastAPI应用）
```

### 二、第一个 FastAPI 应用

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id}
```

```bash
uvicorn main:app --reload    # --reload 开发热重载
# 访问 http://localhost:8000/docs 自动生成Swagger文档
```

### 三、Pydantic 数据校验

```python
from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    email: str = Field(..., pattern=r"^[\w.-]+@[\w.-]+\.\w+$")
    age: int = Field(default=18, ge=0, le=150)

@app.post("/users")
def create_user(user: UserCreate):
    return {"username": user.username, "email": user.email}
```

> **面试一句话：** "Pydantic用BaseModel+类型注解自动校验请求参数，校验失败自动返回422错误。"

### 四、参数获取的四种方式

| 方式 | 数据来源 | 示例 |
|------|----------|------|
| 路径参数 | URL路径 | `/users/{id}` |
| 查询参数 | `?key=value` | `?page=1&size=10` |
| 请求体 | Body JSON | `{"name": "test"}` |
| Header/Cookie | 请求头/Cookie | `Authorization: Bearer xxx` |

### 五、依赖注入

```python
async def get_current_user(token: str = Header(...)):
    user = verify_token(token)
    if not user:
        raise HTTPException(status_code=401)
    return user

@app.get("/me")
def get_me(user = Depends(get_current_user)):
    return {"username": user.username}
```

> **面试一句话：** "Depends()将认证等横切逻辑抽成函数注入路由，类似Spring IoC但用函数实现。"

### 六、中间件

```python
@app.middleware("http")
async def log_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    print(f"耗时: {time.time()-start:.3f}s")
    return response
```

**CORS（前后端分离必配）：** 浏览器同源策略限制跨域请求，需后端配置 `CORSMiddleware` 允许前端跨域访问。

### 七、面试高频 Q&A

**Q1：FastAPI的特点？** > 异步ASGI高性能、Pydantic自动校验、自带Swagger文档。

**Q2：依赖注入？** > Depends()将通用逻辑（认证、数据库）抽成函数自动注入。

**Q3：Pydantic的作用？** > BaseModel+类型注解自动校验参数，失败返回422。

---

## 5.2 RESTful API 设计

### 一、REST 核心原则

- URL表示资源（名词），HTTP方法表示操作（动词）
- 无状态（每次请求自带Token）

### 二、设计规范

| 操作 | URL | HTTP方法 | 状态码 |
|------|-----|----------|--------|
| 获取列表 | `/users` | GET | 200 |
| 获取单个 | `/users/123` | GET | 200 |
| 创建 | `/users` | POST | 201 |
| 全量更新 | `/users/123` | PUT | 200 |
| 部分更新 | `/users/123` | PATCH | 200 |
| 删除 | `/users/123` | DELETE | 204 |

### 三、面试高频 Q&A

**Q1：什么是RESTful？** > URL名词+HTTP动词+无状态通信。

**Q2：PUT vs PATCH？** > PUT全量更新，PATCH部分更新。

**Q3：为什么无状态？** > 服务器不保存会话，便于水平扩展。

---

## 5.3 设计模式（单例/工厂/观察者/策略）

### 一、单例模式

**核心：** 全局唯一实例。**DCL实现：** volatile + 双重检查。

```java
public class Singleton {
    private static volatile Singleton instance;
    private Singleton() {}
    public static Singleton getInstance() {
        if (instance == null) {
            synchronized (Singleton.class) {
                if (instance == null) instance = new Singleton();
            }
        }
        return instance;
    }
}
```

> volatile禁止指令重排序，两次null检查避免重复创建。

### 二、工厂模式

**核心：** 封装对象创建，调用方不关心具体类。

```java
class AnimalFactory {
    static Animal create(String type) {
        if ("dog".equals(type)) return new Dog();
        if ("cat".equals(type)) return new Cat();
    }
}
```

### 三、观察者模式

**核心：** 一对多通知。状态变化时自动通知所有观察者。

**应用：** Vue响应式、Spring事件机制、消息队列。

### 四、策略模式

**核心：** 算法封装为独立策略类，运行时可替换。消除if-else，符合开闭原则。

**应用：** 主人项目中LLMFactory切换DeepSeek/Ollama就是策略模式。

### 五、总结

| 模式 | 核心思想 | 项目体现 |
|------|----------|---------|
| 单例 | 全局唯一 | LLMFactory |
| 工厂 | 封装创建 | LLMFactory |
| 观察者 | 一对多通知 | Vue响应式 |
| 策略 | 算法可替换 | LLM Provider切换 |

---

# 模块二：MySQL 数据库

## 2.1 MySQL 基本操作

### 一、CRUD 增删改查

```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    age INT DEFAULT 0,
    email VARCHAR(100) UNIQUE
);

INSERT INTO users (name, age, email) VALUES ('张三', 25, 'zs@mail.com');
DELETE FROM users WHERE id = 1;
UPDATE users SET age = 26 WHERE name = '张三';
SELECT name, age FROM users WHERE age > 20 ORDER BY age DESC LIMIT 10;
```

### 二、DELETE vs TRUNCATE

|  | DELETE | TRUNCATE |
|--|-------|----------|
| 本质 | DML，逐行删除 | DDL，删除表再重建 |
| WHERE | 支持 | 不支持 |
| 速度 | 慢 | 快 |
| 回滚 | 可以 | 不可以 |
| 自增ID | 不重置 | 重置 |

### 三、JOIN 连接查询

```sql
-- 内连接：只返回两表都有匹配的行
SELECT u.name, o.amount FROM users u INNER JOIN orders o ON u.id = o.user_id;

-- 左连接：左表全保留，右表没匹配填NULL
SELECT u.name, o.amount FROM users u LEFT JOIN orders o ON u.id = o.user_id;
```

### 四、WHERE vs HAVING

|  | WHERE | HAVING |
|--|-------|--------|
| 过滤时机 | 分组前 | 分组后 |
| 能用聚合函数 | 不能 | 能 |

### 五、面试 Q&A

**DELETE vs TRUNCATE？** > DELETE逐行删除可回滚，TRUNCATE重建表不可回滚。
**INNER JOIN vs LEFT JOIN？** > INNER取交集，LEFT左表全保留。

---

## 2.2 MySQL 索引

### 一、B+ 树结构（面试必问）

```text
                    [30 | 60]                     ← 根节点（只存key）
                  ╱          ╲
         [10|20|30]        [40|50|60]              ← 中间节点
        ╱    |    ╲        ╱    |    ╲
     [1-10] [11-20] [21-30] [31-40] [41-50] [51-60] ← 叶子节点（key+数据）
        └──────┴──────┴──────┴──────┴──────┘
              叶子节点双向链表连接 → 范围查询极快
```

**B+树特点：** 非叶子节点只存key（树更矮IO更少），数据全在叶子（查询稳定），叶子链表（范围查询快）。

> **面试一句话：** "B+树非叶子只存key使树更矮，叶子链表支持范围查询，这是MySQL选择B+树的原因。"

### 二、聚簇索引 vs 非聚簇索引

|  | 聚簇索引（主键） | 非聚簇索引（二级） |
|--|------------------|-------------------|
| 叶子存什么 | 完整行数据 | 主键ID |
| 数量 | 一张表只有一个 | 可以有多个 |
| 查找 | 直接拿到数据 | 需要回表查主键索引 |

**回表：** 二级索引查到主键ID → 回主键索引查完整数据（查两棵树）。

### 三、覆盖索引

查询的所有字段都在索引中，不需要回表。EXPLAIN的Extra显示 `Using index`。

### 四、最左前缀匹配

联合索引 `(name, age, email)` 从最左列开始匹配，遇到范围查询停止。

```sql
-- ✅ name / name,age / name,age,email 都能用
-- ❌ 跳过name直接查age或email不能用
-- ⚠️ name='张三' AND age > 20 AND email='...' 只能用到name和age
```

### 五、索引失效场景

| 场景 | 示例 |
|------|------|
| 函数计算 | `WHERE YEAR(create_time) = 2024` |
| 隐式类型转换 | `WHERE varchar_col = 123` |
| LIKE左模糊 | `WHERE name LIKE '%张'` |
| OR无索引列 | `WHERE name='张三' OR age=25`（age无索引） |

### 六、面试 Q&A

**为什么用B+树？** > 非叶子只存key树更矮，叶子链表支持范围查询。
**什么是回表？** > 二级索引查到主键后回主键索引查完整数据。覆盖索引可避免。
**最左前缀？** > 从最左列开始匹配，遇范围查询停止。

---

## 2.3 MySQL 事务

### 一、ACID 四大特性

| 特性 | 含义 | 实现方式 |
|------|------|----------|
| 原子性(A) | 全做或全不做 | undo log |
| 一致性(C) | 满足约束 | 由A+I+D保证 |
| 隔离性(I) | 并发互不干扰 | 锁 + MVCC |
| 持久性(D) | 永久保存 | redo log |

### 二、并发事务问题

| 问题 | 含义 |
|------|------|
| 脏读 | 读到未提交数据 |
| 不可重复读 | 同事务内同一行两次读不同（被UPDATE） |
| 幻读 | 同事务内两次查询行数不同（被INSERT） |

### 三、四种隔离级别

| 隔离级别 | 脏读 | 不可重复读 | 幻读 |
|----------|------|-----------|------|
| 读未提交 | ❌ | ❌ | ❌ |
| 读已提交(RC) | ✅ | ❌ | ❌ |
| 可重复读(RR)**默认** | ✅ | ✅ | ✅* |
| 串行化 | ✅ | ✅ | ✅ |

*MySQL在RR级别通过MVCC+间隙锁基本解决幻读。

### 四、面试 Q&A

**ACID？** > 原子性(undo log)、一致性、隔离性(锁+MVCC)、持久性(redo log)。
**脏读/不可重复读/幻读？** > 脏读读未提交、不可重复读内容变了、幻读行数变了。

---

## 2.4 MVCC（多版本并发控制）

### 一、三个核心组件

1. **隐藏字段：** `DB_TRX_ID`(最后修改的事务ID) + `DB_ROLL_PTR`(指向undo log旧版本)
2. **undo log版本链：** 每次UPDATE的旧版本通过ROLL_PTR串联
3. **ReadView：** 记录当前活跃事务，判断版本可见性

### 二、可见性判断规则

```text
对每个版本的 DB_TRX_ID：
① == creator_trx_id → 自己改的，可见
② < min_trx_id → 修改时都已提交，可见
③ >= max_trx_id → ReadView之后才开始的，不可见
④ 在 m_ids 中 → 未提交，不可见；不在 → 已提交，可见
不可见 → 沿ROLL_PTR找上一个版本继续判断
```

### 三、RC vs RR 区别（面试必问）

|  | RC | RR |
|--|-----|-----|
| ReadView | 每次SELECT生成新的 | 第一次SELECT生成，后续复用 |
| 效果 | 能看到最新提交数据 | 同事务内读取一致 |

> "RC每次SELECT生成新ReadView，RR只在第一次生成并复用——这就是RR能防止不可重复读的根本原因。"

---

## 2.5 MySQL 锁

### 一、行锁的三种形态

| 锁类型 | 锁什么 | 防止什么 |
|--------|--------|----------|
| 记录锁(Record Lock) | 锁单行 | 防修改/删除 |
| 间隙锁(Gap Lock) | 锁两行之间的间隙 | 防INSERT |
| 临键锁(Next-Key Lock)**默认** | 行 + 前面的间隙 | 防修改 + 防插入（防幻读） |

### 二、共享锁 vs 排他锁

|  | 共享锁(S/读锁) | 排他锁(X/写锁) |
|--|----------------|----------------|
| SQL | `LOCK IN SHARE MODE` | `FOR UPDATE` |
| 读 | 允许其他S锁 | 阻塞 |
| 写 | 阻塞 | 阻塞 |

### 三、面试 Q&A

**InnoDB有哪些行锁？** > 记录锁、间隙锁、临键锁（默认=前两者之和）。
**怎么防幻读？** > 临键锁锁行+间隙防INSERT，MVCC保证读一致性。

---

## 2.6 SQL 优化

### 一、EXPLAIN 关键字段

| 字段 | 含义 | 理想值 |
|------|------|--------|
| type | 访问类型 | ref/range（避免ALL） |
| key | 使用的索引 | 不为NULL |
| rows | 扫描行数 | 越少越好 |
| Extra | 额外信息 | Using index（覆盖索引） |

**type排序：** system > const > eq_ref > ref > range > index > ALL

### 二、优化策略

1. **避免索引失效：** 不在索引列上用函数/运算
2. **避免SELECT ***：** 用覆盖索引
3. **深分页优化：** `WHERE id > 上次最大值 LIMIT n` 代替 `OFFSET`
4. **小表驱动大表：** 小结果集驱动大表查询
5. **EXISTS替代IN：** 子查询结果集大时用EXISTS

### 三、面试 Q&A

**怎么分析慢查询？** > EXPLAIN看type/key/Extra，定位后加索引或改写SQL。
**什么是覆盖索引？** > 查询字段都在索引中不回表，Extra显示Using index。
**深分页怎么优化？** > 游标分页 `WHERE id > ? LIMIT n`。

---

# 模块六：测试技术

---

# 模块六：测试技术

> （待更新）

---

# 模块三：AI / Agent / RAG

> （待更新）
