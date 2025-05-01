#pragma once
#include <string>
#include <fstream>
#include <mutex>

#define FMT_HEADER_ONLY
#include <fmt/core.h>

namespace logger
{
    class Logger
    {
    public:
        enum class Level
        {
            INFO,
            WARNING,
            ERROR,
            DEBUG
        };

        static Logger& getInstance();
        void log(const std::string& message, Level level = Level::INFO);

        template<typename... Args>
        void logf(Level level, fmt::format_string<Args...> formatStr, Args&&... args)
        {
            std::string message = fmt::format(formatStr, std::forward<Args>(args)...);
            log(message, level);
        }


        void setLogFile(const std::string& filename);

    private:
        Logger();
        std::ofstream logFile;
        std::mutex logMutex;
        std::string getTimestamp();
        std::string levelToString(Level level);
    };
} // namespace logger
