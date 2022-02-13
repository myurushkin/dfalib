cmake_minimum_required(VERSION 2.9)

set(CMAKE_INCLUDE_CURRENT_DIR ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS}  -std=c++11   -std=c++11 -shared -fPIC")
IF(CMAKE_BUILD_TYPE MATCHES RELEASE)
    message("release mode")
ENDIF(CMAKE_BUILD_TYPE MATCHES RELEASE)


set(HEADERS
        ../../include/dfalib/dfa.h)


set (SOURCES
        dfa.cpp)

include_directories(../../include/)
add_library(dfalib STATIC ${SOURCES} ${HEADERS})


