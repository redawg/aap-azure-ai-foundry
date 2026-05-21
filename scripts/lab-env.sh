# Lab AAP at 172.16.1.23 — source before curl/MCP/API calls:
#   source scripts/lab-env.sh
#
# Override password:  export AAP_PASSWORD='your-password'

_lab_no_proxy='172.16.1.23,127.0.0.1,::1,localhost'
export NO_PROXY="${NO_PROXY:+$NO_PROXY,}${_lab_no_proxy}"
export no_proxy="$NO_PROXY"
unset _lab_no_proxy

export AAP_BASE="${AAP_BASE:-https://172.16.1.23}"
export AAP_USER="${AAP_USER:-admin}"
: "${AAP_PASSWORD:?Set AAP_PASSWORD before sourcing lab-env.sh}"
export MCP_BASE="${MCP_BASE:-$AAP_BASE}"

# Base64(admin:password) for MCP HTTP headers (no "Basic " prefix)
export AAP_BASIC_AUTH="${AAP_BASIC_AUTH:-$(printf '%s' "${AAP_USER}:${AAP_PASSWORD}" | base64 -w0 2>/dev/null || printf '%s' "${AAP_USER}:${AAP_PASSWORD}" | base64)}"
