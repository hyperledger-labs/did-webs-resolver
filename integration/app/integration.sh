#!/bin/bash

#
# Run this script from the base resolver directory, like
# did-webs-resolver% ./integration/app/integration.sh
#

#print commands
#set -x

#save this current directory, this is where the integration_clienting file also is
ORIG_CUR_DIR=$( pwd )

KERI_PRIMARY_STORAGE="/usr/local/var/keri"
KERI_FALLBACK_STORAGE="${HOME}/.keri"

KERI_DEV_BRANCH="development"
# KERI_DEV_TAG="c3a6fc455b5fac194aa9c264e48ea2c52328d4c5"

prompt="y"
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

function genDidWebs() {
    dkr did webs generate --name searcher --did did:webs:127.0.0.1:7676:EK5bvqO2RP8MRTJnE_PHzAsESDj2dHU5avT5I8tuuIzK --oobi http://127.0.0.1:5644/oobi/EK5bvqO2RP8MRTJnE_PHzAsESDj2dHU5avT5I8tuuIzK/witness
}

function getKeripyDir() {
    # Check if the environment variable is set
    if [ -z "$KERIPY_DIR" ]; then
        default_value="../keripy"
        # Prompt the user for input with a default value
        if [ "${prompt}" == "y" ]; then
            read -p "Set keripy dir [${default_value}]: " keriDirInput
        fi
        # Set the value to the user input or the default value
        KERIPY_DIR=${keriDirInput:-$default_value}
    fi
    # Use the value of the environment variable
    echo "$KERIPY_DIR"
}

function loadKeriData() {
    cd ${ORIG_CUR_DIR} || exit
    kloadPid=-1
    keriDir=$(getKeripyDir)
    echo "Keripy dir set to: ${keriDir}"
    if [ "${prompt}" == "y" ]; then
        read -p "Run load keri data (y/n)? [y]: " runKload
    fi
    runLoadKeriData=${runKload:-"n"}
    if [ "${runLoadKeriData}" == "n" ]; then
        echo "Skipping load KERI data"
    else
        echo "Running load KERI data"
        scriptsDir="${keriDir}/scripts"
        if [ -d "${scriptsDir}" ]; then
            echo "Found keri scripts dir"
            demoScriptsDir="${scriptsDir}/demo"
            if [ -d "${demoScriptsDir}" ]; then
                echo "Found keri demo scripts dir"
                cd ${demoScriptsDir} || exit
                source demo-script.sh
                source ./basic/query-for-anchor.sh
                echo "Completed loading KERI data"
            else
                echo "Couldn't find keri demo scripts dir"
            fi
        else
            echo "Couldn't find keri scripts dir"
        fi
    fi
    cd "${ORIG_CUR_DIR}" || exit
}

function runKeri() {
    cd ${ORIG_CUR_DIR} || exit
    witPid=-1
    keriDir=$(getKeripyDir)
    echo "Keripy dir set to: ${keriDir}"
    if [ "${prompt}" == "y" ]; then
        read -p "Run witness network (y/n)? [y]: " runWitNet
    fi
    runWit=${runWitNet:-"y"}
    if [ "${runWit}" == "y" ]; then
        if [ -d  "${keriDir}" ]; then
            #run a clean witness network
            echo "Launching a clean witness network"
            cd "${keriDir}" || exit
            updateFromGit ${KERI_DEV_BRANCH}
            installPythonUpdates "keri"
            rm -rf "${KERI_PRIMARY_STORAGE:?}/*";rm -Rf "${KERI_FALLBACK_STORAGE:?}/*";kli witness demo &
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

function updateFromGit() {
    branch=$1
    commit=$2

    if [ "${prompt}" == "y" ]; then
        read -p "Update git repo ${branch} ${commit}?, [n]: " upGitInput
    fi
    update=${upGitInput:-"n"}
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

runInt="test_salty"
while [ "${runInt}" != "n" ]
do
    intro

    echo "Setting up..."

    runKeri

    sleep 3

    loadKeriData

    sleep 3

    genDidWebs

    # runKeria

    # sleep 3

    # runSignifyIntegrationTests

    # sleep 3

    # runIssueEcr

    # sleep 3

    # runMultisig

    # echo ""

    if [ "${prompt}" == "y" ]; then
        read -p "Your servers still running, hit enter to tear down: " teardown
    fi
    
    echo "Tearing down any leftover processes"
    # #tear down the signify client
    # kill "$signifyPid" >/dev/null 2>&1
    # # tear down the keria cloud agent
    # kill $keriaPid >/dev/null 2>&1
    # # tear down the delegator
    # kill "$delPid" >/dev/null 2>&1
    # # tear down the vLEI server
    # kill $vleiPid >/dev/null 2>&1
    # tear down the witness network
    kill $witPid >/dev/null 2>&1

    read -p "Run again [n]?: " runAgain
    runInt=${runAgain:-"n"}
done

echo "Done"