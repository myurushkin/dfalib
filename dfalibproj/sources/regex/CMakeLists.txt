cmake_minimum_required(VERSION 2.6)

set(CMAKE_INCLUDE_CURRENT_DIR ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11 ")

set(HEADERS
        ../../include/regex/regex.h
        ../../include/regex/regexpattern.h
        ../../include/regex/regexstate.h)


set (SOURCES
        regex.cpp
	regexpattern.cpp
	regexstate.cpp)

include_directories(../../include/regex)
add_library(regex STATIC ${SOURCES} ${HEADERS})


