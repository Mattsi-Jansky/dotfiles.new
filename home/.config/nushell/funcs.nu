# Cowsay with random cowfile
def randomsay [...args: string] {
    let cow = (cowsay -l | lines | skip 1 | split column " " | values | flatten | shuffle | first)
    $args | str join " " | cowsay -f $cow
}

# Docker cleanup
def drm [] { docker ps -a -q | lines | each {|| docker rm $in } }
def dri [] { docker images -q | lines | each {|| docker rmi $in } }
def drk [] { docker ps -q | lines | each {|| docker kill $in } }
def drv [] { docker volume prune -f }
