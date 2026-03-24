#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$SCRIPT_DIR/bin"

OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)

case "$OS" in
    darwin)
        if [[ "$ARCH" == "arm64" ]]; then
            BINARY="cicd-client-darwin-arm64"
        else
            BINARY="cicd-client-darwin-amd64"
        fi
        ;;
    linux)
        BINARY="cicd-client-linux-amd64"
        ;;
    mingw*|msys*|cygwin*)
        BINARY="cicd-client-windows-amd64.exe"
        ;;
    *)
        echo "Unsupported OS: $OS" >&2
        exit 1
        ;;
esac

BINARY_PATH="$BIN_DIR/$BINARY"

if [[ ! -f "$BINARY_PATH" ]]; then
    echo "Error: Binary not found: $BINARY_PATH" >&2
    echo "Please run 'build.sh' first to compile the binary." >&2
    exit 1
fi

exec "$BINARY_PATH" "$@"
