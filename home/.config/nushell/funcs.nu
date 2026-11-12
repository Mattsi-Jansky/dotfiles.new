# Cowsay with random cowfile
def randomsay []: string -> string {
    let input = $in
    let cow = (cowsay -l | lines | skip 1 | split column " " | values | flatten | shuffle | first)
    $input | cowsay -f $cow
}

# cat: render images with chafa (Ghostty's kitty graphics protocol), everything
# else with bat. Images only go to chafa when every file named is an image, so
# mixed or ambiguous calls fall back to bat. Flags pass through to whichever runs.
def --wrapped cat [...args: string] {
    let input = $in
    let image_extensions = [png jpg jpeg gif webp tif tiff svg avif qoi]
    # Files named on the command line, skipping flags and flag values like "40x20"
    let files = $args | where {|a| not ($a | str starts-with "-") and ($a | path exists) }
    let all_images = ($files | is-not-empty) and ($files | all {|f|
        ($f | path parse | get extension | str lowercase) in $image_extensions
    })
    if $all_images {
        ^chafa ...$args
    } else if $input == null {
        ^batcat ...$args
    } else {
        $input | ^batcat ...$args
    }
}

# Docker cleanup
def drm [] { docker ps -a -q | lines | each {|| docker rm $in } }
def dri [] { docker images -q | lines | each {|| docker rmi $in } }
def drk [] { docker ps -q | lines | each {|| docker kill $in } }
def drv [] { docker volume prune -f }
