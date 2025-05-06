project(Backtester)
cmake_minimum_required(VERSION 3.20)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

if (MSVC)
    add_compile_options("/utf-8")
endif()

include_directories(include)


file(GLOB SOURCES "src/*.cpp")


# Set venv path
set(VENV_PATH "${CMAKE_SOURCE_DIR}/DataDownloader/DataDownloaderEnv")

# Ensure Python interpreter is from venv
set(PYTHON_EXECUTABLE "${VENV_PATH}/Scripts/python.exe") # Windows


# Enable Python3 support
find_package(Python3 COMPONENTS Interpreter Development REQUIRED)

include_directories(${Python3_INCLUDE_DIRS})

add_compile_definitions(
    DATA_DOWNLOADER_PATH="${CMAKE_SOURCE_DIR}/DataDownloader"
)


# Debug Output - Verify Interpreter
execute_process(COMMAND ${PYTHON_EXECUTABLE} -c "import sys; print(sys.executable)"
                OUTPUT_VARIABLE PYTHON_DEBUG_INFO
                OUTPUT_STRIP_TRAILING_WHITESPACE)
message(STATUS "Using Python from: ${PYTHON_DEBUG_INFO}")



add_executable(backtester ${SOURCES})

target_link_libraries(backtester PRIVATE ${Python3_LIBRARIES})
