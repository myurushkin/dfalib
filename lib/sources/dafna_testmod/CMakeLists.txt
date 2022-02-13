cmake_minimum_required(VERSION 2.8)

set(CMAKE_INCLUDE_CURRENT_DIR ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11 ")


set (SOURCES
	main.cpp)

include_directories(../../include/)
add_executable(dafna_testmod ${SOURCES})
target_link_libraries(dafna_testmod dafna)

