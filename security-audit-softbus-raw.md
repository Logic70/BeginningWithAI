正在扫描 C 代码: C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite (mode: code)...
# C 语言安全审计报告

**目标**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite`
**模式**: code
**扫描文件**: 45 个
**Level 1 问题**: 412 个
**Level 2 待检区域**: 1472 个

## Level 1 代码检查结果

### format_string_vuln (HIGH)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\os_adapter\include\os_adapter.h:28`
- **描述**: 格式化字符串可能包含用户输入
- **代码**: `#define SOFTBUS_PRINT(format, ...) printf (format, ##__VA_ARGS__)`
- **建议**: 使用 printf("%s", user_input) 固定格式

### return_local_address (HIGH)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\discovery_service.c:281`
- **描述**: 返回局部变量地址（悬垂指针）
- **代码**: `return &g_publishModule[i];`
- **建议**: 使用堆分配或传入缓冲区参数

### return_local_address (HIGH)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\discovery_service.c:313`
- **描述**: 返回局部变量地址（悬垂指针）
- **代码**: `return &g_publishModule[i];`
- **建议**: 使用堆分配或传入缓冲区参数

### return_local_address (HIGH)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\discovery_service.c:386`
- **描述**: 返回局部变量地址（悬垂指针）
- **代码**: `return &g_publishModule[i];`
- **建议**: 使用堆分配或传入缓冲区参数

### return_local_address (HIGH)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\nstackx_device.c:44`
- **描述**: 返回局部变量地址（悬垂指针）
- **代码**: `return &g_interfaceList[NSTACKX_ETH_INDEX];`
- **建议**: 使用堆分配或传入缓冲区参数

### return_local_address (HIGH)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\nstackx_device.c:48`
- **描述**: 返回局部变量地址（悬垂指针）
- **代码**: `return &g_interfaceList[NSTACKX_WLAN_INDEX];`
- **建议**: 使用堆分配或传入缓冲区参数

### return_local_address (HIGH)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\nstackx_device.c:171`
- **描述**: 返回局部变量地址（悬垂指针）
- **代码**: `return &g_localDeviceInfo;`
- **建议**: 使用堆分配或传入缓冲区参数

### return_local_address (HIGH)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\auth_interface.c:57`
- **描述**: 返回局部变量地址（悬垂指针）
- **代码**: `return &g_authSessionMap[i];`
- **建议**: 使用堆分配或传入缓冲区参数

### return_local_address (HIGH)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\auth_interface.c:76`
- **描述**: 返回局部变量地址（悬垂指针）
- **代码**: `return &g_authSessionMap[i];`
- **建议**: 使用堆分配或传入缓冲区参数

### return_local_address (HIGH)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\auth_interface.c:113`
- **描述**: 返回局部变量地址（悬垂指针）
- **代码**: `return &g_authSessionMap[i];`
- **建议**: 使用堆分配或传入缓冲区参数

### return_local_address (HIGH)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\auth_interface.c:327`
- **描述**: 返回局部变量地址（悬垂指针）
- **代码**: `return &node->sKey;`
- **建议**: 使用堆分配或传入缓冲区参数

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\include\utils\aes_gcm.h:7`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `*    http://www.apache.org/licenses/LICENSE-2.0`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\include\utils\comm_defs.h:7`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `*    http://www.apache.org/licenses/LICENSE-2.0`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\include\utils\data_bus_error.h:7`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `*    http://www.apache.org/licenses/LICENSE-2.0`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\include\utils\message.h:7`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `*    http://www.apache.org/licenses/LICENSE-2.0`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\include\utils\tcp_socket.h:7`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `*    http://www.apache.org/licenses/LICENSE-2.0`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\include\utils\tcp_socket.h:20`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `#include <sys/types.h>`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\include\utils\tcp_socket.h:21`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `#include <sys/uio.h>`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\os_adapter\include\os_adapter.h:7`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `*    http://www.apache.org/licenses/LICENSE-2.0`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\interfaces\kits\discovery\discovery_service.h:7`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `*    http://www.apache.org/licenses/LICENSE-2.0`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\interfaces\kits\transport\session.h:7`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `*    http://www.apache.org/licenses/LICENSE-2.0`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\include\coap_service.h:7`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `*    http://www.apache.org/licenses/LICENSE-2.0`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\include\common_info_manager.h:7`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `*    http://www.apache.org/licenses/LICENSE-2.0`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\include\discovery_error.h:7`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `*    http://www.apache.org/licenses/LICENSE-2.0`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\include\coap_adapter.h:7`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `*    http://www.apache.org/licenses/LICENSE-2.0`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\include\coap_def.h:7`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `*    http://www.apache.org/licenses/LICENSE-2.0`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\include\coap_discover.h:7`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `*    http://www.apache.org/licenses/LICENSE-2.0`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\include\coap_socket.h:7`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `*    http://www.apache.org/licenses/LICENSE-2.0`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\include\coap_socket.h:18`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `#include "lwip/sockets.h"`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\include\coap_socket.h:20`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `#include <arpa/inet.h>`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\include\json_payload.h:7`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `*    http://www.apache.org/licenses/LICENSE-2.0`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\include\nstackx.h:7`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `*    http://www.apache.org/licenses/LICENSE-2.0`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\include\nstackx_common.h:7`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `*    http://www.apache.org/licenses/LICENSE-2.0`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\include\nstackx_database.h:7`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `*    http://www.apache.org/licenses/LICENSE-2.0`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\include\nstackx_device.h:7`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `*    http://www.apache.org/licenses/LICENSE-2.0`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\include\nstackx_device.h:20`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `#include "lwip/sockets.h"`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\include\nstackx_device.h:22`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `#include <arpa/inet.h>`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\include\nstackx_error.h:7`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `*    http://www.apache.org/licenses/LICENSE-2.0`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\include\auth_conn.h:7`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `*    http://www.apache.org/licenses/LICENSE-2.0`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\include\auth_interface.h:7`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `*    http://www.apache.org/licenses/LICENSE-2.0`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\include\bus_manager.h:7`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `*    http://www.apache.org/licenses/LICENSE-2.0`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\include\msg_get_deviceid.h:7`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `*    http://www.apache.org/licenses/LICENSE-2.0`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\include\wifi_auth_manager.h:7`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `*    http://www.apache.org/licenses/LICENSE-2.0`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### unchecked_malloc (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\source\utils\aes_gcm.c:29`
- **描述**: 内存分配结果未检查
- **代码**: `unsigned char *randomIv = malloc(IV_LEN);`
- **建议**: 检查返回值: if ((ptr = malloc(size)) == NULL) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\source\utils\aes_gcm.c:7`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `*    http://www.apache.org/licenses/LICENSE-2.0`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\source\utils\aes_gcm.c:22`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `#include "mbedtls/gcm.h"`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### unchecked_array_access (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\source\utils\aes_gcm.c:55`
- **描述**: 数组访问可能越界（无边界检查）
- **代码**: `unsigned char tagBuf[TAG_LEN] = {0};`
- **建议**: 添加边界检查: if (index < sizeof(arr)/sizeof(arr[0]))

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\source\utils\message.c:7`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `*    http://www.apache.org/licenses/LICENSE-2.0`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\source\utils\tcp_socket.c:7`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `*    http://www.apache.org/licenses/LICENSE-2.0`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\source\utils\tcp_socket.c:17`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `#include <arpa/inet.h>`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\source\utils\tcp_socket.c:20`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `#include <lwip/sockets.h>`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\source\utils\tcp_socket.c:22`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `#include <sys/socket.h>`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\source\utils\tcp_socket.c:26`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `#include <netinet/in.h>`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\source\utils\tcp_socket.c:27`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `#include <netinet/tcp.h>`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\source\utils\tcp_socket.c:29`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `#include <sys/types.h>`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\source\utils\tcp_socket.c:73`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `errno = 0;`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\source\utils\tcp_socket.c:82`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `errno = 0;`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\source\utils\tcp_socket.c:89`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `errno = 0;`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\source\utils\tcp_socket.c:121`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `int32_t bytes = 0;`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\source\utils\tcp_socket.c:123`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `errno = 0;`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\source\utils\tcp_socket.c:150`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `errno = 0;`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\source\utils\tcp_socket.c:153`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `rc = 0;`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\os_adapter\source\L0\os_adapter.c:7`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `*    http://www.apache.org/licenses/LICENSE-2.0`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\os_adapter\source\L0\os_adapter.c:16`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `#include "lwip/sockets.h"`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\os_adapter\source\L1\os_adapter.c:7`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `*    http://www.apache.org/licenses/LICENSE-2.0`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### pthread_mutex_lock (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\os_adapter\source\L1\os_adapter.c:36`
- **描述**: 互斥锁操作，需要检查死锁风险
- **代码**: `pthread_mutex_lock((pthread_mutex_t *)mutex);`
- **建议**: 确保锁在异常路径也能释放，考虑使用 pthread_mutex_timedlock

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\coap_service.c:7`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `*    http://www.apache.org/licenses/LICENSE-2.0`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### unchecked_array_access (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\coap_service.c:87`
- **描述**: 数组访问可能越界（无边界检查）
- **代码**: `char serviceData[MAX_DEFAULT_SERVICE_DATA_LEN] = {0};`
- **建议**: 添加边界检查: if (index < sizeof(arr)/sizeof(arr[0]))

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\common_info_manager.c:7`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `* http://www.apache.org/licenses/LICENSE-2.0`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\common_info_manager.c:35`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `#define DEVICE_ID_FILE   "/storage/data/softbus/deviceid"`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### unchecked_array_access (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\common_info_manager.c:51`
- **描述**: 数组访问可能越界（无边界检查）
- **代码**: `tmp[0] = (data[i] & 0xF0) >> FOUR_BIT;`
- **建议**: 添加边界检查: if (index < sizeof(arr)/sizeof(arr[0]))

### unchecked_array_access (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\common_info_manager.c:52`
- **描述**: 数组访问可能越界（无边界检查）
- **代码**: `tmp[1] = data[i] & 0x0F;`
- **建议**: 添加边界检查: if (index < sizeof(arr)/sizeof(arr[0]))

### unchecked_array_access (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\common_info_manager.c:58`
- **描述**: 数组访问可能越界（无边界检查）
- **代码**: `tmp[j] = tmp[j] - NUM_TEN + 'A';`
- **建议**: 添加边界检查: if (index < sizeof(arr)/sizeof(arr[0]))

### unchecked_array_access (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\common_info_manager.c:61`
- **描述**: 数组访问可能越界（无边界检查）
- **代码**: `str[cnt] = tmp[j];`
- **建议**: 添加边界检查: if (index < sizeof(arr)/sizeof(arr[0]))

### unchecked_array_access (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\common_info_manager.c:197`
- **描述**: 数组访问可能越界（无边界检查）
- **代码**: `unsigned char data[MAX_VALUE_SIZE] = {0};`
- **建议**: 添加边界检查: if (index < sizeof(arr)/sizeof(arr[0]))

### unchecked_array_access (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\common_info_manager.c:285`
- **描述**: 数组访问可能越界（无边界检查）
- **代码**: `char deviceId[DEVICEID_MAX_NUM] = {0};`
- **建议**: 添加边界检查: if (index < sizeof(arr)/sizeof(arr[0]))

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\common_info_manager.c:44`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `int cnt = 0;`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\common_info_manager.c:50`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `for (int i = 0; i < len; i++) {`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\common_info_manager.c:54`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `for (int j = 0; j < TWO_NUM; j++) {`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\common_info_manager.c:112`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `unsigned int fileLen = 0;`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\common_info_manager.c:398`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `int len = 0;`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### unchecked_malloc (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\discovery_service.c:244`
- **描述**: 内存分配结果未检查
- **代码**: `g_capabilityData = calloc(1, MAX_SERVICE_DATA_LEN);`
- **建议**: 检查返回值: if ((ptr = malloc(size)) == NULL) { handle_error(); }

### unchecked_malloc (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\discovery_service.c:362`
- **描述**: 内存分配结果未检查
- **代码**: `g_publishModule[i].capabilityData = calloc(1, info->dataLen + 1);`
- **建议**: 检查返回值: if ((ptr = malloc(size)) == NULL) { handle_error(); }

### unchecked_addition (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\discovery_service.c:362`
- **描述**: 内存分配中使用加法可能导致整数溢出
- **代码**: `g_publishModule[i].capabilityData = calloc(1, info->dataLen + 1);`
- **建议**: 检查加法溢出: if (size1 > SIZE_MAX - size2) { handle_error(); }

### unchecked_subtraction (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\discovery_service.c:362`
- **描述**: 内存分配中使用减法可能导致整数下溢
- **代码**: `g_publishModule[i].capabilityData = calloc(1, info->dataLen + 1);`
- **建议**: 确保减法结果非负: if (size1 < size2) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\discovery_service.c:7`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `*    http://www.apache.org/licenses/LICENSE-2.0`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### unchecked_array_access (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\discovery_service.c:167`
- **描述**: 数组访问可能越界（无边界检查）
- **代码**: `char wifiIp[MAX_DEV_IP_LEN] = {0};`
- **建议**: 添加边界检查: if (index < sizeof(arr)/sizeof(arr[0]))

### unchecked_array_access (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\discovery_service.c:469`
- **描述**: 数组访问可能越界（无边界检查）
- **代码**: `unsigned int capabilityBitmap[MAX_CAPABILITY_NUM] = {0};`
- **建议**: 添加边界检查: if (index < sizeof(arr)/sizeof(arr[0]))

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\discovery_service.c:42`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `static int g_isServiceInit = 0;`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\discovery_service.c:56`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `for (unsigned int i = 0; i < sizeof(g_devMap) / sizeof(DeviceMap); i++) {`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\discovery_service.c:123`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `for (unsigned int i = 0; i < num; i++) {`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\discovery_service.c:222`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `g_isServiceInit = 0;`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\discovery_service.c:275`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `for (int i = 0; i < MAX_MODULE_COUNT; i++) {`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\discovery_service.c:294`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `for (int i = 0; i < MAX_MODULE_COUNT; i++) {`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\discovery_service.c:309`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `for (int i = 0; i < MAX_MODULE_COUNT; i++) {`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\discovery_service.c:325`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `for (unsigned int i = 0; i < sizeof(g_capabilityMap) / sizeof(CapabilityMap); i++) {`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\discovery_service.c:352`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `for (int i = 0; i < MAX_MODULE_COUNT; i++) {`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\discovery_service.c:397`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `int len = 0;`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\discovery_service.c:407`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `int moduleUsed = 0;`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\discovery_service.c:408`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `for (int i = 0; i < MAX_MODULE_COUNT; i++) {`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_adapter.c:7`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `*    http://www.apache.org/licenses/LICENSE-2.0`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### unchecked_array_access (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_adapter.c:241`
- **描述**: 数组访问可能越界（无边界检查）
- **代码**: `buf->readWriteBuf[0] = (char)(pkt->header.ver << COAP_SHIFT_BIT6);`
- **建议**: 添加边界检查: if (index < sizeof(arr)/sizeof(arr[0]))

### unchecked_array_access (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_adapter.c:242`
- **描述**: 数组访问可能越界（无边界检查）
- **代码**: `buf->readWriteBuf[0] = (char)((unsigned char)buf->readWriteBuf[0] |`
- **建议**: 添加边界检查: if (index < sizeof(arr)/sizeof(arr[0]))

### unchecked_array_access (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_adapter.c:244`
- **描述**: 数组访问可能越界（无边界检查）
- **代码**: `buf->readWriteBuf[1] = (char)pkt->header.code;`
- **建议**: 添加边界检查: if (index < sizeof(arr)/sizeof(arr[0]))

### unchecked_array_access (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_adapter.c:245`
- **描述**: 数组访问可能越界（无边界检查）
- **代码**: `buf->readWriteBuf[BUF_OFFSET_BYTE2] = (char)((pkt->header.varSection.msgId & 0xFF00) >> COAP_SHIFT_BIT8);`
- **建议**: 添加边界检查: if (index < sizeof(arr)/sizeof(arr[0]))

### unchecked_array_access (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_adapter.c:246`
- **描述**: 数组访问可能越界（无边界检查）
- **代码**: `buf->readWriteBuf[BUF_OFFSET_BYTE3] = (char)(pkt->header.varSection.msgId & 0x00FF);`
- **建议**: 添加边界检查: if (index < sizeof(arr)/sizeof(arr[0]))

### unchecked_array_access (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_adapter.c:429`
- **描述**: 数组访问可能越界（无边界检查）
- **代码**: `buf->readWriteBuf[0] = (char)((unsigned char)buf->readWriteBuf[0] | token->len);`
- **建议**: 添加边界检查: if (index < sizeof(arr)/sizeof(arr[0]))

### unchecked_array_access (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_adapter.c:431`
- **描述**: 数组访问可能越界（无边界检查）
- **代码**: `buf->readWriteBuf[BUF_OFFSET_BYTE2] = (char)((unsigned char)buf->readWriteBuf[BUF_OFFSET_BYTE2]`
- **建议**: 添加边界检查: if (index < sizeof(arr)/sizeof(arr[0]))

### unchecked_array_access (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_adapter.c:598`
- **描述**: 数组访问可能越界（无边界检查）
- **代码**: `COAP_Option options[COAP_MAX_OPTION] = {0};`
- **建议**: 添加边界检查: if (index < sizeof(arr)/sizeof(arr[0]))

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_adapter.c:114`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `unsigned char optionIndex = 0;`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_adapter.c:115`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `unsigned short delta = 0;`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_adapter.c:137`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `pkt->payload.len = 0;`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_adapter.c:199`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `pkt->token.len = 0;`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_adapter.c:304`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `unsigned char delta = 0;`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_adapter.c:305`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `unsigned char len = 0;`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_adapter.c:327`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `unsigned short runningDelta = 0;`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_adapter.c:364`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `prevOptionNum = 0;`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_adapter.c:463`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `for (i = 0; i < param->optionsNum; i++) {`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_adapter.c:509`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `static unsigned short g_msgId = 0;`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### unchecked_malloc (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:150`
- **描述**: 内存分配结果未检查
- **代码**: `sndPktBuff.readWriteBuf = calloc(1, COAP_MAX_PDU_SIZE);`
- **建议**: 检查返回值: if ((ptr = malloc(size)) == NULL) { handle_error(); }

### unchecked_malloc (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:182`
- **描述**: 内存分配结果未检查
- **代码**: `newBuf = (uint8_t *)calloc(1, size + 1);`
- **建议**: 检查返回值: if ((ptr = malloc(size)) == NULL) { handle_error(); }

### unchecked_malloc (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:235`
- **描述**: 内存分配结果未检查
- **代码**: `unsigned char *recvBuffer = calloc(1, COAP_MAX_PDU_SIZE + 1);`
- **建议**: 检查返回值: if ((ptr = malloc(size)) == NULL) { handle_error(); }

### unchecked_addition (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:182`
- **描述**: 内存分配中使用加法可能导致整数溢出
- **代码**: `newBuf = (uint8_t *)calloc(1, size + 1);`
- **建议**: 检查加法溢出: if (size1 > SIZE_MAX - size2) { handle_error(); }

### unchecked_addition (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:235`
- **描述**: 内存分配中使用加法可能导致整数溢出
- **代码**: `unsigned char *recvBuffer = calloc(1, COAP_MAX_PDU_SIZE + 1);`
- **建议**: 检查加法溢出: if (size1 > SIZE_MAX - size2) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:7`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `*    http://www.apache.org/licenses/LICENSE-2.0`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:25`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `#include "lwip/sockets.h"`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:26`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `#include "lwip/netif.h"`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:27`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `#include "lwip/netifapi.h"`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:32`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `#include <arpa/inet.h>`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:33`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `#include <net/if.h>`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:34`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `#include <netinet/in.h>`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:36`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `#include <sys/ioctl.h>`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:37`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `#include <sys/select.h>`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:38`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `#include <sys/socket.h>`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:39`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `#include <sys/types.h>`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:43`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `#include "common/wpa_ctrl.h"`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### unchecked_array_access (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:494`
- **描述**: 数组访问可能越界（无边界检查）
- **代码**: `info->ip[0] = '\0';`
- **建议**: 添加边界检查: if (index < sizeof(arr)/sizeof(arr[0]))

### unchecked_array_access (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:591`
- **描述**: 数组访问可能越界（无边界检查）
- **代码**: `char reply[REPLY_LENGTH] = {0};`
- **建议**: 添加边界检查: if (index < sizeof(arr)/sizeof(arr[0]))

### unchecked_array_access (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:800`
- **描述**: 数组访问可能越界（无边界检查）
- **代码**: `if (ip[pos] == '1' && ip[pos - 1] == '.') {`
- **建议**: 添加边界检查: if (index < sizeof(arr)/sizeof(arr[0]))

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:57`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `unsigned int g_wifiTaskStart = 0;`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:71`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `unsigned int g_terminalFlag = 0;`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:85`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `unsigned int g_updateIpFlag = 0;`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:156`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `sndPktBuff.len = 0;`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:300`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `g_queryIpFlag = 0;`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:330`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `g_wifiTaskStart = 0;`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:673`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `g_updateIpFlag = 0;`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:705`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `g_terminalFlag = 0;`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:717`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `g_terminalFlag = 0;`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:727`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `g_terminalFlag = 0;`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_socket.c:7`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `* http://www.apache.org/licenses/LICENSE-2.0`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\json_payload.c:7`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `* http://www.apache.org/licenses/LICENSE-2.0`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\json_payload.c:26`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `#include <arpa/inet.h>`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### unchecked_array_access (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\json_payload.c:91`
- **描述**: 数组访问可能越界（无边界检查）
- **代码**: `char ipString[INET_ADDRSTRLEN] = {0};`
- **建议**: 添加边界检查: if (index < sizeof(arr)/sizeof(arr[0]))

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\json_payload.c:125`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `for (i = 0; i < deviceInfo->capabilityBitmapNum; i++) {`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\json_payload.c:238`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `uint32_t capabilityBitmapNum = 0;`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\nstackx_common.c:7`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `*    http://www.apache.org/licenses/LICENSE-2.0`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\nstackx_device.c:7`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `*    http://www.apache.org/licenses/LICENSE-2.0`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### unchecked_array_access (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\nstackx_device.c:31`
- **描述**: 数组访问可能越界（无边界检查）
- **代码**: `static char g_networkType[NETWORKTYPE_LENGTH] = {0};`
- **建议**: 添加边界检查: if (index < sizeof(arr)/sizeof(arr[0]))

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\nstackx_device.c:90`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `for (i = 0; i < NSTACKX_MAX_INTERFACE_NUM; i++) {`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\auth_conn.c:7`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `*    http://www.apache.org/licenses/LICENSE-2.0`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\auth_conn.c:142`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `int bufLen = 0;`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### unchecked_malloc (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\auth_interface.c:37`
- **描述**: 内存分配结果未检查
- **代码**: `g_authSessionMap = (AuthSession *)malloc(len);`
- **建议**: 检查返回值: if ((ptr = malloc(size)) == NULL) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\auth_interface.c:7`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `*    http://www.apache.org/licenses/LICENSE-2.0`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\auth_interface.c:51`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `for (int i = 0; i < AUTH_SESSION_MAX_NUM; i++) {`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\auth_interface.c:70`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `for (int i = 0; i < AUTH_SESSION_MAX_NUM; i++) {`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\auth_interface.c:89`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `for (int i = 0; i < AUTH_SESSION_MAX_NUM; i++) {`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\auth_interface.c:92`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `g_authSessionMap[i].isUsed = 0;`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\auth_interface.c:106`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `for (int i = 0; i < AUTH_SESSION_MAX_NUM; i++) {`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\bus_manager.c:7`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `*    http://www.apache.org/licenses/LICENSE-2.0`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\bus_manager.c:26`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `static int g_busStartFlag = 0;`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\bus_manager.c:98`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `g_busStartFlag = 0;`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\msg_get_deviceid.c:7`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `*    http://www.apache.org/licenses/LICENSE-2.0`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### unchecked_malloc (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\wifi_auth_manager.c:392`
- **描述**: 内存分配结果未检查
- **代码**: `char *buf = malloc(bufLen);`
- **建议**: 检查返回值: if ((ptr = malloc(size)) == NULL) { handle_error(); }

### unchecked_malloc (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\wifi_auth_manager.c:431`
- **描述**: 内存分配结果未检查
- **代码**: `unsigned char *output = malloc(len);`
- **建议**: 检查返回值: if ((ptr = malloc(size)) == NULL) { handle_error(); }

### unchecked_malloc (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\wifi_auth_manager.c:585`
- **描述**: 内存分配结果未检查
- **代码**: `conn->db.buf = (char *)malloc(DEFAULT_BUF_SIZE);`
- **建议**: 检查返回值: if ((ptr = malloc(size)) == NULL) { handle_error(); }

### divide_by_zero (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\wifi_auth_manager.c:7`
- **描述**: 除法操作未检查除数是否为零
- **代码**: `*    http://www.apache.org/licenses/LICENSE-2.0`
- **建议**: 检查除数: if (divisor == 0) { handle_error(); }

### unchecked_array_access (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\wifi_auth_manager.c:36`
- **描述**: 数组访问可能越界（无边界检查）
- **代码**: `char g_peerAuthId[MAX_AUTH_ID_LEN] = {0};`
- **建议**: 添加边界检查: if (index < sizeof(arr)/sizeof(arr[0]))

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\wifi_auth_manager.c:382`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `int val = 0;`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\wifi_auth_manager.c:488`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `int val = 0;`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\wifi_auth_manager.c:522`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `long long seq = 0;`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\wifi_auth_manager.c:550`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `int processed = 0;`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### potential_memory_leak (MEDIUM)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\wifi_auth_manager.c:591`
- **描述**: 指针被覆盖为零，可能导致内存泄漏
- **代码**: `conn->db.used = 0;`
- **建议**: 在覆盖指针前确保已释放内存: free(ptr); ptr = NULL;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\include\utils\aes_gcm.h:28`
- **描述**: 变量声明后未初始化
- **代码**: `unsigned int keybits;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\interfaces\kits\discovery\discovery_service.h:98`
- **描述**: 变量声明后未初始化
- **代码**: `int publishId;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\interfaces\kits\discovery\discovery_service.h:100`
- **描述**: 变量声明后未初始化
- **代码**: `int mode;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\interfaces\kits\discovery\discovery_service.h:110`
- **描述**: 变量声明后未初始化
- **代码**: `unsigned int dataLen;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\include\common_info_manager.h:58`
- **描述**: 变量声明后未初始化
- **代码**: `int deviceType;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\include\common_info_manager.h:59`
- **描述**: 变量声明后未初始化
- **代码**: `int devicePort;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\include\common_info_manager.h:61`
- **描述**: 变量声明后未初始化
- **代码**: `int isAccountTrusted;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\include\common_info_manager.h:68`
- **描述**: 变量声明后未初始化
- **代码**: `int deviceType;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\include\coap_adapter.h:25`
- **描述**: 变量声明后未初始化
- **代码**: `unsigned char code;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\include\coap_adapter.h:26`
- **描述**: 变量声明后未初始化
- **代码**: `unsigned short msgId;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\include\coap_adapter.h:28`
- **描述**: 变量声明后未初始化
- **代码**: `unsigned char optionsNum;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\include\coap_adapter.h:38`
- **描述**: 变量声明后未初始化
- **代码**: `unsigned int len;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\include\coap_adapter.h:39`
- **描述**: 变量声明后未初始化
- **代码**: `unsigned int size;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\include\coap_def.h:52`
- **描述**: 变量声明后未初始化
- **代码**: `unsigned short msgLen;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\include\coap_def.h:53`
- **描述**: 变量声明后未初始化
- **代码**: `unsigned short msgId;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\include\coap_def.h:59`
- **描述**: 变量声明后未初始化
- **代码**: `unsigned int len;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\include\coap_def.h:63`
- **描述**: 变量声明后未初始化
- **代码**: `unsigned short num;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\include\coap_def.h:65`
- **描述**: 变量声明后未初始化
- **代码**: `unsigned int len;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\include\coap_def.h:70`
- **描述**: 变量声明后未初始化
- **代码**: `unsigned int len;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\include\coap_def.h:73`
- **描述**: 变量声明后未初始化
- **代码**: `unsigned char optionsNum;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\include\coap_socket.h:26`
- **描述**: 变量声明后未初始化
- **代码**: `int cliendFd;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\include\nstackx.h:64`
- **描述**: 变量声明后未初始化
- **代码**: `int deviceType;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\include\nstackx_device.h:51`
- **描述**: 变量声明后未初始化
- **代码**: `int deviceType;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\include\auth_conn.h:55`
- **描述**: 变量声明后未初始化
- **代码**: `int size;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\include\auth_conn.h:56`
- **描述**: 变量声明后未初始化
- **代码**: `int used;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\include\auth_conn.h:60`
- **描述**: 变量声明后未初始化
- **代码**: `int fd;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\include\auth_conn.h:64`
- **描述**: 变量声明后未初始化
- **代码**: `int busVersion;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\include\auth_conn.h:65`
- **描述**: 变量声明后未初始化
- **代码**: `int authPort;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\include\auth_conn.h:66`
- **描述**: 变量声明后未初始化
- **代码**: `int sessionPort;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\include\auth_conn.h:67`
- **描述**: 变量声明后未初始化
- **代码**: `int authState;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\include\auth_conn.h:68`
- **描述**: 变量声明后未初始化
- **代码**: `int onlineState;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\include\auth_conn.h:78`
- **描述**: 变量声明后未初始化
- **代码**: `int maxVersion;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\include\auth_conn.h:79`
- **描述**: 变量声明后未初始化
- **代码**: `int minVersion;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\include\auth_interface.h:29`
- **描述**: 变量声明后未初始化
- **代码**: `int index;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\include\auth_interface.h:30`
- **描述**: 变量声明后未初始化
- **代码**: `int fd;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\include\auth_interface.h:39`
- **描述**: 变量声明后未初始化
- **代码**: `int isUsed;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\include\auth_interface.h:40`
- **描述**: 变量声明后未初始化
- **代码**: `long long seqId;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\include\wifi_auth_manager.h:33`
- **描述**: 变量声明后未初始化
- **代码**: `int module;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\include\wifi_auth_manager.h:34`
- **描述**: 变量声明后未初始化
- **代码**: `int flags;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\include\wifi_auth_manager.h:35`
- **描述**: 变量声明后未初始化
- **代码**: `long long seq;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\include\wifi_auth_manager.h:36`
- **描述**: 变量声明后未初始化
- **代码**: `int dataLen;`
- **建议**: 声明时初始化: int x = 0;

### integer_underflow_in_assignment (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\source\utils\aes_gcm.c:95`
- **描述**: 整数减法可能导致下溢
- **代码**: `int ret = mbedtls_gcm_setkey(&g_aesContext, MBEDTLS_CIPHER_ID_AES, cipherkey->key, cipherkey->keybits);`
- **建议**: 确保减法结果非负: if (a < b) { result = 0; } else { result = a - b; }

### integer_underflow_in_assignment (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\source\utils\aes_gcm.c:102`
- **描述**: 整数减法可能导致下溢
- **代码**: `int actualPlainLen = cipherTextSize - OVERHEAD_LEN;`
- **建议**: 确保减法结果非负: if (a < b) { result = 0; } else { result = a - b; }

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\source\utils\aes_gcm.c:54`
- **描述**: 变量声明后未初始化
- **代码**: `int ret;`
- **建议**: 声明时初始化: int x = 0;

### multiple_free_in_scope (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\source\utils\aes_gcm.c:39`
- **描述**: 检测到 free 调用，需检查是否存在双重释放风险
- **代码**: `free(randomIv);`
- **建议**: 确保每个指针只被释放一次，建议释放后置为 NULL: ptr = NULL;

### multiple_free_in_scope (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\source\utils\aes_gcm.c:60`
- **描述**: 检测到 free 调用，需检查是否存在双重释放风险
- **代码**: `mbedtls_gcm_free(&g_aesContext);`
- **建议**: 确保每个指针只被释放一次，建议释放后置为 NULL: ptr = NULL;

### multiple_free_in_scope (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\source\utils\aes_gcm.c:67`
- **描述**: 检测到 free 调用，需检查是否存在双重释放风险
- **代码**: `mbedtls_gcm_free(&g_aesContext);`
- **建议**: 确保每个指针只被释放一次，建议释放后置为 NULL: ptr = NULL;

### multiple_free_in_scope (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\source\utils\aes_gcm.c:72`
- **描述**: 检测到 free 调用，需检查是否存在双重释放风险
- **代码**: `mbedtls_gcm_free(&g_aesContext);`
- **建议**: 确保每个指针只被释放一次，建议释放后置为 NULL: ptr = NULL;

### multiple_free_in_scope (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\source\utils\aes_gcm.c:77`
- **描述**: 检测到 free 调用，需检查是否存在双重释放风险
- **代码**: `mbedtls_gcm_free(&g_aesContext);`
- **建议**: 确保每个指针只被释放一次，建议释放后置为 NULL: ptr = NULL;

### multiple_free_in_scope (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\source\utils\aes_gcm.c:81`
- **描述**: 检测到 free 调用，需检查是否存在双重释放风险
- **代码**: `mbedtls_gcm_free(&g_aesContext);`
- **建议**: 确保每个指针只被释放一次，建议释放后置为 NULL: ptr = NULL;

### multiple_free_in_scope (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\source\utils\aes_gcm.c:98`
- **描述**: 检测到 free 调用，需检查是否存在双重释放风险
- **代码**: `mbedtls_gcm_free(&g_aesContext);`
- **建议**: 确保每个指针只被释放一次，建议释放后置为 NULL: ptr = NULL;

### multiple_free_in_scope (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\source\utils\aes_gcm.c:107`
- **描述**: 检测到 free 调用，需检查是否存在双重释放风险
- **代码**: `mbedtls_gcm_free(&g_aesContext);`
- **建议**: 确保每个指针只被释放一次，建议释放后置为 NULL: ptr = NULL;

### multiple_free_in_scope (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\source\utils\aes_gcm.c:111`
- **描述**: 检测到 free 调用，需检查是否存在双重释放风险
- **代码**: `mbedtls_gcm_free(&g_aesContext);`
- **建议**: 确保每个指针只被释放一次，建议释放后置为 NULL: ptr = NULL;

### pointer_assignment_after_free_risk (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\source\utils\aes_gcm.c:39`
- **描述**: 内存释放操作，需检查后续是否存在释放后使用风险
- **代码**: `free(randomIv);`
- **建议**: 释放后立即将指针置为 NULL，避免释放后使用

### pointer_assignment_after_free_risk (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\source\utils\aes_gcm.c:60`
- **描述**: 内存释放操作，需检查后续是否存在释放后使用风险
- **代码**: `mbedtls_gcm_free(&g_aesContext);`
- **建议**: 释放后立即将指针置为 NULL，避免释放后使用

### pointer_assignment_after_free_risk (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\source\utils\aes_gcm.c:67`
- **描述**: 内存释放操作，需检查后续是否存在释放后使用风险
- **代码**: `mbedtls_gcm_free(&g_aesContext);`
- **建议**: 释放后立即将指针置为 NULL，避免释放后使用

### pointer_assignment_after_free_risk (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\source\utils\aes_gcm.c:72`
- **描述**: 内存释放操作，需检查后续是否存在释放后使用风险
- **代码**: `mbedtls_gcm_free(&g_aesContext);`
- **建议**: 释放后立即将指针置为 NULL，避免释放后使用

### pointer_assignment_after_free_risk (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\source\utils\aes_gcm.c:77`
- **描述**: 内存释放操作，需检查后续是否存在释放后使用风险
- **代码**: `mbedtls_gcm_free(&g_aesContext);`
- **建议**: 释放后立即将指针置为 NULL，避免释放后使用

### pointer_assignment_after_free_risk (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\source\utils\aes_gcm.c:81`
- **描述**: 内存释放操作，需检查后续是否存在释放后使用风险
- **代码**: `mbedtls_gcm_free(&g_aesContext);`
- **建议**: 释放后立即将指针置为 NULL，避免释放后使用

### pointer_assignment_after_free_risk (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\source\utils\aes_gcm.c:98`
- **描述**: 内存释放操作，需检查后续是否存在释放后使用风险
- **代码**: `mbedtls_gcm_free(&g_aesContext);`
- **建议**: 释放后立即将指针置为 NULL，避免释放后使用

### pointer_assignment_after_free_risk (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\source\utils\aes_gcm.c:107`
- **描述**: 内存释放操作，需检查后续是否存在释放后使用风险
- **代码**: `mbedtls_gcm_free(&g_aesContext);`
- **建议**: 释放后立即将指针置为 NULL，避免释放后使用

### pointer_assignment_after_free_risk (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\source\utils\aes_gcm.c:111`
- **描述**: 内存释放操作，需检查后续是否存在释放后使用风险
- **代码**: `mbedtls_gcm_free(&g_aesContext);`
- **建议**: 释放后立即将指针置为 NULL，避免释放后使用

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\coap_service.c:43`
- **描述**: 变量声明后未初始化
- **代码**: `unsigned int ret;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\coap_service.c:63`
- **描述**: 变量声明后未初始化
- **代码**: `int ret;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\common_info_manager.c:106`
- **描述**: 变量声明后未初始化
- **代码**: `int ret;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\common_info_manager.c:156`
- **描述**: 变量声明后未初始化
- **代码**: `int ret;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\common_info_manager.c:157`
- **描述**: 变量声明后未初始化
- **代码**: `int fd;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\common_info_manager.c:196`
- **描述**: 变量声明后未初始化
- **代码**: `int ret;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\common_info_manager.c:240`
- **描述**: 变量声明后未初始化
- **代码**: `unsigned int ret;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\common_info_manager.c:299`
- **描述**: 变量声明后未初始化
- **代码**: `unsigned int ret;`
- **建议**: 声明时初始化: int x = 0;

### multiple_free_in_scope (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\common_info_manager.c:336`
- **描述**: 检测到 free 调用，需检查是否存在双重释放风险
- **代码**: `free(g_deviceInfo);`
- **建议**: 确保每个指针只被释放一次，建议释放后置为 NULL: ptr = NULL;

### pointer_assignment_after_free_risk (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\common_info_manager.c:336`
- **描述**: 内存释放操作，需检查后续是否存在释放后使用风险
- **代码**: `free(g_deviceInfo);`
- **建议**: 释放后立即将指针置为 NULL，避免释放后使用

### integer_underflow_in_assignment (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\discovery_service.c:70`
- **描述**: 整数减法可能导致下溢
- **代码**: `int ret = strcpy_s(info->deviceId, MAX_DEV_ID_LEN, devInfo->deviceId);`
- **建议**: 确保减法结果非负: if (a < b) { result = 0; } else { result = a - b; }

### integer_underflow_in_assignment (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\discovery_service.c:91`
- **描述**: 整数减法可能导致下溢
- **代码**: `int ret = strcpy_s(info->deviceId, MAX_DEV_ID_LEN, devInfo->deviceId);`
- **建议**: 确保减法结果非负: if (a < b) { result = 0; } else { result = a - b; }

### integer_underflow_in_assignment (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\discovery_service.c:402`
- **描述**: 整数减法可能导致下溢
- **代码**: `int ret = sprintf_s(capabilityData, dataLen, "port:%d,", local->devicePort);`
- **建议**: 确保减法结果非负: if (a < b) { result = 0; } else { result = a - b; }

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\discovery_service.c:27`
- **描述**: 变量声明后未初始化
- **代码**: `int publishId;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\discovery_service.c:28`
- **描述**: 变量声明后未初始化
- **代码**: `unsigned short medium;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\discovery_service.c:29`
- **描述**: 变量声明后未初始化
- **代码**: `unsigned short capabilityBitmap;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\discovery_service.c:31`
- **描述**: 变量声明后未初始化
- **代码**: `unsigned short dataLength;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\discovery_service.c:32`
- **描述**: 变量声明后未初始化
- **代码**: `unsigned short used;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\discovery_service.c:38`
- **描述**: 变量声明后未初始化
- **代码**: `int  deviceType;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\discovery_service.c:119`
- **描述**: 变量声明后未初始化
- **代码**: `int ret;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\discovery_service.c:120`
- **描述**: 变量声明后未初始化
- **代码**: `int devType;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\discovery_service.c:165`
- **描述**: 变量声明后未初始化
- **代码**: `int ret;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\discovery_service.c:351`
- **描述**: 变量声明后未初始化
- **代码**: `int ret;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\discovery_service.c:475`
- **描述**: 变量声明后未初始化
- **代码**: `int ret;`
- **建议**: 声明时初始化: int x = 0;

### multiple_free_in_scope (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\discovery_service.c:206`
- **描述**: 检测到 free 调用，需检查是否存在双重释放风险
- **代码**: `free(g_publishModule);`
- **建议**: 确保每个指针只被释放一次，建议释放后置为 NULL: ptr = NULL;

### multiple_free_in_scope (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\discovery_service.c:211`
- **描述**: 检测到 free 调用，需检查是否存在双重释放风险
- **代码**: `free(g_capabilityData);`
- **建议**: 确保每个指针只被释放一次，建议释放后置为 NULL: ptr = NULL;

### multiple_free_in_scope (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\discovery_service.c:372`
- **描述**: 检测到 free 调用，需检查是否存在双重释放风险
- **代码**: `free(g_publishModule[i].capabilityData);`
- **建议**: 确保每个指针只被释放一次，建议释放后置为 NULL: ptr = NULL;

### multiple_free_in_scope (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\discovery_service.c:381`
- **描述**: 检测到 free 调用，需检查是否存在双重释放风险
- **代码**: `free(g_publishModule[i].capabilityData);`
- **建议**: 确保每个指针只被释放一次，建议释放后置为 NULL: ptr = NULL;

### multiple_free_in_scope (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\discovery_service.c:449`
- **描述**: 检测到 free 调用，需检查是否存在双重释放风险
- **代码**: `free(findModule->capabilityData);`
- **建议**: 确保每个指针只被释放一次，建议释放后置为 NULL: ptr = NULL;

### multiple_free_in_scope (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\discovery_service.c:569`
- **描述**: 检测到 free 调用，需检查是否存在双重释放风险
- **代码**: `free(findModule->capabilityData);`
- **建议**: 确保每个指针只被释放一次，建议释放后置为 NULL: ptr = NULL;

### pointer_assignment_after_free_risk (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\discovery_service.c:206`
- **描述**: 内存释放操作，需检查后续是否存在释放后使用风险
- **代码**: `free(g_publishModule);`
- **建议**: 释放后立即将指针置为 NULL，避免释放后使用

### pointer_assignment_after_free_risk (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\discovery_service.c:211`
- **描述**: 内存释放操作，需检查后续是否存在释放后使用风险
- **代码**: `free(g_capabilityData);`
- **建议**: 释放后立即将指针置为 NULL，避免释放后使用

### pointer_assignment_after_free_risk (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\discovery_service.c:288`
- **描述**: 内存释放操作，需检查后续是否存在释放后使用风险
- **代码**: `unsigned int IsAllModuleFree(void)`
- **建议**: 释放后立即将指针置为 NULL，避免释放后使用

### pointer_assignment_after_free_risk (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\discovery_service.c:372`
- **描述**: 内存释放操作，需检查后续是否存在释放后使用风险
- **代码**: `free(g_publishModule[i].capabilityData);`
- **建议**: 释放后立即将指针置为 NULL，避免释放后使用

### pointer_assignment_after_free_risk (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\discovery_service.c:381`
- **描述**: 内存释放操作，需检查后续是否存在释放后使用风险
- **代码**: `free(g_publishModule[i].capabilityData);`
- **建议**: 释放后立即将指针置为 NULL，避免释放后使用

### pointer_assignment_after_free_risk (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\discovery_service.c:449`
- **描述**: 内存释放操作，需检查后续是否存在释放后使用风险
- **代码**: `free(findModule->capabilityData);`
- **建议**: 释放后立即将指针置为 NULL，避免释放后使用

### pointer_assignment_after_free_risk (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\discovery_service\source\discovery_service.c:569`
- **描述**: 内存释放操作，需检查后续是否存在释放后使用风险
- **代码**: `free(findModule->capabilityData);`
- **建议**: 释放后立即将指针置为 NULL，避免释放后使用

### integer_underflow_in_assignment (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_adapter.c:124`
- **描述**: 整数减法可能导致下溢
- **代码**: `int ret = COAP_ParseOption(&((pkt->options)[optionIndex]), &delta, &dataPos, end - dataPos);`
- **建议**: 确保减法结果非负: if (a < b) { result = 0; } else { result = a - b; }

### integer_underflow_in_assignment (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_adapter.c:605`
- **描述**: 整数减法可能导致下溢
- **代码**: `unsigned int len = sndPktBuff->size;`
- **建议**: 确保减法结果非负: if (a < b) { result = 0; } else { result = a - b; }

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_adapter.c:76`
- **描述**: 变量声明后未初始化
- **代码**: `unsigned char headLen;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_adapter.c:77`
- **描述**: 变量声明后未初始化
- **代码**: `unsigned short len;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_adapter.c:78`
- **描述**: 变量声明后未初始化
- **代码**: `unsigned short delta;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_adapter.c:79`
- **描述**: 变量声明后未初始化
- **代码**: `int ret;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_adapter.c:167`
- **描述**: 变量声明后未初始化
- **代码**: `int ret;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_adapter.c:326`
- **描述**: 变量声明后未初始化
- **代码**: `unsigned short optionLen;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_adapter.c:355`
- **描述**: 变量声明后未初始化
- **代码**: `unsigned char delta;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_adapter.c:356`
- **描述**: 变量声明后未初始化
- **代码**: `unsigned char len;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_adapter.c:357`
- **描述**: 变量声明后未初始化
- **代码**: `unsigned short optionDelta;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_adapter.c:358`
- **描述**: 变量声明后未初始化
- **代码**: `unsigned short prevOptionNum;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_adapter.c:448`
- **描述**: 变量声明后未初始化
- **代码**: `int i;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_adapter.c:449`
- **描述**: 变量声明后未初始化
- **代码**: `int ret;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_adapter.c:484`
- **描述**: 变量声明后未初始化
- **代码**: `int ret;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_adapter.c:528`
- **描述**: 变量声明后未初始化
- **代码**: `unsigned long payloadLen;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_adapter.c:547`
- **描述**: 变量声明后未初始化
- **代码**: `int ret;`
- **建议**: 声明时初始化: int x = 0;

### integer_underflow_in_assignment (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:55`
- **描述**: 整数减法可能导致下溢
- **代码**: `int g_wifiQueueId = -1;`
- **建议**: 确保减法结果非负: if (a < b) { result = 0; } else { result = a - b; }

### integer_underflow_in_assignment (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:56`
- **描述**: 整数减法可能导致下溢
- **代码**: `int g_queryIpFlag = -1;`
- **建议**: 确保减法结果非负: if (a < b) { result = 0; } else { result = a - b; }

### integer_underflow_in_assignment (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:799`
- **描述**: 整数减法可能导致下溢
- **代码**: `int pos = length - 1;`
- **建议**: 确保减法结果非负: if (a < b) { result = 0; } else { result = a - b; }

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:66`
- **描述**: 变量声明后未初始化
- **代码**: `size_t dataLength;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:139`
- **描述**: 变量声明后未初始化
- **代码**: `int ret;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:262`
- **描述**: 变量声明后未初始化
- **代码**: `int ret;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:312`
- **描述**: 变量声明后未初始化
- **代码**: `unsigned int readSize;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:313`
- **描述**: 变量声明后未初始化
- **代码**: `unsigned int ret;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:329`
- **描述**: 变量声明后未初始化
- **代码**: `unsigned int ret;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:389`
- **描述**: 变量声明后未初始化
- **代码**: `int ret;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:408`
- **描述**: 变量声明后未初始化
- **代码**: `unsigned int ret;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:443`
- **描述**: 变量声明后未初始化
- **代码**: `int ret;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:470`
- **描述**: 变量声明后未初始化
- **代码**: `int flag;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:605`
- **描述**: 变量声明后未初始化
- **代码**: `int status;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:641`
- **描述**: 变量声明后未初始化
- **代码**: `int updateFlag;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:642`
- **描述**: 变量声明后未初始化
- **代码**: `int prevFlag;`
- **建议**: 声明时初始化: int x = 0;

### multiple_free_in_scope (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:152`
- **描述**: 检测到 free 调用，需检查是否存在双重释放风险
- **代码**: `free(payload);`
- **建议**: 确保每个指针只被释放一次，建议释放后置为 NULL: ptr = NULL;

### multiple_free_in_scope (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:159`
- **描述**: 检测到 free 调用，需检查是否存在双重释放风险
- **代码**: `free(payload);`
- **建议**: 确保每个指针只被释放一次，建议释放后置为 NULL: ptr = NULL;

### multiple_free_in_scope (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:161`
- **描述**: 检测到 free 调用，需检查是否存在双重释放风险
- **代码**: `free(sndPktBuff.readWriteBuf);`
- **建议**: 确保每个指针只被释放一次，建议释放后置为 NULL: ptr = NULL;

### multiple_free_in_scope (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:168`
- **描述**: 检测到 free 调用，需检查是否存在双重释放风险
- **代码**: `free(sndPktBuff.readWriteBuf);`
- **建议**: 确保每个指针只被释放一次，建议释放后置为 NULL: ptr = NULL;

### multiple_free_in_scope (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:197`
- **描述**: 检测到 free 调用，需检查是否存在双重释放风险
- **代码**: `free(newBuf);`
- **建议**: 确保每个指针只被释放一次，建议释放后置为 NULL: ptr = NULL;

### multiple_free_in_scope (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:203`
- **描述**: 检测到 free 调用，需检查是否存在双重释放风险
- **代码**: `free(newBuf);`
- **建议**: 确保每个指针只被释放一次，建议释放后置为 NULL: ptr = NULL;

### multiple_free_in_scope (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:228`
- **描述**: 检测到 free 调用，需检查是否存在双重释放风险
- **代码**: `free(remoteUrl);`
- **建议**: 确保每个指针只被释放一次，建议释放后置为 NULL: ptr = NULL;

### multiple_free_in_scope (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:243`
- **描述**: 检测到 free 调用，需检查是否存在双重释放风险
- **代码**: `free(recvBuffer);`
- **建议**: 确保每个指针只被释放一次，建议释放后置为 NULL: ptr = NULL;

### multiple_free_in_scope (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:252`
- **描述**: 检测到 free 调用，需检查是否存在双重释放风险
- **代码**: `free(recvBuffer);`
- **建议**: 确保每个指针只被释放一次，建议释放后置为 NULL: ptr = NULL;

### pointer_assignment_after_free_risk (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:152`
- **描述**: 内存释放操作，需检查后续是否存在释放后使用风险
- **代码**: `free(payload);`
- **建议**: 释放后立即将指针置为 NULL，避免释放后使用

### pointer_assignment_after_free_risk (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:159`
- **描述**: 内存释放操作，需检查后续是否存在释放后使用风险
- **代码**: `free(payload);`
- **建议**: 释放后立即将指针置为 NULL，避免释放后使用

### pointer_assignment_after_free_risk (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:161`
- **描述**: 内存释放操作，需检查后续是否存在释放后使用风险
- **代码**: `free(sndPktBuff.readWriteBuf);`
- **建议**: 释放后立即将指针置为 NULL，避免释放后使用

### pointer_assignment_after_free_risk (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:168`
- **描述**: 内存释放操作，需检查后续是否存在释放后使用风险
- **代码**: `free(sndPktBuff.readWriteBuf);`
- **建议**: 释放后立即将指针置为 NULL，避免释放后使用

### pointer_assignment_after_free_risk (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:197`
- **描述**: 内存释放操作，需检查后续是否存在释放后使用风险
- **代码**: `free(newBuf);`
- **建议**: 释放后立即将指针置为 NULL，避免释放后使用

### pointer_assignment_after_free_risk (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:203`
- **描述**: 内存释放操作，需检查后续是否存在释放后使用风险
- **代码**: `free(newBuf);`
- **建议**: 释放后立即将指针置为 NULL，避免释放后使用

### pointer_assignment_after_free_risk (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:228`
- **描述**: 内存释放操作，需检查后续是否存在释放后使用风险
- **代码**: `free(remoteUrl);`
- **建议**: 释放后立即将指针置为 NULL，避免释放后使用

### pointer_assignment_after_free_risk (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:243`
- **描述**: 内存释放操作，需检查后续是否存在释放后使用风险
- **代码**: `free(recvBuffer);`
- **建议**: 释放后立即将指针置为 NULL，避免释放后使用

### pointer_assignment_after_free_risk (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_discover.c:252`
- **描述**: 内存释放操作，需检查后续是否存在释放后使用风险
- **代码**: `free(recvBuffer);`
- **建议**: 释放后立即将指针置为 NULL，避免释放后使用

### integer_underflow_in_assignment (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_socket.c:22`
- **描述**: 整数减法可能导致下溢
- **代码**: `int g_serverFd = -1;`
- **建议**: 确保减法结果非负: if (a < b) { result = 0; } else { result = a - b; }

### integer_underflow_in_assignment (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_socket.c:23`
- **描述**: 整数减法可能导致下溢
- **代码**: `int g_clientFd = -1;`
- **建议**: 确保减法结果非负: if (a < b) { result = 0; } else { result = a - b; }

### integer_underflow_in_assignment (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\coap_socket.c:132`
- **描述**: 整数减法可能导致下溢
- **代码**: `int ret = sendto(socket->cliendFd, buffer, length, 0, (struct sockaddr *)&socket->dstAddr, dstAddrLen);`
- **建议**: 确保减法结果非负: if (a < b) { result = 0; } else { result = a - b; }

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\nstackx_common.c:34`
- **描述**: 变量声明后未初始化
- **代码**: `int ret;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\discovery\coap\source\nstackx_device.c:81`
- **描述**: 变量声明后未初始化
- **代码**: `int ret;`
- **建议**: 声明时初始化: int x = 0;

### integer_overflow_in_assignment (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\auth_conn.c:97`
- **描述**: 整数加法可能导致溢出
- **代码**: `int dataLen = isCipherText ? (strlen(str) + MESSAGE_ENCRYPT_OVER_HEAD_LEN) : strlen(str);`
- **建议**: 检查加法溢出: if (a > INT_MAX - b) { handle_error(); }

### integer_overflow_in_assignment (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\auth_conn.c:98`
- **描述**: 整数加法可能导致溢出
- **代码**: `int len = dataLen + PACKET_HEAD_SIZE;`
- **建议**: 检查加法溢出: if (a > INT_MAX - b) { handle_error(); }

### integer_underflow_in_assignment (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\auth_conn.c:69`
- **描述**: 整数减法可能导致下溢
- **代码**: `int ret = memcpy_s(cipherKey.key, SESSION_KEY_LENGTH, skey->key, AUTH_SESSION_KEY_LEN);`
- **建议**: 确保减法结果非负: if (a < b) { result = 0; } else { result = a - b; }

### multiple_free_in_scope (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\auth_conn.c:75`
- **描述**: 检测到 free 调用，需检查是否存在双重释放风险
- **代码**: `free(randomIv);`
- **建议**: 确保每个指针只被释放一次，建议释放后置为 NULL: ptr = NULL;

### multiple_free_in_scope (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\auth_conn.c:117`
- **描述**: 检测到 free 调用，需检查是否存在双重释放风险
- **代码**: `free(buf);`
- **建议**: 确保每个指针只被释放一次，建议释放后置为 NULL: ptr = NULL;

### multiple_free_in_scope (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\auth_conn.c:123`
- **描述**: 检测到 free 调用，需检查是否存在双重释放风险
- **代码**: `free(buf);`
- **建议**: 确保每个指针只被释放一次，建议释放后置为 NULL: ptr = NULL;

### multiple_free_in_scope (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\auth_conn.c:128`
- **描述**: 检测到 free 调用，需检查是否存在双重释放风险
- **代码**: `free(buf);`
- **建议**: 确保每个指针只被释放一次，建议释放后置为 NULL: ptr = NULL;

### multiple_free_in_scope (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\auth_conn.c:148`
- **描述**: 检测到 free 调用，需检查是否存在双重释放风险
- **代码**: `free(buf);`
- **建议**: 确保每个指针只被释放一次，建议释放后置为 NULL: ptr = NULL;

### multiple_free_in_scope (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\auth_conn.c:171`
- **描述**: 检测到 free 调用，需检查是否存在双重释放风险
- **代码**: `free(msgStr);`
- **建议**: 确保每个指针只被释放一次，建议释放后置为 NULL: ptr = NULL;

### pointer_assignment_after_free_risk (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\auth_conn.c:75`
- **描述**: 内存释放操作，需检查后续是否存在释放后使用风险
- **代码**: `free(randomIv);`
- **建议**: 释放后立即将指针置为 NULL，避免释放后使用

### pointer_assignment_after_free_risk (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\auth_conn.c:117`
- **描述**: 内存释放操作，需检查后续是否存在释放后使用风险
- **代码**: `free(buf);`
- **建议**: 释放后立即将指针置为 NULL，避免释放后使用

### pointer_assignment_after_free_risk (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\auth_conn.c:123`
- **描述**: 内存释放操作，需检查后续是否存在释放后使用风险
- **代码**: `free(buf);`
- **建议**: 释放后立即将指针置为 NULL，避免释放后使用

### pointer_assignment_after_free_risk (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\auth_conn.c:128`
- **描述**: 内存释放操作，需检查后续是否存在释放后使用风险
- **代码**: `free(buf);`
- **建议**: 释放后立即将指针置为 NULL，避免释放后使用

### pointer_assignment_after_free_risk (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\auth_conn.c:148`
- **描述**: 内存释放操作，需检查后续是否存在释放后使用风险
- **代码**: `free(buf);`
- **建议**: 释放后立即将指针置为 NULL，避免释放后使用

### pointer_assignment_after_free_risk (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\auth_conn.c:171`
- **描述**: 内存释放操作，需检查后续是否存在释放后使用风险
- **代码**: `free(msgStr);`
- **建议**: 释放后立即将指针置为 NULL，避免释放后使用

### integer_underflow_in_assignment (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\auth_interface.c:128`
- **描述**: 整数减法可能导致下溢
- **代码**: `int ret = AuthConnPostBytes(auth->conn->fd, module, 0, auth->seqId, data);`
- **建议**: 确保减法结果非负: if (a < b) { result = 0; } else { result = a - b; }

### integer_underflow_in_assignment (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\auth_interface.c:144`
- **描述**: 整数减法可能导致下溢
- **代码**: `int ret = AuthSendData(identity->session_id, MODULE_AUTH_SDK, data);`
- **建议**: 确保减法结果非负: if (a < b) { result = 0; } else { result = a - b; }

### integer_underflow_in_assignment (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\auth_interface.c:254`
- **描述**: 整数减法可能导致下溢
- **代码**: `int ret = memcpy_s(node->sKey.key, sizeof(node->sKey.key), session->session_key, session->length);`
- **建议**: 确保减法结果非负: if (a < b) { result = 0; } else { result = a - b; }

### integer_underflow_in_assignment (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\auth_interface.c:275`
- **描述**: 整数减法可能导致下溢
- **代码**: `int ret = memcpy_s(node->sKey.key, sizeof(node->sKey.key), session->session_key, session->length);`
- **建议**: 确保减法结果非负: if (a < b) { result = 0; } else { result = a - b; }

### integer_underflow_in_assignment (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\auth_interface.c:302`
- **描述**: 整数减法可能导致下溢
- **代码**: `int index = (int)auth->seqId;`
- **建议**: 确保减法结果非负: if (a < b) { result = 0; } else { result = a - b; }

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\auth_interface.c:301`
- **描述**: 变量声明后未初始化
- **代码**: `int ret;`
- **建议**: 声明时初始化: int x = 0;

### multiple_free_in_scope (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\auth_interface.c:210`
- **描述**: 检测到 free 调用，需检查是否存在双重释放风险
- **代码**: `free(node);`
- **建议**: 确保每个指针只被释放一次，建议释放后置为 NULL: ptr = NULL;

### multiple_free_in_scope (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\auth_interface.c:238`
- **描述**: 检测到 free 调用，需检查是否存在双重释放风险
- **代码**: `free(node);`
- **建议**: 确保每个指针只被释放一次，建议释放后置为 NULL: ptr = NULL;

### multiple_free_in_scope (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\auth_interface.c:256`
- **描述**: 检测到 free 调用，需检查是否存在双重释放风险
- **代码**: `free(node);`
- **建议**: 确保每个指针只被释放一次，建议释放后置为 NULL: ptr = NULL;

### multiple_free_in_scope (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\auth_interface.c:277`
- **描述**: 检测到 free 调用，需检查是否存在双重释放风险
- **代码**: `free(node);`
- **建议**: 确保每个指针只被释放一次，建议释放后置为 NULL: ptr = NULL;

### pointer_assignment_after_free_risk (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\auth_interface.c:210`
- **描述**: 内存释放操作，需检查后续是否存在释放后使用风险
- **代码**: `free(node);`
- **建议**: 释放后立即将指针置为 NULL，避免释放后使用

### pointer_assignment_after_free_risk (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\auth_interface.c:238`
- **描述**: 内存释放操作，需检查后续是否存在释放后使用风险
- **代码**: `free(node);`
- **建议**: 释放后立即将指针置为 NULL，避免释放后使用

### pointer_assignment_after_free_risk (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\auth_interface.c:256`
- **描述**: 内存释放操作，需检查后续是否存在释放后使用风险
- **代码**: `free(node);`
- **建议**: 释放后立即将指针置为 NULL，避免释放后使用

### pointer_assignment_after_free_risk (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\auth_interface.c:277`
- **描述**: 内存释放操作，需检查后续是否存在释放后使用风险
- **代码**: `free(node);`
- **建议**: 释放后立即将指针置为 NULL，避免释放后使用

### integer_underflow_in_assignment (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\bus_manager.c:58`
- **描述**: 整数减法可能导致下溢
- **代码**: `int authPort = StartListener(&g_baseLister, info->deviceIp);`
- **建议**: 确保减法结果非负: if (a < b) { result = 0; } else { result = a - b; }

### integer_underflow_in_assignment (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\bus_manager.c:65`
- **描述**: 整数减法可能导致下溢
- **代码**: `int sessionPort = StartSession(info->deviceIp);`
- **建议**: 确保减法结果非负: if (a < b) { result = 0; } else { result = a - b; }

### integer_underflow_in_assignment (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\msg_get_deviceid.c:164`
- **描述**: 整数减法可能导致下溢
- **代码**: `int connMaxVersion = connInfo->maxVersion;`
- **建议**: 确保减法结果非负: if (a < b) { result = 0; } else { result = a - b; }

### integer_underflow_in_assignment (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\msg_get_deviceid.c:165`
- **描述**: 整数减法可能导致下溢
- **代码**: `int connMinVersion = connInfo->minVersion;`
- **建议**: 确保减法结果非负: if (a < b) { result = 0; } else { result = a - b; }

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\msg_get_deviceid.c:154`
- **描述**: 变量声明后未初始化
- **代码**: `int maxVersion;`
- **建议**: 声明时初始化: int x = 0;

### uninitialized_variable (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\msg_get_deviceid.c:159`
- **描述**: 变量声明后未初始化
- **代码**: `int minVersion;`
- **建议**: 声明时初始化: int x = 0;

### integer_overflow_in_assignment (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\wifi_auth_manager.c:391`
- **描述**: 整数加法可能导致溢出
- **代码**: `unsigned int bufLen = dataLen + 1;`
- **建议**: 检查加法溢出: if (a > INT_MAX - b) { handle_error(); }

### integer_overflow_in_assignment (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\wifi_auth_manager.c:430`
- **描述**: 整数加法可能导致溢出
- **代码**: `unsigned int len = dataLen - MESSAGE_ENCRYPT_OVER_HEAD_LEN + 1;`
- **建议**: 检查加法溢出: if (a > INT_MAX - b) { handle_error(); }

### integer_underflow_in_assignment (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\wifi_auth_manager.c:31`
- **描述**: 整数减法可能导致下溢
- **代码**: `static int g_authPort = -1;`
- **建议**: 确保减法结果非负: if (a < b) { result = 0; } else { result = a - b; }

### integer_underflow_in_assignment (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\wifi_auth_manager.c:32`
- **描述**: 整数减法可能导致下溢
- **代码**: `static int g_sessionPort = -1;`
- **建议**: 确保减法结果非负: if (a < b) { result = 0; } else { result = a - b; }

### integer_underflow_in_assignment (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\wifi_auth_manager.c:210`
- **描述**: 整数减法可能导致下溢
- **代码**: `int ret = strcpy_s(aconn->deviceIp, sizeof(aconn->deviceIp), ip);`
- **建议**: 确保减法结果非负: if (a < b) { result = 0; } else { result = a - b; }

### integer_underflow_in_assignment (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\wifi_auth_manager.c:307`
- **描述**: 整数减法可能导致下溢
- **代码**: `int code = codeJson->valueint;`
- **建议**: 确保减法结果非负: if (a < b) { result = 0; } else { result = a - b; }

### integer_underflow_in_assignment (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\wifi_auth_manager.c:430`
- **描述**: 整数减法可能导致下溢
- **代码**: `unsigned int len = dataLen - MESSAGE_ENCRYPT_OVER_HEAD_LEN + 1;`
- **建议**: 确保减法结果非负: if (a < b) { result = 0; } else { result = a - b; }

### integer_underflow_in_assignment (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\wifi_auth_manager.c:443`
- **描述**: 整数减法可能导致下溢
- **代码**: `int ret = memcpy_s(cipherKey.key, SESSION_KEY_LENGTH, sKey->key, AUTH_SESSION_KEY_LEN);`
- **建议**: 确保减法结果非负: if (a < b) { result = 0; } else { result = a - b; }

### integer_underflow_in_assignment (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\wifi_auth_manager.c:558`
- **描述**: 整数减法可能导致下溢
- **代码**: `int len = pkt->dataLen;`
- **建议**: 确保减法结果非负: if (a < b) { result = 0; } else { result = a - b; }

### integer_underflow_in_assignment (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\wifi_auth_manager.c:596`
- **描述**: 整数减法可能导致下溢
- **代码**: `int used = db->used;`
- **建议**: 确保减法结果非负: if (a < b) { result = 0; } else { result = a - b; }

### integer_underflow_in_assignment (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\wifi_auth_manager.c:597`
- **描述**: 整数减法可能导致下溢
- **代码**: `int size = db->size;`
- **建议**: 确保减法结果非负: if (a < b) { result = 0; } else { result = a - b; }

### integer_underflow_in_assignment (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\wifi_auth_manager.c:599`
- **描述**: 整数减法可能导致下溢
- **代码**: `int rc = AuthConnRecv(fd, buf, used, size - used, 0);`
- **建议**: 确保减法结果非负: if (a < b) { result = 0; } else { result = a - b; }

### multiple_free_in_scope (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\wifi_auth_manager.c:141`
- **描述**: 检测到 free 调用，需检查是否存在双重释放风险
- **代码**: `free(buf);`
- **建议**: 确保每个指针只被释放一次，建议释放后置为 NULL: ptr = NULL;

### multiple_free_in_scope (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\wifi_auth_manager.c:146`
- **描述**: 检测到 free 调用，需检查是否存在双重释放风险
- **代码**: `free(node->aconn);`
- **建议**: 确保每个指针只被释放一次，建议释放后置为 NULL: ptr = NULL;

### multiple_free_in_scope (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\wifi_auth_manager.c:150`
- **描述**: 检测到 free 调用，需检查是否存在双重释放风险
- **代码**: `free(node);`
- **建议**: 确保每个指针只被释放一次，建议释放后置为 NULL: ptr = NULL;

### multiple_free_in_scope (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\wifi_auth_manager.c:212`
- **描述**: 检测到 free 调用，需检查是否存在双重释放风险
- **代码**: `free(aconn);`
- **建议**: 确保每个指针只被释放一次，建议释放后置为 NULL: ptr = NULL;

### multiple_free_in_scope (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\wifi_auth_manager.c:221`
- **描述**: 检测到 free 调用，需检查是否存在双重释放风险
- **代码**: `free(aconn);`
- **建议**: 确保每个指针只被释放一次，建议释放后置为 NULL: ptr = NULL;

### multiple_free_in_scope (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\wifi_auth_manager.c:397`
- **描述**: 检测到 free 调用，需检查是否存在双重释放风险
- **代码**: `free(buf);`
- **建议**: 确保每个指针只被释放一次，建议释放后置为 NULL: ptr = NULL;

### multiple_free_in_scope (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\wifi_auth_manager.c:401`
- **描述**: 检测到 free 调用，需检查是否存在双重释放风险
- **代码**: `free(buf);`
- **建议**: 确保每个指针只被释放一次，建议释放后置为 NULL: ptr = NULL;

### multiple_free_in_scope (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\wifi_auth_manager.c:406`
- **描述**: 检测到 free 调用，需检查是否存在双重释放风险
- **代码**: `free(buf);`
- **建议**: 确保每个指针只被释放一次，建议释放后置为 NULL: ptr = NULL;

### multiple_free_in_scope (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\wifi_auth_manager.c:436`
- **描述**: 检测到 free 调用，需检查是否存在双重释放风险
- **代码**: `free(output);`
- **建议**: 确保每个指针只被释放一次，建议释放后置为 NULL: ptr = NULL;

### multiple_free_in_scope (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\wifi_auth_manager.c:446`
- **描述**: 检测到 free 调用，需检查是否存在双重释放风险
- **代码**: `free(output);`
- **建议**: 确保每个指针只被释放一次，建议释放后置为 NULL: ptr = NULL;

### multiple_free_in_scope (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\wifi_auth_manager.c:455`
- **描述**: 检测到 free 调用，需检查是否存在双重释放风险
- **代码**: `free(output);`
- **建议**: 确保每个指针只被释放一次，建议释放后置为 NULL: ptr = NULL;

### multiple_free_in_scope (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\wifi_auth_manager.c:461`
- **描述**: 检测到 free 调用，需检查是否存在双重释放风险
- **代码**: `free(output);`
- **建议**: 确保每个指针只被释放一次，建议释放后置为 NULL: ptr = NULL;

### multiple_free_in_scope (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\wifi_auth_manager.c:560`
- **描述**: 检测到 free 调用，需检查是否存在双重释放风险
- **代码**: `free(pkt);`
- **建议**: 确保每个指针只被释放一次，建议释放后置为 NULL: ptr = NULL;

### multiple_free_in_scope (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\wifi_auth_manager.c:568`
- **描述**: 检测到 free 调用，需检查是否存在双重释放风险
- **代码**: `free(pkt);`
- **建议**: 确保每个指针只被释放一次，建议释放后置为 NULL: ptr = NULL;

### pointer_assignment_after_free_risk (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\wifi_auth_manager.c:141`
- **描述**: 内存释放操作，需检查后续是否存在释放后使用风险
- **代码**: `free(buf);`
- **建议**: 释放后立即将指针置为 NULL，避免释放后使用

### pointer_assignment_after_free_risk (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\wifi_auth_manager.c:146`
- **描述**: 内存释放操作，需检查后续是否存在释放后使用风险
- **代码**: `free(node->aconn);`
- **建议**: 释放后立即将指针置为 NULL，避免释放后使用

### pointer_assignment_after_free_risk (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\wifi_auth_manager.c:150`
- **描述**: 内存释放操作，需检查后续是否存在释放后使用风险
- **代码**: `free(node);`
- **建议**: 释放后立即将指针置为 NULL，避免释放后使用

### pointer_assignment_after_free_risk (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\wifi_auth_manager.c:212`
- **描述**: 内存释放操作，需检查后续是否存在释放后使用风险
- **代码**: `free(aconn);`
- **建议**: 释放后立即将指针置为 NULL，避免释放后使用

### pointer_assignment_after_free_risk (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\wifi_auth_manager.c:221`
- **描述**: 内存释放操作，需检查后续是否存在释放后使用风险
- **代码**: `free(aconn);`
- **建议**: 释放后立即将指针置为 NULL，避免释放后使用

### pointer_assignment_after_free_risk (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\wifi_auth_manager.c:397`
- **描述**: 内存释放操作，需检查后续是否存在释放后使用风险
- **代码**: `free(buf);`
- **建议**: 释放后立即将指针置为 NULL，避免释放后使用

### pointer_assignment_after_free_risk (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\wifi_auth_manager.c:401`
- **描述**: 内存释放操作，需检查后续是否存在释放后使用风险
- **代码**: `free(buf);`
- **建议**: 释放后立即将指针置为 NULL，避免释放后使用

### pointer_assignment_after_free_risk (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\wifi_auth_manager.c:406`
- **描述**: 内存释放操作，需检查后续是否存在释放后使用风险
- **代码**: `free(buf);`
- **建议**: 释放后立即将指针置为 NULL，避免释放后使用

### pointer_assignment_after_free_risk (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\wifi_auth_manager.c:436`
- **描述**: 内存释放操作，需检查后续是否存在释放后使用风险
- **代码**: `free(output);`
- **建议**: 释放后立即将指针置为 NULL，避免释放后使用

### pointer_assignment_after_free_risk (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\wifi_auth_manager.c:446`
- **描述**: 内存释放操作，需检查后续是否存在释放后使用风险
- **代码**: `free(output);`
- **建议**: 释放后立即将指针置为 NULL，避免释放后使用

### pointer_assignment_after_free_risk (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\wifi_auth_manager.c:455`
- **描述**: 内存释放操作，需检查后续是否存在释放后使用风险
- **代码**: `free(output);`
- **建议**: 释放后立即将指针置为 NULL，避免释放后使用

### pointer_assignment_after_free_risk (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\wifi_auth_manager.c:461`
- **描述**: 内存释放操作，需检查后续是否存在释放后使用风险
- **代码**: `free(output);`
- **建议**: 释放后立即将指针置为 NULL，避免释放后使用

### pointer_assignment_after_free_risk (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\wifi_auth_manager.c:560`
- **描述**: 内存释放操作，需检查后续是否存在释放后使用风险
- **代码**: `free(pkt);`
- **建议**: 释放后立即将指针置为 NULL，避免释放后使用

### pointer_assignment_after_free_risk (LOW)
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\authmanager\source\wifi_auth_manager.c:568`
- **描述**: 内存释放操作，需检查后续是否存在释放后使用风险
- **代码**: `free(pkt);`
- **建议**: 释放后立即将指针置为 NULL，避免释放后使用

## Level 2 AI 检查建议区域

以下区域需要 AI 进行深度上下文分析：

### pointer_usage
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\include\utils\aes_gcm.h:2`
- **说明**: 指针解引用区域（需要 AI 检查空指针、野指针）
- **代码**: `* Copyright (c) 2020 Huawei Device Co., Ltd.`

### pointer_usage
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\include\utils\aes_gcm.h:3`
- **说明**: 指针解引用区域（需要 AI 检查空指针、野指针）
- **代码**: `* Licensed under the Apache License, Version 2.0 (the "License");`

### pointer_usage
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\include\utils\aes_gcm.h:4`
- **说明**: 指针解引用区域（需要 AI 检查空指针、野指针）
- **代码**: `* you may not use this file except in compliance with the License.`

### pointer_usage
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\include\utils\aes_gcm.h:5`
- **说明**: 指针解引用区域（需要 AI 检查空指针、野指针）
- **代码**: `* You may obtain a copy of the License at`

### pointer_usage
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\include\utils\aes_gcm.h:7`
- **说明**: 指针解引用区域（需要 AI 检查空指针、野指针）
- **代码**: `*    http://www.apache.org/licenses/LICENSE-2.0`

### pointer_usage
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\include\utils\aes_gcm.h:9`
- **说明**: 指针解引用区域（需要 AI 检查空指针、野指针）
- **代码**: `* Unless required by applicable law or agreed to in writing, software`

### pointer_usage
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\include\utils\aes_gcm.h:10`
- **说明**: 指针解引用区域（需要 AI 检查空指针、野指针）
- **代码**: `* distributed under the License is distributed on an "AS IS" BASIS,`

### pointer_usage
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\include\utils\aes_gcm.h:11`
- **说明**: 指针解引用区域（需要 AI 检查空指针、野指针）
- **代码**: `* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.`

### pointer_usage
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\include\utils\aes_gcm.h:12`
- **说明**: 指针解引用区域（需要 AI 检查空指针、野指针）
- **代码**: `* See the License for the specific language governing permissions and`

### pointer_usage
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\include\utils\aes_gcm.h:13`
- **说明**: 指针解引用区域（需要 AI 检查空指针、野指针）
- **代码**: `* limitations under the License.`

### pointer_usage
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\include\utils\aes_gcm.h:33`
- **说明**: 指针解引用区域（需要 AI 检查空指针、野指针）
- **代码**: `unsigned char* GenerateRandomIv(void);`

### pointer_usage
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\include\utils\aes_gcm.h:34`
- **说明**: 指针解引用区域（需要 AI 检查空指针、野指针）
- **代码**: `int EncryptTransData(const AesGcmCipherKey *cipherkey, const unsigned char* plainText, unsigned int `

### pointer_usage
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\include\utils\aes_gcm.h:35`
- **说明**: 指针解引用区域（需要 AI 检查空指针、野指针）
- **代码**: `unsigned char* cipherText, unsigned int cipherTextLen);`

### pointer_usage
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\include\utils\aes_gcm.h:36`
- **说明**: 指针解引用区域（需要 AI 检查空指针、野指针）
- **代码**: `int DecryptTransData(const AesGcmCipherKey *cipherkey, const unsigned char* cipherText, unsigned int`

### pointer_usage
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\include\utils\aes_gcm.h:37`
- **说明**: 指针解引用区域（需要 AI 检查空指针、野指针）
- **代码**: `unsigned char* plain, unsigned int plainLen);`

### pointer_usage
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\include\utils\comm_defs.h:2`
- **说明**: 指针解引用区域（需要 AI 检查空指针、野指针）
- **代码**: `* Copyright (c) 2020 Huawei Device Co., Ltd.`

### pointer_usage
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\include\utils\comm_defs.h:3`
- **说明**: 指针解引用区域（需要 AI 检查空指针、野指针）
- **代码**: `* Licensed under the Apache License, Version 2.0 (the "License");`

### pointer_usage
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\include\utils\comm_defs.h:4`
- **说明**: 指针解引用区域（需要 AI 检查空指针、野指针）
- **代码**: `* you may not use this file except in compliance with the License.`

### pointer_usage
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\include\utils\comm_defs.h:5`
- **说明**: 指针解引用区域（需要 AI 检查空指针、野指针）
- **代码**: `* You may obtain a copy of the License at`

### pointer_usage
- **文件**: `C:\Users\zhd\AppData\Local\Temp\communication_softbus_lite\trans_service\include\utils\comm_defs.h:7`
- **说明**: 指针解引用区域（需要 AI 检查空指针、野指针）
- **代码**: `*    http://www.apache.org/licenses/LICENSE-2.0`

## 修复建议汇总

### Level 1 快速修复

| 原函数 | 安全替代 | 风险 |
|--------|----------|------|
| strcpy | strncpy | 缓冲区溢出 |
| strcat | strncat | 缓冲区溢出 |
| sprintf | snprintf | 缓冲区溢出 |
| gets | fgets | 无限制输入 |
| scanf | scanf with limit | 格式问题 |
| system | execve | 命令注入 |

### Level 2 检查要点

- [ ] 检查所有 malloc/free 配对
- [ ] 验证指针使用前的有效性
- [ ] 确认并发代码的锁使用
- [ ] 审查文件操作的 TOCTOU 风险

