cmake_minimum_required(VERSION 2.8) 					
project(DNALangParser)				

set(SOURCE_LIB StringUtils.h  DNALangParser.h DNALangParser.cpp)
add_library(DNALangParser STATIC ${SOURCE_LIB})

