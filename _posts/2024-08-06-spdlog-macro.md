
---
layout: post
title: 给spdlog增加打印宏
categories: [language]
tags: [spdlog]
---

抄自trpc

<!-- more -->


```c++
inline void InitSpdLog() {
  bool truncate = true;
  auto max_files = 5;
  auto log_name = "xxxlog_dir" + "/" + "INFO.%Y-%m-%d.log";
  auto default_logger =
      spdlog::daily_logger_format_mt("xxxlog", log_name, 12, 0, truncate, max_files);
  default_logger->set_level(spdlog::level::info);
}


#define MODULE_NAME_FMT(instance, level, formats, ...)            \
  do {                                                          \
    spdlog::get(instance)->level(formats, ##__VA_ARGS__); \
  } while (0)

#define MODULE_NAME_IF(instance, condition, level, formats, ...) \
  if (condition) {                                             \
    LOG_FMT(instance, level, formats, ##__VA_ARGS__);               \
  }

#define LOGGER_FMT_TRACE(instance, format, args...) MODULE_NAME_FMT(instance, trace, format, ##args)
#define LOGGER_FMT_DEBUG(instance, format, args...) MODULE_NAME_FMT(instance, debug, format, ##args)
#define LOGGER_FMT_INFO(instance, format, args...) MODULE_NAME_FMT(instance, info, format, ##args)
#define LOGGER_FMT_WARN(instance, format, args...) MODULE_NAME_FMT(instance, warn, format, ##args)
#define LOGGER_FMT_ERROR(instance, format, args...) MODULE_NAME_FMT(instance, error, format, ##args)
#define LOGGER_FMT_CRITICAL(instance, format, args...) MODULE_NAME_FMT(instance, critical, format, ##args)

#define MODULE_NAME_TRACE(format, args...) LOGGER_FMT_TRACE(FLAGS_default_logger, format, ##args)
#define MODULE_NAME_DEBUG(format, args...) LOGGER_FMT_DEBUG(FLAGS_default_logger, format, ##args)
#define MODULE_NAME_INFO(format, args...) LOGGER_FMT_INFO(FLAGS_default_logger, format, ##args)
#define MODULE_NAME_WARN(format, args...) LOGGER_FMT_WARN(FLAGS_default_logger, format, ##args)
#define MODULE_NAME_ERROR(format, args...) LOGGER_FMT_ERROR(FLAGS_default_logger, format, ##args)
#define MODULE_NAME_CRITICAL(format, args...) LOGGER_FMT_CRITICAL(FLAGS_default_logger, format, ##args)

#define LOGGER_FMT_TRACE_IF(instance, condition, format, args...) \
  MODULE_NAME_IF(instance, condition, trace, format, ##args)
#define LOGGER_FMT_DEBUG_IF(instance, condition, format, args...) \
  MODULE_NAME_IF(instance, condition, debug, format, ##args)
#define LOGGER_FMT_INFO_IF(instance, condition, format, args...) \
  MODULE_NAME_IF(instance, condition, info, format, ##args)
#define LOGGER_FMT_WARN_IF(instance, condition, format, args...) \
  MODULE_NAME_IF(instance, condition, warn, format, ##args)
#define LOGGER_FMT_ERROR_IF(instance, condition, format, args...) \
  MODULE_NAME_IF(instance, condition, error, format, ##args)
#define LOGGER_FMT_CRITICAL_IF(instance, condition, format, args...) \
  MODULE_NAME_IF(instance, condition, critical, format, ##args)

#define MODULE_NAME_TRACE_IF(condition, format, args...) \
  LOGGER_FMT_TRACE_IF(FLAGS_default_logger, condition, format, ##args)
#define MODULE_NAME_DEBUG_IF(condition, format, args...) \
  LOGGER_FMT_DEBUG_IF(FLAGS_default_logger, condition, format, ##args)
#define MODULE_NAME_INFO_IF(condition, format, args...) \
  LOGGER_FMT_INFO_IF(FLAGS_default_logger, condition, format, ##args)
#define MODULE_NAME_WARN_IF(condition, format, args...) \
  LOGGER_FMT_WARN_IF(FLAGS_default_logger, condition, format, ##args)
#define MODULE_NAME_ERROR_IF(condition, format, args...) \
  LOGGER_FMT_ERROR_IF(FLAGS_default_logger, condition, format, ##args)
#define MODULE_NAME_CRITICAL_IF(condition, format, args...) \
  LOGGER_FMT_CRITICAL_IF(FLAGS_default_logger, condition, format, ##args)

#define MODULE_NAME_ASSERT(x)                             \
  do {                                              \
    if (__builtin_expect(!(x), 0)) {                \
      [&]() __attribute__((noinline, cold)) {       \
        MODULE_NAME_CRITICAL("assertion failed: {}", #x); \
        std::abort();                               \
      }                                             \
      ();                                           \
      __builtin_unreachable();                      \
    }                                               \
  } while (0)

#define MODULE_NAME_ONCE()                                               \
  ({                                                               \
    static std::atomic_flag __MODULE_NAME_LOG_FLAG__ = ATOMIC_FLAG_INIT; \
    (!__MODULE_NAME_LOG_FLAG__.test_and_set(std::memory_order_relaxed)); \
  })

#define MODULE_NAME_EVERY_N(n)                                                            \
  ({                                                                                \
    MODULE_NAME_ASSERT((n) > 0 && "should not be less than 1");                           \
    static std::atomic<uint64_t> __MODULE_NAME_LOG_OCCURENCE_N__{(n)};                    \
    (__MODULE_NAME_LOG_OCCURENCE_N__.fetch_add(1, std::memory_order_relaxed) % (n) == 0); \
  })

#define MODULE_NAME_WITHIN_N(ms)                                                              \
  ({                                                                                    \
    MODULE_NAME_ASSERT((ms) > 0 && "should not be less than 1");                              \
    bool __MODULE_NAME_LOG_WRITEABLE__ = false;                                               \
    static std::chrono::time_point<std::chrono::steady_clock> __MODULE_NAME_TIME_POINT__;     \
    static std::atomic_flag __MODULE_NAME_LOG_CONDITION_FLAG__ = ATOMIC_FLAG_INIT;            \
    if (!__MODULE_NAME_LOG_CONDITION_FLAG__.test_and_set(std::memory_order_acquire)) {        \
      auto __MODULE_NAME_NOWS__ = std::chrono::steady_clock::now();                           \
      int64_t __MODULE_NAME_DIFF_N__ = std::chrono::duration_cast<std::chrono::milliseconds>( \
                                     __MODULE_NAME_NOWS__ - __MODULE_NAME_TIME_POINT__)             \
                                     .count();                                          \
      if (__MODULE_NAME_DIFF_N__ > ms) {                                                      \
        __MODULE_NAME_TIME_POINT__ = __MODULE_NAME_NOWS__;                                          \
        __MODULE_NAME_LOG_WRITEABLE__ = true;                                                 \
      }                                                                                 \
      __MODULE_NAME_LOG_CONDITION_FLAG__.clear(std::memory_order_release);                    \
    }                                                                                   \
    __MODULE_NAME_LOG_WRITEABLE__;                                                            \
  })

#define MODULE_NAME_INFO_ONCE(format, args...) MODULE_NAME_INFO_IF(MODULE_NAME_ONCE(), format, ##args)
#define MODULE_NAME_WARN_ONCE(format, args...) MODULE_NAME_WARN_IF(MODULE_NAME_ONCE(), format, ##args)
#define MODULE_NAME_ERROR_ONCE(format, args...) MODULE_NAME_ERROR_IF(MODULE_NAME_ONCE(), format, ##args)
#define MODULE_NAME_CRITICAL_ONCE(format, args...) MODULE_NAME_CRITICAL_IF(MODULE_NAME_ONCE(), format, ##args)

#define MODULE_NAME_INFO_EVERY_N(N, format, args...) MODULE_NAME_INFO_IF(MODULE_NAME_EVERY_N(N), format, ##args)
#define MODULE_NAME_WARN_EVERY_N(N, format, args...) MODULE_NAME_WARN_IF(MODULE_NAME_EVERY_N(N), format, ##args)
#define MODULE_NAME_ERROR_EVERY_N(N, format, args...) MODULE_NAME_ERROR_IF(MODULE_NAME_EVERY_N(N), format, ##args)
#define MODULE_NAME_CRITICAL_EVERY_N(N, format, args...) \
  MODULE_NAME_CRITICAL_IF(MODULE_NAME_EVERY_N(N), format, ##args)

#define MODULE_NAME_INFO_EVERY_SECOND(format, args...) MODULE_NAME_INFO_IF(MODULE_NAME_WITHIN_N(1000), format, ##args)
#define MODULE_NAME_WARN_EVERY_SECOND(format, args...) MODULE_NAME_WARN_IF(MODULE_NAME_WITHIN_N(1000), format, ##args)
#define MODULE_NAME_ERROR_EVERY_SECOND(format, args...) \
  MODULE_NAME_ERROR_IF(MODULE_NAME_WITHIN_N(1000), format, ##args)
#define MODULE_NAME_CRITICAL_EVERY_SECOND(format, args...) \
  MODULE_NAME_CRITICAL_IF(MODULE_NAME_WITHIN_N(1000), format, ##args)
```