ln -s "to-here" <- "from-here"

find /volume1/Pictures -not -path '*/@eaDir/*' -type f -name "*.jpg"

filenames="*.jpg"
for i in ./*/; do
    ln -s /var/services/web/node/slideshow/public/img/ $i$filenames
done