#!/bin/bash

#
# Run this script from the base resolver directory, like
# did-webs-resolver% ./integration/app/integration.sh
#

#print commands
set -x

#save this current directory, this is where the integration_clienting file also is
ORIG_CUR_DIR=$( pwd )

CTRL_NAME="controller"

KERI_BRANCH="main"
# KERI_TAG="c3a6fc455b5fac194aa9c264e48ea2c52328d4c5"
KERI_PRIMARY_STORAGE="/usr/local/var/keri/"
KERI_FALLBACK_STORAGE="${HOME}/.keri/"
db_files=()
db_names=("$CTRL_NAME" wan wes wil wit wub wyz)
for db_name in "${db_names[@]}"; do
    path="${KERI_PRIMARY_STORAGE}*/${db_name}*"
    db_files+=( $path )
    path="${KERI_FALLBACK_STORAGE}*/${db_name}*"
    db_files+=( $path )
done

prompt="y"

function cleanKeri() {
    echo "Cleaning KERI data"
    #clean up any old KERI data
    default_clean_keri="y"
    if [ "${prompt}" == "y" ]; then
        read -p "Clean keri dbs ${db_files[*]} (y/n)? [${default_clean_keri}]: " cleanKeriInput
    fi
    clean_keri_data=${cleanKeriInput:-$default_clean_keri}
    if [ "${clean_keri_data}" == "n" ]; then
        echo "Skipping clean KERI data"
    else
        echo "Running clean KERI data"
        for db_file in "${db_files[@]}"; do rm -R "$db_file";done
        echo "Cleaned KERI data"
    fi
}

function genDidWebs() {
    default_gen_webs="y"
    if [ "${prompt}" == "y" ]; then
        default_gen_webs="n"
        read -p "Generate did:webs (y/n)? [${default_gen_webs}]: " runGenDid
    fi
    run_gen_webs=${runGenDid:-$default_gen_webs}
    if [ "${run_gen_webs}" == "n" ]; then
        echo "Skipping generate did:webs did document"
    else
        echo "Generating did:webs DID Document and KERI event stream"
        start_webs="${ORIG_CUR_DIR}/volume/dkr/examples/get_started_webs.sh"
        if [ -f "${start_webs}" ]; then
            echo "Found get started script to generate did:webs"
            source "${start_webs}" "${CTRL_NAME}" "labs.hyperledger.org:did-webs-resolver:pages" "EKYGGh-FtAphGmSZbsuBs_t4qpsjYJ2ZqvMKluq9OxmP"
            sleep 3
            echo "Completed loading generating did:webs"
        else
            echo "Couldn't find get started did:webs script"
        fi
    fi
}

function getKeripyDir() {
    # Check if the environment variable is set
    if [ -z "$KERIPY_DIR" ]; then
        # Prompt the user for input with a default value
        default_keri_dir="../keripy"
        if [ "${prompt}" == "y" ]; then
            read -p "Set keripy dir [${default_keri_dir}]: " keriDirInput
        fi
        # Set the value to the user input or the default value
        KERIPY_DIR=${keriDirInput:-$default_keri_dir}
    fi
    # Use the value of the environment variable
    echo "$KERIPY_DIR"
}

function installPythonUpdates() {
    name=$1
    if [ "${prompt}" == "y" ]; then
        read -p "Install $name?, [n]: " installInput
    fi
    install=${installInput:-"n"}
    if [ "${install}" == "n" ]; then
        echo "Skipping install of $name"
    else
        echo "Installing python module updates..."
        python -m pip install -e .
    fi
}

function intro() {
    echo "Welcome to the integration test setup/run/teardown script"
    read -p "Enable prompts?, [y]: " enablePrompts
    prompt=${enablePrompts:-"y"}
    if [ "${prompt}" != "n" ]; then
        echo "Prompts enabled"
    else
        echo "Skipping prompts, using defaults"
    fi
}

function createKeriId() {
    cd ${ORIG_CUR_DIR} || exit
    kloadPid=-1
    default_kload="y"
    if [ "${prompt}" == "y" ]; then
        default_kload="n"
        read -p "Run create keri id (y/n)? [${default_kload}]: " run_kload_input
    fi
    create_keri_id=${run_kload_input:-$default_kload}
    if [ "${create_keri_id}" == "n" ]; then
        echo "Skipping load KERI data"
    else
        echo "Running load KERI data"
        create_aid_script="${ORIG_CUR_DIR}/volume/dkr/examples/get_started_create_id.sh"
        if [ -f "${create_aid_script}" ]; then
            echo "Found get started keri script"
            source "${create_aid_script}" "${CTRL_NAME}" "${ORIG_CUR_DIR}/volume/dkr/examples/my-scripts" "config-local" "incept-wits.json"
            sleep 3
            echo "Completed creating KERI identity"
        else
            echo "Couldn't find get started keri script"
        fi
    fi
    cd "${ORIG_CUR_DIR}" || exit
    echo ""
}

function resolveDIDAndKeriEvents() {
    default_res_webs="y"
    if [ "${prompt}" == "y" ]; then
        default_res_webs="n"
        read -p "Resolve did:webs and keri events (y/n)? [${default_res_webs}]: " res_webs_input
    fi
    res_webs=${res_webs_input:-$default_res_webs}
    if [ "${res_webs}" == "n" ]; then
        echo "Skipping resolving did:webs DID Document and Keri Events"
    else
        echo "Resolving did:webs DID Document and Keri Events"
        res_webs_script="${ORIG_CUR_DIR}/volume/dkr/examples/get_started_webs_resolve.sh"
        if [ -f "${res_webs_script}" ]; then
            echo "Found get started keri script"
            source "${res_webs_script}" "${CTRL_NAME}" "${ORIG_CUR_DIR}/volume/dkr/examples/my-scripts" "config-local"
            sleep 3
            echo "Completed creating KERI identity"
        else
            echo "Couldn't find get started keri script"
        fi
        dkr did webs resolve --name wan --did did:webs:127.0.0.1%3a7676:BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha
        sleep 3
    fi
}

function runKeri() {
    cd ${ORIG_CUR_DIR} || exit
    witPid=-1
    keriDir=$(getKeripyDir)
    echo "Keripy dir set to: ${keriDir}"

    default_wit="y"
    if [ "${prompt}" == "y" ]; then
        default_wit="n"
        read -p "Run witness network (y/n)? [${default_wit}]: " runWitNet
    fi
    runWit=${runWitNet:-$default_wit}
    if [ "${runWit}" == "y" ]; then
        if [ -d  "${keriDir}" ]; then
            #run a clean witness network
            echo "Launching a clean witness network"
            cd "${keriDir}" || exit
            updateFromGit ${KERI_BRANCH}
            installPythonUpdates "keri"
            kli witness demo &
            witPid=$!
            sleep 5
            echo "Clean witness network launched"
        else
            echo "KERIPY dir missing ${keriDir}"
            exit 1
        fi
    else
        echo "Skipping witness network"
    fi
    echo ""
}

function serveDidAndKeriEvents() {
    default_serve_webs="y"
    if [ "${prompt}" == "y" ]; then
        default_serve_webs="n"
        read -p "Serve dids and keri events (y/n)? [${default_serve_webs}]: " serveKeriEvents
    fi
    serve_webs=${serveKeriEvents:-$default_serve_webs}
    if [ "${serve_webs}" == "n" ]; then
        echo "Skipping serving did:webs DID Document and Keri Events"
    else
        srv_webs_script="${ORIG_CUR_DIR}/volume/dkr/examples/get_started_webs_resolve.sh"
        if [ -f "${srv_webs_script}" ]; then
            echo "Found get started serve script"
            source "${srv_webs_script}" "${CTRL_NAME}" "${ORIG_CUR_DIR}/volume/dkr/examples/my-scripts" "config-local"
        servePid=$!
        sleep 3
        echo "Serving did:webs and keri events"
        else
            echo "Couldn't find get started serve script"
        fi
    fi
}

function updateFromGit() {
    branch=$1
    commit=$2
    default_up_git="n"
    if [ "${prompt}" == "y" ]; then
        read -p "Update git repo ${branch} ${commit}?, [${default_up_git}]: " upGitInput
    fi
    update=${upGitInput:-$default_up_git}
    if [ "${update}" == "y" ]; then
        echo "Updating git branch ${branch} ${commit}"
        fetch=$(git fetch)
        echo "git fetch status ${fetch}"
        if [ -z "${commit}" ]; then
            switch=$(git switch "${branch}")
            echo "git switch status ${switch}"
            pull=$(git pull)
            echo "git pull status ${pull}"
        else
            switch=$(git checkout "${commit}")
            echo "git checkout commit status ${switch}"
        fi
    else
        echo "Skipping git update ${branch}"
    fi
}

run_main_loop="y"
while [ "${run_main_loop}" != "n" ]
do
    intro

    echo "Setting up..."

    cleanKeri

    runKeri

    createKeriId

    genDidWebs

    serveDidAndKeriEvents

    resolveDIDAndKeriEvents

    # runMultisig

    # echo ""

    # if [ "${prompt}" == "y" ]; then
    # fi
    read -p "Your servers still running, hit enter to tear down: " teardown
    echo "Tearing down any leftover processes"
    # #tear down the signify client
    # kill "$signifyPid" >/dev/null 2>&1
    # # tear down the keria cloud agent
    # kill $keriaPid >/dev/null 2>&1
    # tear down the delegator
    kill "$servePid" >/dev/null 2>&1
    # tear down the vLEI server
    kill $kloadPid >/dev/null 2>&1
    # tear down the witness network
    kill $witPid >/dev/null 2>&1

    default_run_again="n"
    if [ "${prompt}" == "y" ]; then
        read -p "Run again [${default_run_again}]?: " run_main_again
    fi
    run_main_loop=${run_main_again:-$default_run_again}
done

echo "Done"