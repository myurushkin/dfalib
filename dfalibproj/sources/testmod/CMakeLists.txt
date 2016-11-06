cmake_minimum_required(VERSION 2.8)

set(CMAKE_INCLUDE_CURRENT_DIR ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11 ")



set(HEADERS
        parserequest.h
        StringUtils.h
        DNALangParser.h)

set (SOURCES
	main.cpp
        parserequest.cpp
        DNALangParser.cpp)

include_directories(../../include/)
add_executable(testmod ${SOURCES} ${HEADERS})
target_link_libraries(testmod dfalib regex)

