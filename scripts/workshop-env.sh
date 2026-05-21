# Source before workshop curl/oc commands:  source scripts/workshop-env.sh
_workshop_no_proxy='127.0.0.1,::1,localhost,172.16.1.23,.redhatworkshops.io,.rhdp.net,cluster-wg2cd-2.dynamic2.redhatworkshops.io'
export NO_PROXY="${NO_PROXY:+$NO_PROXY,}${_workshop_no_proxy}"
export no_proxy="$NO_PROXY"
unset _workshop_no_proxy
