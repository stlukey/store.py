#!/usr/bin/env bash
# Directory of file
readonly DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

OPTIND=1
production=0

set_env_vars() {
    if [ $production -eq 0 ]; then
        echo "Development Mode"
        source $DIR/configs/development
    else
        echo "Production Mode"
        source $DIR/configs/production
    fi
}

check_virtualenv() {
    if [ $(python -c'print(int(hasattr(__import__("sys"), "real_prefix")))') -eq 0 ]; then
        source $DIR/.env/bin/activate
    fi
}

is_mongodb_up() {
    return $(mongo --eval "db.stats()" >/dev/null)
}



launch_mongodb() {
    is_mongodb_up && echo "Mongodb running." && return

    echo "MongoDB not running! Launching now...."
    sudo su <<END
    nohup mongod >/dev/null 2>&1 &
    disown
END
    sleep 5
    is_mongodb_up && echo "Mongodb running." && return


    echo "Error launching mongodb."
    exit 1
}

main() {
    cd $DIR

    check_virtualenv
    set_env_vars
    [ $production -eq 0 ] && launch_mongodb

    target='api'
    [[ $@ != '' ]] && target="$target.scripts.$@"
    python -m $target

}


while getopts "p" opt; do
    case "$opt" in
    p)  production=1
    esac
done
shift $((OPTIND-1))

main "$@"

