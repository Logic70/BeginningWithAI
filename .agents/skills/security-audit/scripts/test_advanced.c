#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

// 整数溢出测试
void* integer_overflow(size_t nmemb, size_t size) {
    // 危险：乘法可能溢出
    void *ptr = malloc(nmemb * size);
    return ptr;
}

// 无符号/有符号混用
void unsigned_signed_issue() {
    size_t len = -1;  // 危险：size_t 赋负值
    char buf[100];
    strncpy(buf, "test", len);  // 会复制大量数据
}

// 返回局部变量地址
char* dangling_pointer() {
    char local[100] = "local data";
    return local;  // 危险：返回局部变量地址
}

// 未初始化变量
void uninitialized_use() {
    int x;
    printf("%d\n", x);  // 危险：使用未初始化变量
}

// 数组越界访问
void unchecked_array_access() {
    int arr[10];
    int index = 20;
    arr[index] = 100;  // 危险：越界写入
}

// strncpy 不保证终止符
void strncpy_without_null() {
    char dest[10];
    strncpy(dest, "hello world", 10);  // dest[9] 可能不是 '\0'
    printf("%s", dest);  // 可能读取越界
}

// 危险函数组合
void dangerous_combo() {
    char buf[100];
    gets(buf);  // CRITICAL
    strcpy(buf, "test");  // HIGH
    sprintf(buf, "%s", "test");  // HIGH
}

// 格式化字符串
void format_vuln(char *user_input) {
    printf(user_input);  // HIGH: 用户控制格式字符串
}

int main() {
    integer_overflow(1000000, 1000000);
    unsigned_signed_issue();
    dangling_pointer();
    uninitialized_use();
    unchecked_array_access();
    strncpy_without_null();
    dangerous_combo();
    format_vuln("%s%s%s%s%s%s%s%s");
    return 0;
}
