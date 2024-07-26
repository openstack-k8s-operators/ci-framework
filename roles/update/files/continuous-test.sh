#!/bin/bash
set -eu
## ---------------------------------------------------------------------
## NAME:
##    continuous-test.sh - run a script in a loop and gather the results.
##
## SYNOPSIS
##    continuous-test.sh [OPTION] [SCRIPT]
##
## DESCRIPTION
##   Run SCRIPT and collect date, time and exit status.
##
##   The SCRIPT will be continuously run until we get a SIGUSR1
##   signal. When the signal is caught, we will wait for the last
##   run to end and dump to stdout the result of all commands.
##
##   The output of the each command will be saved into "continuous-test-<pid>/" under
##   the current directory.
##
##   A /var/run/continuous-test.pid will register the pid of the
##   running process.
##
## OPTIONS
##   -d Enable debug mode.
##   -l <PREFIX> Prefix used for:
##        - Logfile: Default to  ./continuous-test-<PID>.log
##        - Done file: Default to ./continuous-test-<PID>.done
##
##      The logfile will hold the result of each command run and the
##      done file indicate that the last run is finished when we want
##      to end the continuous test.
##
##      Both those files will have the <PID> added to the prefix so that
##      multiple command can be run in parallel if needed.
##
##      The pid can be find in the PIDFILE.
##
##   -p <PIDFILE> save the PID to that file.
##        Default to ./continuous-test.pid
##
##   -o <DIR> Directory where to save all those files. Default to
##        the directory where continuous-test.sh is.
##
## FILES
##
##   /var/run/continuous-test.pid will hold the pid of the process
##   ./continuous-test.log have the result of the check
##   ./continuous-test-<pid>/<files> will hold the output of each command.
##
## ENVIRONMENT
##   CT_SCRIPT_ARGS  A string holding any argument that should
##   be passed to SCRIPT.
##
## AUTHOR
##   Athlan-Guyot Sofer <sathlang@redhat.com>
## ---------------------------------------------------------------------
FILE=$(basename $0)

CT_PARENT=${CT_PARENT:-true}
CT_CHILD=${CT_CHILD:-false}

CT_STOP=false

## ---------------------------------------------------------------------
## Function definitions.
process_sig() {
    echo "$$: received term signal" >&2
    CT_STOP=true
}

process_sigterm_parent() {
    echo "$$: Parent received term signal" >&2
    if [ -n "${CT_PID}" ]; then
        echo "$$: received term signal: killing $CT_PID" >&2
        kill -s USR1 $CT_PID
    else
        # Should not happen.
        echo "$$: received term signal: killing group" >&2
        kill -s USR1 0
    fi
}

# Daemonize the process. This will fork a process and detach from the
# console after setting the environment from the options.
if "${CT_PARENT}"; then
    export DEBUG=false
    while getopts :p:l:o:d OPT; do
        case $OPT in
            l|+l)
                CT_PREFIX="$OPTARG"
                ;;
            p|+p)
                CT_PIDFILE="$OPTARG"
                ;;
            o|+o)
                CT_DIR="$OPTARG"
                ;;
            d|+d)
                DEBUG=true
                ;;
            *)
                echo "usage: ${0##*/} [-l LOGFILE] [-p PIDFILE] [-d] SCRIPT"
                exit 2
        esac
    done
    shift $(( OPTIND - 1 ))
    OPTIND=1
    if [ -z "${CT_DIR}" ]; then
        CT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    fi
    export CT_DIR
    if $DEBUG; then
        export CT_TTY=$(tty)
    else
        export CT_TTY=/dev/null
    fi
    exec 2>$CT_TTY
    echo "entering parent $$ $FILE" >&2
    export CT_SCRIPT_ARGS=${CT_SCRIPT_ARGS:-""}
    export CT_SCRIPT="${@:?'SCRIPT cannot be empty.'}"
    export CT_PREFIX="${CT_PREFIX:-}"
    export CT_PIDFILE="${CT_PIDFILE:-}"
    export CT_CHILD=true
    export CT_PARENT=false
    setsid ${CT_DIR}/${FILE} "$@" </dev/null >$CT_TTY 2>$CT_TTY &
    CT_PID=$!
    if $DEBUG ; then
        trap process_sigterm_parent SIGTERM SIGINT
        wait $CT_PID
        echo "leaving parent $$ after waiting for $CT_PID/$FILE" >&2
    else
        echo "leaving parent $$ $FILE" >&2
    fi
    sync
    exit 0
fi

if "${CT_CHILD}"; then
    if [ -n "${CT_TTY}" ]; then
        exec 2> ${CT_TTY}
        exec 1> ${CT_TTY}
    else
        CT_TTY=/dev/null
    fi
    echo "entering child $$ running $FILE" >&2
    if [ -z "${CT_PREFIX}" ]; then
        CT_LOGFILE="${CT_DIR}/continuous-test-$$.log"
    else
        CT_LOGFILE="${CT_DIR}/${CT_PREFIX}-$$.log"
    fi
    if [ -z "${CT_PIDFILE}" ]; then
        CT_PIDFILE="${CT_DIR}/continuous-test.pid"
    fi
    export CT_LOGFILE
    export CT_PIDFILE
    export CT_CMD_OUT_DIR="${CT_DIR}/ct-$$"
    trap process_sig SIGTERM SIGUSR1
    export CT_CHILD=false
    export CT_PARENT=false
    echo $$ > "${CT_PIDFILE}"
    # Main loop where eventually run the script.
    while ! $CT_STOP; do
        setsid ${CT_DIR}/$FILE "$@" </dev/null 2>$CT_TTY
    done
    echo "Leaving child $$ running $FILE" >&2
    if [ -z "${CT_PREFIX}" ]; then
        CT_ENDFILE="${CT_DIR}/continuous-test-$$.done"
    else
        CT_ENDFILE="${CT_DIR}/${CT_PREFIX}-$$.done"
    fi
    date > $CT_ENDFILE
    sync
    exit 0
fi

exec >>$CT_LOGFILE
mkdir -p "${CT_CMD_OUT_DIR}"
echo "entering loop $$ $CT_SCRIPT" >&2
# We cannot have to jobs in the same seconds, or else we will
# overwrite the file. sleep 1 prevents this.
sleep 1
start_time="$(date +%s)"
start_time_h="$(date -d@${start_time})"
echo -n "${start_time_h} (${start_time}) "
set +e
"${CT_SCRIPT}" ${CT_SCRIPT_ARGS} &>> "${CT_CMD_OUT_DIR}/${start_time}.log"
RC="${?}"
set -e
end_time="$(date +%s)"
duration=$((end_time - start_time))
echo -n "${duration}s "

if [ $RC -eq 0 ]; then
    echo "SUCCESS (0)"
else
    echo "FAILED (${RC})"
fi
echo "leaving loop $$" >&2
