#pragma once
#include "Logger.h"

// For LOG_DEBUG, LOG_INFO, LOG_WARN, LOG_ERROR, pass variadic arguments correctly to logf
#define LOG_DEBUG(fmt, ...) logger::Logger::getInstance().logf(logger::Logger::Level::DEBUG, fmt, ##__VA_ARGS__)
#define LOG_INFO(fmt, ...)  logger::Logger::getInstance().logf(logger::Logger::Level::INFO, fmt, ##__VA_ARGS__)
#define LOG_WARN(fmt, ...)  logger::Logger::getInstance().logf(logger::Logger::Level::WARNING, fmt, ##__VA_ARGS__)
#define LOG_ERROR(fmt, ...) logger::Logger::getInstance().logf(logger::Logger::Level::ERROR, fmt, ##__VA_ARGS__)
