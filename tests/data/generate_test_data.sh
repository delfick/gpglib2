#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

do_mdc() {
    create "yes" "$@"
    create "no" "$@"
}

do_key() {
    do_mdc "rsa" "$@"
    do_mdc "dsa" "$@"
}

do_cipher() {
    do_key "cast5" "$@"
    do_key "aes" "$@"
    do_key "3des" "$@"
    do_key "blowfish" "$@"
}

do_compression() {
    do_cipher "zip" "$@"
    do_cipher "zlib" "$@"
    do_cipher "bzip2" "$@"
    do_cipher "none" "$@"
}

do_msg() {
    do_compression "small"
    do_compression "big"
}

create() {
    do_mdc=$1
    if [[ $do_mdc == "yes" ]]; then
        mdc="mdc"
        mdc_option=""
    else
        mdc="no_mdc"
        mdc_option="--disable-mdc"
    fi

    key=$2
    if [[ $key == "rsa" ]]; then
        name="Stephen"
    elif [[ $key == "dsa" ]]; then
        name="Bobby"
    else
        name="UNKNOWN"
    fi

    cipher=$3
    compression=$4
    msg=$5

    path=$DIR/encrypted/$mdc/$key/$cipher/$compression/$msg.gpg

    bn=$(dirname $path)
    if [[ ! -d $bn ]]; then
        mkdir -p $bn
    fi

    if [[ ! -e $path ]]; then
        echo "Generating $path"
        gpg -o $path --cipher-algo $cipher --compress-algo $compression --yes $mdc_option --homedir $DIR/gpg -r $name --encrypt $DIR/dump.$msg
    fi
}

do_msg
