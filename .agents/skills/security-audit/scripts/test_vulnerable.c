#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>

// 硬编码密钥 - 应该被 Level 1 检测到
char *API_KEY = "sk-1234567890abcdef";
char password[] = "admin123";

// 危险函数使用示例
void unsafe_string_ops() {
    char buffer[100];
    char input[256];

    // CRITICAL: gets 使用
    gets(input);

    // HIGH: strcpy 无长度检查
    strcpy(buffer, input);

    // HIGH: strcat 可能导致溢出
    strcat(buffer, " suffix");

    // HIGH: sprintf 无边界
    sprintf(buffer, "Result: %s", input);
}

// 格式化字符串漏洞
void format_string_vuln(char *user_input) {
    // HIGH: 用户输入作为格式字符串
    printf(user_input);
}

// 命令注入风险
void command_injection(char *hostname) {
    char cmd[256];
    // HIGH: system 调用
    sprintf(cmd, "ping -c 1 %s", hostname);
    system(cmd);
}

// 内存管理问题 - 需要 Level 2 AI 检查
void *global_ptr = NULL;

void memory_issues() {
    char *ptr = malloc(100);
    // 未检查 malloc 返回值

    // 可能的双重释放（需要 AI 分析控制流）
    if (some_condition()) {
        free(ptr);
    }

    // use-after-free 风险（需要 AI 分析）
    if (another_condition()) {
        strcpy(ptr, "data");  // 可能已释放
    }

    free(ptr);
}

// 并发问题 - 需要 Level 2 AI 检查
pthread_mutex_t mutex;
int shared_counter = 0;

void *thread_func(void *arg) {
    // 复杂的锁使用模式，需要 AI 分析是否有死锁
    pthread_mutex_lock(&mutex);
    shared_counter++;

    // 可能调用其他函数，需要检查锁传递
    some_other_function();

    pthread_mutex_unlock(&mutex);
    return NULL;
}

// TOCTOU 风险 - 需要 Level 2 AI 检查
void file_race_condition(char *filename) {
    // 检查文件存在
    if (access(filename, F_OK) == 0) {
        // TOCTOU: 检查时和使用时之间可能被替换
        FILE *fp = fopen(filename, "r");
        if (fp) {
            // 读取文件
            fclose(fp);
        }
    }
}

// 未检查输入
void unchecked_input() {
    char buf[100];
    // HIGH: scanf %s 无长度限制
    scanf("%s", buf);
}

// 辅助函数占位符
int some_condition() { return 0; }
int another_condition() { return 0; }
void some_other_function() {}

int main(int argc, char *argv[]) {
    unsafe_string_ops();
    format_string_vuln(argv[1]);
    command_injection(argv[2]);
    memory_issues();

    pthread_t thread;
    pthread_create(&thread, NULL, thread_func, NULL);
    pthread_join(thread, NULL);

    return 0;
}
