#!/bin/sh
# fetch-core.sh SLUG... -- download libretro cores for registry slugs into
# .cache/cores/<arch>/, from the libretro buildbot's nightly macOS builds.
# Prints the path of each core. A slug the map does not list is an error, unless a
# core built from source sits in .cache/cores/built/<arch>/<slug>_libretro.dylib.
set -eu
here=$(cd "$(dirname "$0")" && pwd)
cache="$here/../.cache/cores"
for slug in "$@"; do
  # A core built here from source (.cache/cores/built/<arch>/<slug>_libretro.dylib) comes first.
  for arch in arm64 x86_64; do
    lib="$cache/built/$arch/${slug}_libretro.dylib"
    if [ -f "$lib" ]; then echo "$lib"; continue 2; fi
  done
  line=$(awk -F'\t' -v s="$slug" '$1==s {print $2"\t"$3}' "$here/cores.tsv")
  if [ -z "$line" ]; then echo "no buildbot core for $slug" >&2; exit 1; fi
  name=$(printf '%s' "$line" | cut -f1); arch=$(printf '%s' "$line" | cut -f2)
  dir="$cache/$arch"; mkdir -p "$dir"
  lib="$dir/${name}_libretro.dylib"
  if [ ! -f "$lib" ]; then
    tmp=$(mktemp -d)
    curl -fsSL -o "$tmp/core.zip" "https://buildbot.libretro.com/nightly/apple/osx/$arch/latest/${name}_libretro.dylib.zip"
    unzip -q -o "$tmp/core.zip" -d "$tmp/x"
    mv "$tmp/x/${name}_libretro.dylib" "$lib"
    rm -rf "$tmp"
  fi
  echo "$lib"
done
