#include <chrono>
#include <ctime>
#include <iomanip>
#include <iostream>
#include "Logger.h"

namespace logger
{
    Logger::Logger() {}

    Logger& Logger::getInstance()
    {
        static Logger instance;
        return instance;
    }

    void Logger::setLogFile(const std::string& filename)
    {
        std::lock_guard<std::mutex> lock(logMutex);
        logFile.open(filename, std::ios::app);
    }

    void Logger::log(const std::string& message, Level level)
    {
        std::lock_guard<std::mutex> lock(logMutex);
        std::string time = getTimestamp();
        std::string levelStr = levelToString(level);
        std::string fullMessage = "[" + time + "][" + levelStr + "] " + message;

        if (logFile.is_open())
        {
            logFile << fullMessage << std::endl;
        }
        else
        {
            std::cout << fullMessage << std::endl;
        }
    }

    std::string Logger::getTimestamp()
    {
        auto now = std::chrono::system_clock::now();
        auto in_time_t = std::chrono::system_clock::to_time_t(now);
        std::tm buf;
#ifdef _WIN32
        localtime_s(&buf, &in_time_t);
#else
        localtime_r(&in_time_t, &buf);
#endif
        std::ostringstream ss;
        ss << std::put_time(&buf, "%Y-%m-%d %H:%M:%S");
        return ss.str();
    }

    std::string Logger::levelToString(Level level)
    {
        switch (level)
        {
        case Level::INFO:
            return "INFO";
        case Level::WARNING:
            return "WARNING";
        case Level::ERROR:
            return "ERROR";
        case Level::DEBUG:
            return "DEBUG";
        default:
            return "UNKNOWN";
        }
    }
} // namespace logger
