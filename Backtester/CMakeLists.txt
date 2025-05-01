project(Backtester)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

if (MSVC)
    add_compile_options("/utf-8")
endif()

include_directories(include)


file(GLOB SOURCES "src/*.cpp")

# Enable Python3 support
find_package(Python3 COMPONENTS Interpreter Development REQUIRED)

include_directories(${Python3_INCLUDE_DIRS})

add_compile_definitions(
    DATA_DOWNLOADER_PATH="${CMAKE_SOURCE_DIR}/DataDownloader"
)

add_executable(backtester ${SOURCES})

target_link_libraries(backtester PRIVATE ${Python3_LIBRARIES})
