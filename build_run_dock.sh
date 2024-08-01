#!/bin/bash
git pull

tag_name=$(cat src/VERSION.TXT)
dir_path=$(pwd)
log_folder="$dir_path/logging"
config_folder="$dir_path/config"
lower_path=$(dirname $dir_path)
graphs_folder="$lower_path/graphs"
docker_name="graphs-bot${tag_name}"

PS3='Build for (Ocean Server/Raspberry Server)?: '
server_options=("Ocean Server" "Raspberry Server")
select server in "${server_options[@]}"
do
    case $server in
        "Ocean Server")
            dockerfile="Dockerfile"
            image_name="python:3.11.0-slim-buster"
            break
            ;;
        "Raspberry Server")
            dockerfile="Dockerraspfile"
            image_name="python:3.11-slim-bookworm"
            break
            ;;
        *) echo "invalid option $REPLY";;
    esac
done



PS3='Build What?: '
# options=("dev" "acc" "prod" "Quit")
options=("acc" "prod" "Quit")
select opt in "${options[@]}"
do
    case $opt in
        "dev")
            echo "your choice is DEV"
            break
            ;;
        "acc")
            echo "your choice is ACC"
            break
            ;;
        "prod")
            echo "your choice is PROD"
            break
            ;;
        "Quit")
            break
            ;;
        *) echo "invalid option $REPLY";;
    esac
done

docker build -f "$dockerfile" -t "$docker_name" .

docker run -it -d --restart on-failure:30 --network="host" -v "$log_folder:/src/logging" -v "$config_folder:/src/config" -v "$graphs_folder:/src/graphs" -e "TZ=Europe/Amsterdam" --log-opt tag="$docker_name/$image_name" --name="$docker_name" "$docker_name"

docker ps -a
