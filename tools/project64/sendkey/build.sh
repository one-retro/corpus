#!/bin/bash
# Builds sendkey.exe (Win32, no C runtime) with Homebrew's LLVM and lld; harness.js runs it from
# Project64's Scripts folder: copy sendkey.exe there.
set -e
cd "$(dirname "$0")"
L=/opt/homebrew/opt/llvm/bin
$L/llvm-dlltool -m i386 -d user32.def -l user32.lib -k
$L/llvm-dlltool -m i386 -d kernel32.def -l kernel32.lib -k
$L/clang --target=i686-pc-windows-msvc -O1 -ffreestanding -fno-stack-protector -c sendkey.c -o sendkey.obj
lld-link /entry:start /subsystem:console /nodefaultlib sendkey.obj user32.lib kernel32.lib /out:sendkey.exe
rm -f sendkey.obj user32.lib kernel32.lib
