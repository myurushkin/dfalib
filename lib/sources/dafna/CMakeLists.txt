cmake_minimum_required(VERSION 2.9)
project(Dafna)

message("${CMAKE_BUILD_TYPE}")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS}  -std=c++11 -shared -fPIC")
set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -O3")

set (HEADERS
        ../../include/dafna/dafna.h)

set (SOURCES
        dafna.cpp)

include_directories(../../include/)
add_library(dafna SHARED ${SOURCES} ${HEADERS})
target_link_libraries(dafna dfalib regex)

install(TARGETS dafna DESTINATION lib)