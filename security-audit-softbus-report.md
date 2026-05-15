# OpenHarmony communication_softbus_lite 安全审计报告

**审计时间**: 2026-03-23
**目标项目**: openharmony/communication_softbus_lite
**代码规模**: 609KB (45个文件)

---

## 执行摘要

| 指标 | 数值 |
|------|------|
| 扫描文件数 | 45 |
| Level 1 问题数 | 412 |
| Level 2 分析区域 | 1472 |
| 关键漏洞 | 2 个 (P0-P1) |
| 中危问题 | 5 个 |
| 低危问题 | 多个 |

---

## Level 1: 代码检查 - 关键发现

### 🔴 P0 - 全局加密上下文竞争条件 (CRITICAL)

**文件**: `trans_service/source/utils/aes_gcm.c`

```c
static mbedtls_gcm_context g_aesContext;  // 全局共享变量

int EncryptTransData(...) {
    mbedtls_gcm_init(&g_aesContext);      // 初始化全局上下文
    mbedtls_gcm_setkey(&g_aesContext, ...); // 设置密钥
    // 加密操作...
    mbedtls_gcm_free(&g_aesContext);      // 释放
}
```

**漏洞描述**:
- `g_aesContext` 是静态全局变量，在 `EncryptTransData` 和 `DecryptTransData` 中共享使用
- 多线程环境下，线程A设置密钥后，线程B可能覆盖密钥，导致线程A使用错误的密钥进行加密
- 可能导致密钥泄露或数据被错误加密/解密

**攻击场景**:
1. 线程A调用 `EncryptTransData`，设置密钥K1
2. 线程B调用 `DecryptTransData`，覆盖为密钥K2
3. 线程A继续加密操作，错误地使用密钥K2
4. 结果是加密数据使用的密钥与预期不符

**修复建议**:
```c
// 方案1: 使用局部变量（推荐）
int EncryptTransData(...) {
    mbedtls_gcm_context aesContext;  // 改为局部变量
    mbedtls_gcm_init(&aesContext);
    ret = mbedtls_gcm_setkey(&aesContext, ...);
    // ...
    mbedtls_gcm_free(&aesContext);
}

// 方案2: 如果必须共享，添加互斥锁
static pthread_mutex_t g_aesMutex = PTHREAD_MUTEX_INITIALIZER;
```

---

### 🔴 P1 - 格式字符串漏洞 (HIGH)

**文件**: `os_adapter/include/os_adapter.h:28`

```c
#define SOFTBUS_PRINT(format, ...) printf (format, ##__VA_ARGS__)
```

**漏洞描述**:
- `SOFTBUS_PRINT` 宏直接将 format 参数传递给 printf
- 如果 format 来自用户输入，攻击者可注入格式化字符串（如 `%s%s%s`）
- 可导致内存任意读取或代码执行

**修复建议**:
```c
// 修复方案
#define SOFTBUS_PRINT(format, ...) printf("%s", format)
// 或更安全的方案
#define SOFTBUS_PRINT(format, ...) do { \
    if (strchr(format, '%') != NULL) { \
        printf(format, ##__VA_ARGS__); \
    } else { \
        printf("%s", format); \
    } \
} while(0)
```

---

### 🔴 P1 - 整数下溢风险 (MEDIUM-HIGH)

**文件**: `trans_service/source/utils/aes_gcm.c:102`

```c
int actualPlainLen = cipherTextSize - OVERHEAD_LEN;  // 无符号检查
```

**漏洞描述**:
- `cipherTextSize` 和 `OVERHEAD_LEN` 都是无符号整数
- 如果 `cipherTextSize <= OVERHEAD_LEN`，会导致整数下溢
- 下溢后 `actualPlainLen` 变成一个很大的正数，可能导致缓冲区溢出

**修复建议**:
```c
if (cipherTextSize <= OVERHEAD_LEN) {
    SOFTBUS_PRINT("[TRANS] DecryptTransData invalid cipherTextSize\n");
    return -DBE_AES_CALC_ERROR;
}
int actualPlainLen = cipherTextSize - OVERHEAD_LEN;
```

---

### 🟡 P2 - IV 熵减少问题 (MEDIUM)

**文件**: `authmanager/source/auth_conn.c: GetEncryptTransData`

```c
unsigned char* randomIv = GenerateRandomIv();  // 生成随机IV
// ...
ret += memcpy_s(cipherKey.iv, sizeof(seqNum), &seqNum, sizeof(seqNum));  // 覆盖部分IV
```

**漏洞描述**:
- 先生成16字节随机IV
- 然后将 `seqNum`（序列号，通常可预测）复制到IV的后8字节
- 减少了IV的熵，降低了GCM模式的安全性
- 在极端情况下可能导致GCM nonce重用攻击

**修复建议**:
```c
// 不要覆盖IV，使用完整的随机IV
// 如果需要传递seqNum，应放在密文的其他位置
```

---

### 🟡 P2 - 返回局部变量地址误报 (MEDIUM)

**文件**: `discovery/discovery_service/source/discovery_service.c:281`

```c
return &g_publishModule[i];
```

**分析**:
- 实际返回的是全局数组 `g_publishModule` 的元素地址
- 不是局部变量，但在多线程环境下仍需注意生命周期管理
- 建议: 添加文档说明，明确调用者不应长期持有该指针

---

### 🟢 正确处理的示例

**文件**: `authmanager/source/auth_conn.c: AuthConnPackBytes`

```c
unsigned char *buf = (unsigned char *)calloc(1, sizeof(unsigned char) * len);
if (buf == NULL) {
    return NULL;
}
```

**状态**: ✅ 内存分配失败正确处理

---

## Level 2: AI 深度分析

### 分析 1: COAP 协议解析安全性

**文件**: `discovery/coap/source/coap_adapter.c`

**发现**:
- `COAP_ParseHeader`、`COAP_ParseOption` 等函数有完善的边界检查
- 多处验证 `bufLen` 和指针边界
- 使用了 `memcpy_s` 等安全函数

**建议**:
```bash
# 建议进行 fuzz 测试验证
# 使用 AFL++ 或 libFuzzer
./fuzz_coap_parser -- corpus/
```

---

### 分析 2: 内存管理审查

**总体评价**:
- 项目广泛使用了 `securec.h` 中的安全函数（`memcpy_s`, `memset_s`, `strcpy_s`）
- 相比标准C字符串/内存函数，安全性有显著提升
- 但仍有部分代码使用原始 `malloc/free`，需确保配对正确

---

## 修复优先级矩阵

| 优先级 | 问题 | 文件 | 修复难度 | 影响 |
|--------|------|------|----------|------|
| **P0** | 全局加密上下文竞争条件 | aes_gcm.c | 中 | 密钥泄露、数据损坏 |
| **P1** | 格式字符串漏洞 | os_adapter.h | 低 | 信息泄露、代码执行 |
| **P1** | 整数下溢 | aes_gcm.c | 低 | 缓冲区溢出 |
| **P2** | IV 熵减少 | aes_gcm.c/auth_conn.c | 中 | 加密强度降低 |
| **P3** | COAP fuzz 测试 | coap_adapter.c | 高 | 未知漏洞 |

---

## 修复代码示例

### 修复 1: aes_gcm.c 竞争条件

```c
// 修改前（有问题）
static mbedtls_gcm_context g_aesContext;
int EncryptTransData(...) {
    mbedtls_gcm_init(&g_aesContext);
    // ...
}

// 修改后（安全）
int EncryptTransData(...) {
    mbedtls_gcm_context aesContext;  // 局部变量
    mbedtls_gcm_init(&aesContext);
    int ret = mbedtls_gcm_setkey(&aesContext, MBEDTLS_CIPHER_ID_AES,
                                  cipherkey->key, cipherkey->keybits);
    // ...
    ret = mbedtls_gcm_crypt_and_tag(&aesContext, ...);
    mbedtls_gcm_free(&aesContext);
    return ret;
}
```

### 修复 2: 整数下溢检查

```c
// 修改前
int actualPlainLen = cipherTextSize - OVERHEAD_LEN;

// 修改后
if (cipherTextSize <= OVERHEAD_LEN) {
    return -DBE_AES_CALC_ERROR;
}
int actualPlainLen = cipherTextSize - OVERHEAD_LEN;
```

### 修复 3: 格式字符串漏洞

```c
// 修改前
#define SOFTBUS_PRINT(format, ...) printf (format, ##__VA_ARGS__)

// 修改后
#define SOFTBUS_PRINT(format, ...) printf("%s", format)
```

---

## 建议

### 立即行动 (本周内)
1. **修复 P0 竞争条件**: 将 `g_aesContext` 改为局部变量
2. **修复 P1 整数下溢**: 添加边界检查
3. **审查 `SOFTBUS_PRINT` 使用**: 确认没有用户输入直接传递

### 短期行动 (本月内)
4. **修复 IV 问题**: 确保使用完整随机 IV
5. **添加单元测试**: 针对加密函数添加多线程测试
6. **代码审计**: 审查所有全局可变状态

### 长期行动
7. **集成静态分析**: 将安全审计工具集成到 CI/CD
8. **Fuzz 测试**: 对网络协议解析代码进行 fuzz 测试
9. **安全培训**: 团队安全意识培训

---

## 工具输出原始数据

完整 Level 1 扫描结果 (412 个问题) 见: `security-audit-softbus-raw.md`

---

**审计完成时间**: 2026-03-23
**审计工具**: security-audit skill v1.0
