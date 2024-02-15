#!/bin/bash

#
# Run this script from the base resolver directory, like
# did-webs-resolver% ./integration/app/integration.sh
#
# If there is an error you can search for running services (on mac) with
# sudo lsof -i -P -n | grep LISTEN | grep <port>

# print commands
# set -x

#save this current directory, this is where the integration_clienting file also is
ORIG_CUR_DIR=$( pwd )

controller="my-controller"
csalt="0AAQmsjh-C7kAJZQEzdrzwB7"
verifier="my-verifier"
vsalt="0ABPTOtI5Qy8dCYNSs3uoCHe"
host="127.0.0.1"
caid="ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe"
vaid="EKK9_Aau-htVcu8HyAZCIUkTFMqyVB6I2LCa_GhMYWm2"

KERI_BRANCH="main"
# KERI_TAG="c3a6fc455b5fac194aa9c264e48ea2c52328d4c5"

prompt="y"

function genDidWebs() {
    default_gen_webs="y"
    if [ "${prompt}" == "y" ]; then
        default_gen_webs="n"
        read -p "Generate did:webs in docker (y/n)? [${default_gen_webs}]: " runGenDid
    fi
    run_gen_webs=${runGenDid:-$default_gen_webs}
    if [ "${run_gen_webs}" == "n" ]; then
        echo "Skipping generate did:webs did document in docker"
    else
        echo "Generating did:webs DID Document and KERI event stream in docker"
        docker compose exec webs /bin/bash -c ./get_started_docker_gen.sh
    fi
}

function intro() {
    echo "Welcome to the docker test setup/run/teardown script"
    read -p "Enable prompts?, [y]: " enablePrompts
    prompt=${enablePrompts:-"y"}
    if [ "${prompt}" != "n" ]; then
        echo "Prompts enabled"
    else
        echo "Skipping prompts, using defaults"
    fi
}

function resolveDIDAndKeriEvents() {
    default_res_webs="y"
    if [ "${prompt}" == "y" ]; then
        default_res_webs="n"
        read -p "Resolve did:webs and keri events from docker (y/n)? [${default_res_webs}]: " res_webs_input
    fi
    res_webs=${res_webs_input:-$default_res_webs}
    if [ "${res_webs}" == "n" ]; then
        echo "Skipping resolving did:webs DID Document and Keri Events from docker"
    else
        echo "Resolving did:webs DID Document and Keri Events from docker"
        docker compose exec did-webs-resolver /bin/bash -c ./get_started_docker_resolve.sh
    fi
}

function serveDidAndKeriEvents() {
    default_serve_webs="y"
    if [ "${prompt}" == "y" ]; then
        default_serve_webs="n"
        read -p "Serve dids and keri events (y/n)? [${default_serve_webs}]: " serveKeriEvents
    fi
    serve_webs=${serveKeriEvents:-$default_serve_webs}
    if [ "${serve_webs}" == "n" ]; then
        echo "Skipping serving did:webs DID Document and Keri Events from docker"
    else
        echo "Serving did:webs and keri events from docker"
        docker compose exec did-webs-service /bin/bash -c './get_started_docker_serve.sh'
        echo "DID doc served at http://${host}:7676/${caid}/did.json"
        echo "KERI CESR at http://${host}:7676/${caid}/keri.cesr"
    fi
}

function startDocker() {
    echo "Setting up docker..."
    cd "${ORIG_CUR_DIR}/volume/dkr/examples/" || exit
    
    default_dock_build="n"
    if [ "${prompt}" == "y" ]; then
        read -p "Build docker containers before starting? [${default_dock_build}]: " upDockBuild
    fi
    run_dock_build=${upDockBuild:-$default_dock_build}

    if [ "${run_dock_build}" == "y" ]; then
        echo "Building docker images"
        docker compose build --no-cache
    else
        echo "Skipping docker build"
    fi

    echo "Running docker containers"
    docker compose down
    docker compose up -d

    echo "Docker containers running"
}

function stopDocker() {
    echo "Stopping docker..."
    cd "${ORIG_CUR_DIR}/volume/dkr/examples/" || exit

    echo "Stopping docker containers"
    docker compose down
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

    startDocker

    genDidWebs

    serveDidAndKeriEvents

    resolveDIDAndKeriEvents

    # runMultisig

    # echo ""

    # if [ "${prompt}" == "y" ]; then
    # fi
    read -p "Your docker containers are still running, hit enter to tear down: " teardown
   
    stopDocker

    default_run_again="n"
    if [ "${prompt}" == "y" ]; then
        read -p "Run again [${default_run_again}]?: " run_main_again
    fi
    run_main_loop=${run_main_again:-$default_run_again}
done

echo "Done"